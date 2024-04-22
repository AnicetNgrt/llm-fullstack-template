from yourapp.chat.payload import Payload
from yourapp.chat.payloads import PayloadChat, PayloadEndSession
from yourapp.core.system_state import SystemState, SystemStateExecInputs
from yourapp.core.system_states.registry import register_state


def execute_null(inputs: SystemStateExecInputs) -> tuple["SystemState", list[Payload]]:
    return NULL_STATE, []


NULL_STATE = SystemState({"type": "null"}, execute_null)


register_state("null", execute_null)


def new_goodbye_state():
    return SystemState({"type": "goodbye"}, execute_goodbye)


def execute_goodbye(
    inputs: SystemStateExecInputs,
) -> tuple["SystemState", list[Payload]]:
    return NULL_STATE, [PayloadChat("Goodbye!"), PayloadEndSession()]


register_state("goodbye", execute_goodbye)
