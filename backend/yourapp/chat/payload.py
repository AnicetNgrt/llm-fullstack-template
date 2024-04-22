from abc import ABC, abstractmethod
from typing import Optional


class Payload(ABC):

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    def requires_user_input(self) -> bool:
        return False

    @staticmethod
    @abstractmethod
    def try_from_dict(data: dict) -> Optional["Payload"]:
        pass
