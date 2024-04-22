from typing import Callable
from yourapp.core.system_state import SystemState, SystemStateFunc


SYSTEM_STATES_REGISTRY: dict[str, Callable[[dict], SystemState]] = {}


def register_state(type: str, executor: SystemStateFunc):
    global SYSTEM_STATES_REGISTRY
    SYSTEM_STATES_REGISTRY[type] = lambda inner: SystemState(
        dict({"type": type}, **inner), executor
    )


def system_state_from_dict(data: dict) -> SystemState:
    global SYSTEM_STATES_REGISTRY
    type = data.get("type")
    if type is None:
        raise ValueError("SystemState type is missing")
    state = SYSTEM_STATES_REGISTRY.get(type)
    if state is None:
        raise ValueError(f"Unknown SystemState type: {type}")
    return state(data)
