import json
from flask import jsonify, request
from flask_cors import cross_origin
from loguru import logger
from simple_websocket import Server, ConnectionClosed
from supabase import Client as SupabaseClient
from datetime import datetime

from yourapp.chat.payload import Payload
from yourapp.chat.payloads import PayloadOpenChat, payload_from_dict
from yourapp.core.system_states.registry import system_state_from_dict
from yourapp.core.system_states.start_state import new_start_state
from yourapp.core.system_states.util_states import NULL_STATE
from yourapp.sessions import (
    add_session,
    delete_session,
    get_session,
    update_states,
    open_session,
    close_session,
    duplicate_session,
)
from yourapp.sessions.messages import Message, add_multiple_messages, get_messages
from yourapp.user import get_user_infos


def init_chat_routes(app, login_required, admin_client: SupabaseClient):
    @app.route("/chat/<session_id>", websocket=True)
    @cross_origin()
    @login_required
    def chat(session_id: str, user_id=None):
        logger.info(f"user {user_id} session {session_id} chat requested")

        session_id = int(session_id)
        ws = Server.accept(request.environ)
        ws.send(
            json.dumps(
                Message(
                    id=None,
                    created_at=datetime.now(),
                    payload={"type": "connected"},
                    is_system=True,
                ).to_dict()
            )
        )

        logger.info(f"user {user_id} session {session_id} websocket connected")

        user = get_user_infos(admin_client, user_id)

        if user is None:
            logger.critical(
                f"user {user_id} session {session_id} user not found inconsistency"
            )
            return jsonify({"error": "User not found"}), 404

        system_state = new_start_state()
        user_state = {}

        if session_id == -1:
            logger.info(f"user {user_id} creating new session")

            result = add_session(
                admin_client, user_id, system_state.to_dict(), user_state
            )
            if result is None:
                logger.error(f"user {user_id} failed to create new session")
                return jsonify({"error": "Session creation failed"}), 500

            session_id = result

            logger.info(f"user {user_id} session {session_id} created")

            ws.send(
                json.dumps(
                    Message(
                        id=None,
                        created_at=datetime.now(),
                        payload={"type": "session_created", "id": session_id},
                        is_system=True,
                    ).to_dict()
                )
            )

        session = get_session(admin_client, session_id)
        if session is None:
            logger.error(f"user {user_id} session {session_id} not found")
            return jsonify({"error": "Session not found"}), 404
        if session.owner_id != user_id:
            logger.warning(
                f"user {user_id} requested user {session.owner_id}'s session {session_id}"
            )
            return jsonify({"error": "Unauthorized"}), 401
        if session.is_open:
            logger.info(
                f"user {user_id} session {session_id} already open, attempting duplication"
            )
            result = duplicate_session(admin_client, session_id)
            if result is None:
                logger.error(f"user {user_id} session {session_id} failed to duplicate")
                return jsonify({"error": "Session duplication failed"}), 500
            logger.info(f"user {user_id} session {session_id} duplicated to {result}")
            session_id = result

        result = open_session(admin_client, session_id)
        if result is None:
            logger.error(f"user {user_id} session {session_id} failed to open")
            return jsonify({"error": "Failed to open session"}), 500

        logger.info(f"user {user_id} session {session_id} opened")

        system_state = system_state_from_dict(session.system_state)
        user_state = session.user_state

        history = get_messages(admin_client, session_id)
        if history is None:
            logger.error(f"user {user_id} session {session_id} failed to get history")
            return jsonify({"error": "Failed to get session messages"}), 500

        try:
            for message in history[:-1]:
                ws.send(json.dumps(message.to_dict()))

            if len(history) > 0:
                last_message = history[-1]
                ws.send(json.dumps(last_message.to_dict()))
                logger.info(f"user {user_id} session {session_id} sent entire history")

                payload = payload_from_dict(last_message.payload)
                is_system = last_message.is_system
                requires_user_input = payload.requires_user_input()
                if is_system and requires_user_input:
                    data = ws.receive()
                    input_payload = json.loads(data)
                    received_messages = add_multiple_messages(
                        admin_client, session_id, [input_payload], False
                    )
                    if received_messages is None:
                        logger.error(
                            f"user {user_id} session {session_id} failed to persist user message"
                        )
                        return jsonify({"error": "Failed to persist user message"}), 500
                    for received_message in received_messages:
                        ws.send(json.dumps(received_message.to_dict()))
                        history += [received_message]

            logger.info(f"user {user_id} session {session_id} starting chat loop")

            def send_payload(payload):
                ws.send(
                    json.dumps(
                        {
                            "payload": payload.to_dict(),
                            "id": -1,
                            "created_at": datetime.now().isoformat(),
                            "is_system": True,
                        }
                    )
                )

            def expect_payload() -> Payload:
                send_payload(PayloadOpenChat())
                data = ws.receive()
                payload_dict = json.loads(data)
                message_sendback = json.dumps(
                    {
                        "payload": payload_dict,
                        "id": -1,
                        "created_at": datetime.now().isoformat(),
                        "is_system": False,
                    }
                )
                ws.send(message_sendback)
                return payload_from_dict(payload_dict)

            while system_state != NULL_STATE:
                system_state, payloads = system_state.execute(
                    user, history, send_payload, expect_payload
                )

                result = update_states(
                    admin_client, session_id, system_state.to_dict(), user_state
                )
                if result is None:
                    logger.error(
                        f"user {user_id} session {session_id} failed to persist updated session states"
                    )
                    return (
                        jsonify({"error": "Failed to persist updated session states"}),
                        500,
                    )

                payloads_dicts = [payload.to_dict() for payload in payloads]
                messages = add_multiple_messages(
                    admin_client, session_id, payloads_dicts, True
                )
                if messages is None:
                    logger.error(
                        f"user {user_id} session {session_id} failed to persist system messages"
                    )
                    return jsonify({"error": "Failed to persist system messages"}), 500

                for message in messages:
                    ws.send(json.dumps(message.to_dict()))
                    history += [message]
                    payload = payload_from_dict(message.payload)
                    if payload.requires_user_input():
                        data = ws.receive()
                        input_payload = json.loads(data)
                        received_messages = add_multiple_messages(
                            admin_client, session_id, [input_payload], False
                        )
                        if received_messages is None:
                            logger.error(
                                f"user {user_id} session {session_id} failed to persist user message"
                            )
                            return (
                                jsonify({"error": "Failed to persist user message"}),
                                500,
                            )
                        for received_message in received_messages:
                            ws.send(json.dumps(received_message.to_dict()))
                            history += [received_message]

        except ConnectionClosed:
            logger.info(f"user {user_id} session {session_id} closed websocket")
        except Exception as e:
            logger.error(
                f"user {user_id} session {session_id} exception raised in chat"
            )
            logger.exception(e)

        all_history_message_are_system = all([message.is_system for message in history])
        if all_history_message_are_system:
            logger.info(
                f"user {user_id} session {session_id} all messages from system, deleting"
            )
            result = delete_session(admin_client, session_id)
            if result is None:
                logger.error(
                    f"user {user_id} session {session_id} failed to delete session"
                )
                return jsonify({"error": "Failed to delete session"}), 500
        else:
            logger.info(f"user {user_id} session {session_id} closing session")
            result = close_session(admin_client, session_id)
            if result is None:
                logger.error(
                    f"user {user_id} session {session_id} failed to close session"
                )
                return jsonify({"error": "Failed to close session"}), 500
        return "end"
