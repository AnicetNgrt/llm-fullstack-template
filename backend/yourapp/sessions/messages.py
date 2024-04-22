from dataclasses import dataclass
import json
from typing import Optional
from loguru import logger
from supabase import Client as SupabaseClient
from datetime import datetime


@dataclass
class Message:
    id: int
    payload: dict
    created_at: datetime
    is_system: bool

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "payload": self.payload,
            "created_at": self.created_at.isoformat(),
            "is_system": self.is_system,
        }


def add_message(
    client: SupabaseClient, session_id: int, payload: dict, is_system: bool
) -> Optional[Message]:
    try:
        logger.trace(
            f"DB adding {'system' if is_system else 'user'} message to session {session_id}"
        )
        result = (
            client.table("sessions messages")
            .insert(
                {
                    "session_id": session_id,
                    "payload_json": json.dumps(payload),
                    "is_system": is_system,
                }
            )
            .execute()
        )
        if len(result.data) == 0:
            logger.trace(f"DB no message added to session {session_id}")
            return None

        logger.trace(
            f"DB {'system' if is_system else 'user'} message added to session {session_id}"
        )
        return Message(
            id=result.data[0]["id"],
            payload=json.loads(result.data[0]["payload_json"]),
            created_at=datetime.fromisoformat(result.data[0]["created_at"]),
            is_system=result.data[0]["is_system"],
        )
    except Exception as e:
        logger.error(
            f"DB error adding {'system' if is_system else 'user'} message to session {session_id}"
        )
        logger.exception(e)
        return None


def add_multiple_messages(
    client: SupabaseClient, session_id: int, payloads: list[dict], is_system: bool
) -> Optional[list[Message]]:
    try:
        logger.trace(
            f"DB adding {len(payloads)} {'system' if is_system else 'user'} messages to session {session_id}"
        )
        result = (
            client.table("sessions messages")
            .insert(
                [
                    {
                        "session_id": session_id,
                        "payload_json": json.dumps(payload),
                        "is_system": is_system,
                    }
                    for payload in payloads
                ]
            )
            .execute()
        )
        if len(result.data) == 0:
            logger.error(
                f"DB no {'system' if is_system else 'user'} messages added to session {session_id}"
            )
            return None

        messages = []
        for message in result.data:
            messages.append(
                Message(
                    id=message["id"],
                    payload=json.loads(message["payload_json"]),
                    created_at=datetime.fromisoformat(message["created_at"]),
                    is_system=message["is_system"],
                )
            )

        logger.trace(
            f"DB {'system' if is_system else 'user'} messages added to session {session_id}"
        )
        return messages

    except Exception as e:
        logger.error(
            f"DB error adding {'system' if is_system else 'user'} messages to session {session_id}"
        )
        logger.exception(e)
        return None


def duplicate_all_session_messages_and_assign_to_new_session(
    client: SupabaseClient, old_session_id: int, new_session_id: int
) -> Optional[list[Message]]:
    try:
        logger.trace(
            f"DB duplicating all messages from session {old_session_id} to session {new_session_id}"
        )
        result = (
            client.table("sessions messages")
            .select("*")
            .eq("session_id", old_session_id)
            .execute()
        )
        if len(result.data) == 0:
            logger.trace(f"DB no messages found in session {old_session_id}")
            return []

        logger.trace(
            f"DB {len(result.data)} messages found in session {old_session_id}"
        )

        messages = []
        for message in result.data:
            messages.append(
                Message(
                    id=message["id"],
                    payload=json.loads(message["payload_json"]),
                    created_at=datetime.fromisoformat(message["created_at"]),
                    is_system=message["is_system"],
                )
            )

        result = (
            client.table("sessions messages")
            .insert(
                [
                    {
                        "session_id": new_session_id,
                        "payload_json": json.dumps(message.payload),
                        "is_system": message.is_system,
                    }
                    for message in messages
                ]
            )
            .execute()
        )
        if len(result.data) == 0:
            logger.error(f"DB no messages added to session {new_session_id}")
            return None

        logger.trace(
            f"DB {len(result.data)} messages added to session {new_session_id}"
        )

        messages = []
        for message in result.data:
            messages.append(
                Message(
                    id=message["id"],
                    payload=json.loads(message["payload_json"]),
                    created_at=datetime.fromisoformat(message["created_at"]),
                    is_system=message["is_system"],
                )
            )

        return messages

    except Exception as e:
        logger.error(
            f"DB error duplicating all messages from session {old_session_id} to session {new_session_id}"
        )
        logger.exception(e)
        return None


def get_messages(client: SupabaseClient, session_id: int) -> Optional[list[Message]]:
    try:
        logger.trace(f"DB getting messages from session {session_id}")
        result = (
            client.table("sessions messages")
            .select("*")
            .eq("session_id", session_id)
            .order("id")
            .execute()
        )
        if len(result.data) == 0:
            logger.trace(f"DB no messages found in session {session_id}")
            return []

        messages = []
        for message in result.data:
            messages.append(
                Message(
                    id=message["id"],
                    payload=json.loads(message["payload_json"]),
                    created_at=datetime.fromisoformat(message["created_at"]),
                    is_system=message["is_system"],
                )
            )

        logger.trace(f"DB {len(messages)} messages found in session {session_id}")

        return messages
    except Exception as e:
        logger.error(f"DB error getting messages from session {session_id}")
        logger.exception(e)
        return None
