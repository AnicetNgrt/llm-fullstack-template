from dataclasses import dataclass
import json
from typing import Optional
from loguru import logger
from supabase import Client as SupabaseClient
from datetime import datetime, UTC

from yourapp.sessions.messages import (
    duplicate_all_session_messages_and_assign_to_new_session,
)
from yourapp.utils.generate_name import generate_randome_tripartite_name


@dataclass
class Session:
    id: int
    owner_id: str
    title: str
    created_at: datetime
    last_activity_at: datetime
    system_state: dict
    user_state: dict
    is_open: bool

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "last_activity_at": self.last_activity_at.isoformat(),
            "system_state": self.system_state,
            "user_state": self.user_state,
            "is_open": self.is_open,
        }


def get_sessions(client: SupabaseClient, user_id: str) -> Optional[list[Session]]:
    try:
        logger.trace(f"DB getting sessions for user {user_id}")
        result = (
            client.table("sessions")
            .select("*")
            .eq("owner_id", user_id)
            .order("last_activity_at", desc=True)
            .execute()
        )
        if len(result.data) == 0:
            logger.trace(f"DB no sessions found for user {user_id}")
            return []

        sessions = []
        for session in result.data:
            sessions.append(
                Session(
                    id=session["id"],
                    title=session["title"],
                    created_at=datetime.fromisoformat(session["created_at"]),
                    last_activity_at=datetime.fromisoformat(
                        session["last_activity_at"]
                    ),
                    system_state=json.loads(session["system_state_json"]),
                    user_state=json.loads(session["user_state_json"]),
                    owner_id=session["owner_id"],
                    is_open=session["is_open"],
                )
            )

        logger.trace(f"DB {len(sessions)} sessions found for user {user_id}")
        return sessions
    except Exception as e:
        logger.error(f"DB error getting sessions for user {user_id}")
        logger.exception(e)
        return None


def get_session(client: SupabaseClient, session_id: int) -> Optional[Session]:
    try:
        logger.trace(f"DB getting session {session_id}")
        result = (
            client.table("sessions").select("*").eq("id", session_id).limit(1).execute()
        )
        if len(result.data) == 0:
            logger.error(f"DB no session found for id {session_id}")
            return None

        session = result.data[0]

        logger.trace(f"DB session {session_id} found")

        return Session(
            id=session["id"],
            title=session["title"],
            created_at=datetime.fromisoformat(session["created_at"]),
            last_activity_at=datetime.fromisoformat(session["last_activity_at"]),
            system_state=json.loads(session["system_state_json"]),
            user_state=json.loads(session["user_state_json"]),
            owner_id=session["owner_id"],
            is_open=session["is_open"],
        )
    except Exception as e:
        logger.error(f"DB error getting session {session_id}")
        logger.exception(e)
        return None


def open_session(client: SupabaseClient, session_id: int) -> Optional[int]:
    try:
        logger.trace(f"DB opening session {session_id}")
        result = (
            client.table("sessions")
            .update({"is_open": True})
            .eq("id", session_id)
            .execute()
        )
        if len(result.data) == 0:
            logger.error(f"DB no session opened for id {session_id}")
            return None

        logger.trace(f"DB session {session_id} opened")
        return result.data[0]["id"]
    except Exception as e:
        logger.error(f"DB error opening session {session_id}")
        logger.exception(e)
        return None


def close_session(client: SupabaseClient, session_id: int) -> Optional[int]:
    try:
        logger.trace(f"DB closing session {session_id}")
        result = (
            client.table("sessions")
            .update({"is_open": False})
            .eq("id", session_id)
            .execute()
        )
        if len(result.data) == 0:
            logger.error(f"DB no session closed for id {session_id}")
            return None

        logger.trace(f"DB session {session_id} closed")
        return result.data[0]["id"]
    except Exception as e:
        logger.error(f"DB error closing session {session_id}")
        logger.exception(e)
        return None


