from yourapp.example_logic.example import new_expand_state
from yourapp.chat.payload import Payload
from yourapp.chat.payloads import PayloadChat, PayloadOpenChat
from yourapp.core.system_state import SystemState, SystemStateExecInputs
from yourapp.core.system_states.registry import register_state


def new_start_state():
    return SystemState({"type": "start"}, execute_start)


def execute_start(
    inputs: SystemStateExecInputs,
) -> tuple["SystemState", list[Payload]]:
    return new_expand_state(), [
        PayloadChat(
            "Hello! I'm Your app.\nI can do stuff for you! Chat with me."
        ),
        PayloadOpenChat(),
    ]


register_state("start", execute_start)
