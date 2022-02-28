from wombo_combo.global_state import GlobalState
from wombo_combo.input_event_codes import Key
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
        # We have timed out
        events_to_write = state.create_key_events_from_buffer()
        state.buffered_events.clear()
        return events_to_write

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

    if len(possible_combos) == 0:
        if len(state.buffered_events) == 0:
            return [incoming]

        if combo := state.is_buffer_complete_combo():
            write_events = state.activate_target(combo)
            return write_events + [incoming]

        # Cache buffered keys
        tmp_buffered_keys = state.create_key_events_from_buffer()

        # Clear buffer in global state
        state.buffered_events.clear()

        # Check if the incoming key on its own is part of a combo
        if state.get_possible_combos(incoming_key):
            state.buffered_events.append(
                {"key": incoming["code"], "time_pressed_ns": 123}
            )
            return (tmp_buffered_keys, THRESHOLD_MS)

        return tmp_buffered_keys + [incoming]

    if (
        len(state.buffered_events) > 0
        and len(possible_combos) == 1
        and state.is_combo_complete(possible_combos[0], incoming_key)
    ):
        combo = possible_combos[0]
        return state.activate_target(combo)

    # Append incoming key to buffer and return threshold timer ms
    state.buffered_events.append({"key": incoming_key, "time_pressed_ns": 0})
    return THRESHOLD_MS


def handle_key_up_event(incoming: KeyEvent, state: GlobalState) -> ResultAction:
    incoming_key = incoming["code"]

    if incoming_key in state.buffered_keys:
        # Return write all downs + latest up
        to_write = state.create_key_events_from_buffer()
        # Clear the buffer
        state.buffered_events.clear()
        return to_write + [incoming]

    if active_combos := state.get_active_combos(incoming_key):
        result_action: ResultAction = None

        # Handle fully downed combos
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
            combo.state = set(
                filter(lambda x: x is not incoming_key, combo.state)
            )

        # Update active combo with empty state/set to idle combo
        for idx, combo in enumerate(state.combos):
            if isinstance(combo, ActiveCombo) and len(combo.state) == 0:
                state.combos[idx] = combo.to_idle_combo()

        return result_action

    return [incoming]


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


if __name__ == "__main__":
    c = IdleCombo(
        id=1,
        source=[Key.KEY_A],
        target=[Key.KEY_Z],
        state=None,
    )
    print(c)
