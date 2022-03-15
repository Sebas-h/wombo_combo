from wombo_combo.config import THRESHOLD_MS
from wombo_combo.global_state import GlobalState
from wombo_combo.input_event_codes import Key
from wombo_combo.type_hints import (
    ActiveCombo,
    KeyAlreadyPressed,
    KeyEvent,
    ResultAction,
    TimeOut,
)


def key_event_handler(
    incoming: KeyEvent | TimeOut, state: GlobalState
) -> ResultAction:
    """
    [key event] -> [key_event_handler()]{mutates global `state`} -> [action(s)]
    """
    if isinstance(incoming, TimeOut):
        if combo := state.is_buffer_complete_combo():
            return state.activate_combo(combo)
        return state.buffer.to_key_events(clear_buffer=True)

    if incoming["value"] == "down":
        return handle_key_down_event(incoming, state)

    return handle_key_up_event(incoming, state)


def handle_key_down_event(
    incoming: KeyEvent, state: GlobalState
) -> ResultAction:
    incoming_key = incoming["code"]

    # Check if down key already in buffer
    if state.is_key_pressed(incoming_key):
        # NOTE: Not sure how to handle this currently.
        # this situation shouldn't really occur in practice
        raise KeyAlreadyPressed

    possible_combos = state.get_possible_combos(incoming_key)

    if len(possible_combos) > 0:
        if len(possible_combos) == 1 and state.is_combo_complete(
            possible_combos[0], incoming_key
        ):
            return state.activate_combo(possible_combos[0])

        # Append incoming key to buffer and return threshold timer ms
        state.buffer.events.append({"key": incoming_key, "time_pressed_ns": 0})
        return THRESHOLD_MS

    if len(state.buffer.events) == 0:
        return [incoming]

    if combo := state.is_buffer_complete_combo():
        write_events = state.activate_combo(combo)
        return write_events + [incoming]

    buffered_key_events = state.buffer.to_key_events(clear_buffer=True)

    # Check if the incoming key on its own is part of a combo
    if state.is_combo_key(incoming_key):
        state.buffer.events.append(
            {"key": incoming["code"], "time_pressed_ns": 1}
        )
        return (buffered_key_events, THRESHOLD_MS)

    return buffered_key_events + [incoming]


def handle_key_up_event(incoming: KeyEvent, state: GlobalState) -> ResultAction:
    incoming_key = incoming["code"]

    if incoming_key in state.buffer.keys:
        buffered_key_events = state.buffer.to_key_events(clear_buffer=True)
        return buffered_key_events + [incoming]

    active_combos = state.get_active_combos(incoming_key)

    if len(active_combos) == 0:
        return [incoming]

    return handle_active_combos(incoming_key, state, active_combos)


def handle_active_combos(
    incoming_key: Key, state: GlobalState, active_combos: list[ActiveCombo]
):
    result_action: ResultAction = None

    if fully_downed_combos := [
        combo for combo in active_combos if combo.is_fully_down
    ]:
        result_action = [
            {"code": tgt_key, "value": "up"}
            for t in fully_downed_combos
            for tgt_key in t.target
        ]

    # Update active combo state
    for combo in active_combos:
        combo.pressed_keys = set(
            filter(lambda x: x is not incoming_key, combo.pressed_keys)
        )

    # Convert active combos without pressed/active keys to idle combos
    for idx, combo_ in enumerate(state.combos):
        if isinstance(combo_, ActiveCombo) and len(combo_.pressed_keys) == 0:
            state.combos[idx] = combo_.to_idle_combo()

    return result_action
