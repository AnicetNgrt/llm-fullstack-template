from typing import Optional
from yourapp.chat.payload import Payload


def payload_from_dict(data: dict) -> Payload:
    payload_type = data.get("type")
    if payload_type == "message":
        return PayloadChat.try_from_dict(data)
    elif payload_type == "state" and data.get("state") == "closed":
        return PayloadCloseChat.try_from_dict(data)
    elif payload_type == "state" and data.get("state") == "opened":
        return PayloadOpenChat.try_from_dict(data)
    elif payload_type == "end":
        return PayloadEndSession.try_from_dict(data)
    elif payload_type == "dict":
        return PayloadDict.try_from_dict(data)
    elif payload_type == "text-file":
        return PayloadTextFile.try_from_dict(data)
    raise ValueError(f"Unknown payload type: {data['type']}")


class PayloadChat(Payload):
    message: str

    def __init__(self, message: str):
        self.message = message

    def to_dict(self) -> dict:
        return {"type": "message", "message": self.message}

    @staticmethod
    def try_from_dict(data: dict) -> Optional["PayloadChat"]:
        if data.get("type") == "message":
            return PayloadChat(message=data["message"])
        return None


class PayloadCloseChat(Payload):

    def to_dict(self) -> dict:
        return {"type": "state", "state": "closed"}

    @staticmethod
    def try_from_dict(data: dict) -> Optional["PayloadCloseChat"]:
        if data.get("type") == "state" and data.get("state") == "closed":
            return PayloadCloseChat()
        return None


class PayloadOpenChat(Payload):

    def to_dict(self) -> dict:
        return {"type": "state", "state": "opened"}

    def requires_user_input(self) -> bool:
        return True

    @staticmethod
    def try_from_dict(data: dict) -> Optional["PayloadOpenChat"]:
        if data.get("type") == "state" and data.get("state") == "opened":
            return PayloadOpenChat()
        return None


class PayloadEndSession(Payload):

    def to_dict(self) -> dict:
        return {"type": "end"}

    @staticmethod
    def try_from_dict(data: dict) -> Optional["PayloadEndSession"]:
        if data.get("type") == "end":
            return PayloadEndSession()
        return None


class PayloadDict(Payload):
    data: dict

    def __init__(self, data: dict):
        self.data = data

    def to_dict(self) -> dict:
        return {"type": "dict", "data": self.data}

    @staticmethod
    def try_from_dict(data: dict) -> Optional["PayloadDict"]:
        if data.get("type") == "dict":
            return PayloadDict(data["data"])
        return None


class PayloadTextFile(Payload):
    name: str
    type: str
    content: str

    def __init__(self, name: str, type: str, content: str):
        self.name = name
        self.content = content
        self.type = type

    def to_dict(self) -> dict:
        return {
            "type": "text-file",
            "file": {"name": self.name, "content": self.content, "type": self.type},
        }

    @staticmethod
    def try_from_dict(data: dict) -> Optional["PayloadTextFile"]:
        if data.get("type") == "text-file":
            return PayloadTextFile(
                name=data["file"]["name"],
                content=data["file"]["content"],
                type=data["file"]["type"],
            )
        return None
