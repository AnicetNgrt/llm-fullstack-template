from dataclasses import dataclass
from typing import Optional
from loguru import logger
from supabase import Client as SupabaseClient
from gotrue.types import UserAttributes


@dataclass
class UserInfos:
    id: str
    username: str
    created_at: str
    plan: int

    def from_dict_strict(data: dict) -> "UserInfos":
        # crash if any field is missing or has the wrong type
        for field in UserInfos.__dataclass_fields__.keys():
            if field not in data:
                raise ValueError(f"Missing field {field}")
            if not isinstance(data[field], UserInfos.__dataclass_fields__[field].type):
                raise ValueError(f"Field {field} has the wrong type")

        return UserInfos(
            id=data["id"],
            username=data["username"],
            created_at=data["created_at"],
            plan=data["plan"],
        )


def get_user_infos(client: SupabaseClient, user_id: str) -> Optional[UserInfos]:
    try:
        logger.trace(f"DB getting user infos for user {user_id}")
        result = (
            client.table("users infos").select("*").eq("id", user_id).limit(1).execute()
        )
        if len(result.data) == 0:
            logger.trace(f"DB no user infos found for user {user_id}")
            return UserInfos(
                id="NOT_FOUND", username="NOT_FOUND", created_at="NOT_FOUND", plan=0
            )

        logger.trace(f"DB user infos found for user {user_id}")
        return UserInfos.from_dict_strict(result.data[0])
    except Exception as e:
        logger.error(f"DB error getting user infos for user {user_id}")
        logger.exception(e)
        return None


def onboard_user(
    user_client: SupabaseClient,
    admin_client: SupabaseClient,
    user_id: str,
    username: str,
    new_password: str,
) -> Optional[str]:
    try:
        logger.trace(f"DB onboarding user {user_id}")
        result = (
            admin_client.table("users infos")
            .insert({"id": user_id, "username": username})
            .execute()
        )

        if len(result.data) == 0:
            logger.error(f"DB no user onboarded for user {user_id}")
            return None

        user_client.auth.update_user(UserAttributes(password=new_password))

        logger.trace(f"DB user onboarded for user {user_id}")
        return username
    except Exception as e:
        logger.error(f"DB error onboarding user {user_id}")
        logger.exception(e)
        return None