def close_all_open_sessions(client: SupabaseClient) -> Optional[list[int]]:
    try:
        logger.trace("DB closing all open sessions")
        result = (
            client.table("sessions")
            .update({"is_open": False})
            .eq("is_open", True)
            .execute()
        )
        if len(result.data) == 0:
            logger.trace("DB no open sessions found")
            return []

        logger.trace(f"DB {len(result.data)} open sessions closed")
        return [s["id"] for s in result.data]
    except Exception as e:
        logger.error("DB error closing all open sessions")
        logger.exception(e)
        return None


def delete_session(client: SupabaseClient, session_id: int) -> Optional[int]:
    try:
        logger.trace(f"DB deleting session {session_id}")
        result = client.table("sessions").delete().eq("id", session_id).execute()
        if len(result.data) == 0:
            logger.error(f"DB no session deleted for id {session_id}")
            return None

        logger.trace(f"DB session {session_id} deleted")
        return result.data[0]["id"]
    except Exception as e:
        logger.error(f"DB error deleting session {session_id}")
        logger.exception(e)
        return None


def add_session(
    client: SupabaseClient, owner_id: str, system_state: dict, user_state: dict
) -> Optional[int]:
    try:
        logger.trace(f"DB adding session for {owner_id}")
        result = (
            client.table("sessions")
            .insert(
                {
                    "owner_id": owner_id,
                    "title": generate_randome_tripartite_name(),
                    "system_state_json": json.dumps(system_state),
                    "user_state_json": json.dumps(user_state),
                }
            )
            .execute()
        )
        if len(result.data) == 0:
            logger.error(f"DB no session added for user {owner_id}")
            return None

        logger.trace(f"DB session {result.data[0]['id']} added for user {owner_id}")
        return result.data[0]["id"]
    except Exception as e:
        logger.error(f"DB error adding session for user {owner_id}")
        logger.exception(e)
        return None


def duplicate_session(client: SupabaseClient, session_id: int) -> Optional[int]:
    try:
        logger.trace(f"DB duplicating session {session_id}")
        session = get_session(client, session_id)
        if session is None:
            logger.error(f"DB no session found for id {session_id}")
            return None

        session_title_ends_with_number = session.title[-3:].isdigit()
        new_session_title = session.title + " 1"
        if session_title_ends_with_number:
            new_session_title = f"{session.title[:-2]}{int(session.title[-2:]) + 1}"

        result = (
            client.table("sessions")
            .insert(
                {
                    "owner_id": session.owner_id,
                    "title": new_session_title,
                    "system_state_json": json.dumps(session.system_state),
                    "user_state_json": json.dumps(session.user_state),
                }
            )
            .execute()
        )
        if len(result.data) == 0:
            logger.error(f"DB no session duplicated for id {session_id}")
            return None

        new_session_id = result.data[0]["id"]
        result = duplicate_all_session_messages_and_assign_to_new_session(
            client, session_id, new_session_id
        )

        if result is None:
            logger.error(
                f"DB messages duplication failed, stoping duplication for id {session_id}"
            )
            return None

        logger.trace(f"DB session {session_id} duplicated")

        return new_session_id
    except Exception as e:
        logger.error(f"DB error duplicating session {session_id}")
        logger.exception(e)
        return None


def update_states(
    client: SupabaseClient, session_id: int, system_state: dict, user_state: dict
) -> Optional[int]:
    try:
        logger.trace(f"DB updating states for session {session_id}")

        result = (
            client.table("sessions")
            .update(
                {
                    "system_state_json": json.dumps(system_state),
                    "user_state_json": json.dumps(user_state),
                    "last_activity_at": datetime.now(UTC).isoformat(),
                }
            )
            .eq("id", session_id)
            .execute()
        )
        if len(result.data) == 0:
            logger.error(f"DB no session updated for id {session_id}")
            return None

        logger.trace(f"DB session {session_id} updated")
        return result.data[0]["id"]
    except Exception as e:
        logger.error(f"DB error updating states for session {session_id}")
        logger.exception(e)
        return None
