from dataclasses import dataclass
from typing import Callable

from yourapp.chat.payload import Payload
from yourapp.sessions.messages import Message
from yourapp.user import UserInfos


SystemStateFunc = Callable[
    ["SystemStateExecInputs"], tuple["SystemState", list[Payload]]
]


class SystemStateExecInputs:
    inner: dict
    user: UserInfos
    history: list[Message]
    send_payload: Callable[[Payload], None]
    expect_payload: Callable[[], Payload]

    def __init__(
        self,
        inner: dict,
        user: UserInfos,
        history: list[Message],
        send_payload: Callable[[Payload], None],
        expect_payload: Callable[[], Payload],
    ):
        self.inner = inner
        self.user = user
        self.history = history
        self.send_payload = send_payload
        self.expect_payload = expect_payload


@dataclass
class SystemState:
    inner: dict
    f: SystemStateFunc

    def to_dict(self) -> dict:
        return self.inner

    def execute(
        self,
        user: UserInfos,
        history: list[Message],
        send_payload: Callable[[Payload], None],
        expect_payload: Callable[[], Payload],
    ) -> tuple["SystemState", list[Payload]]:
        return self.f(
            SystemStateExecInputs(
                self.inner, user, history, send_payload, expect_payload
            )
        )

    def __eq__(self, value: object) -> bool:
        """
        Compare the SystemState object with another object for equality.

        Args:
            value (object): The object to compare with.

        Returns:
            bool: True if the objects are equal, False otherwise.
        """
        if not isinstance(value, SystemState):
            return False

        equal = True
        for key in self.inner.keys():
            if self.inner[key] != value.inner[key]:
                equal = False
                break

        return equal
