from wombo_combo.global_state import GlobalState
from wombo_combo.type_hints import (
    ActiveCombo,
    ComboMap,
    Combos,
    IdleCombo,
    KeyAlreadyPressed,
    KeyEvent,
    ResultAction,
    T,
    TimeOut,
)

THRESHOLD_MS = 50


def key_event_handler(
    incoming: KeyEvent | TimeOut, state: GlobalState
) -> ResultAction:
    """
    [key event] -> [key_event_handler()]{mutates global `state`} -> [action(s)]
    """
    if isinstance(incoming, TimeOut):
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

    if combo := state.is_buffer_a_combo():
        write_events = state.activate_combo(combo)
        return write_events + [incoming]

    buffered_key_events = state.buffer.to_key_events(clear_buffer=True)

    # Check if the incoming key on its own is part of a combo
    if state.is_combo_key(incoming_key):
        state.buffer.events.append(
            {"key": incoming["code"], "time_pressed_ns": 123}
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
        combo.state = set(filter(lambda x: x is not incoming_key, combo.state))

    # Update active combo with empty state/set to idle combo
    for idx, combo in enumerate(state.combos):
        if isinstance(combo, ActiveCombo) and len(combo.state) == 0:
            state.combos[idx] = combo.to_idle_combo()

    return result_action


def flatten_2d_seq(t: list[list[T]]) -> list[T]:
    return [item for sublist in t for item in sublist]


def initialize_combos_state(config: list[ComboMap]) -> Combos:
    return [
        IdleCombo(
            id=idx,
            source=combo_map["activator"],
            target=combo_map["to"],
            state=None,
        )
        for idx, combo_map in enumerate(config)
    ]
