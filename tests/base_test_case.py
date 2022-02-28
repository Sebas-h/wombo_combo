import unittest
from typing import Set
from wombo_combo.global_state import Buffer

from wombo_combo.input_event_codes import Key
from wombo_combo.main import (
    ActiveCombo,
    ComboMap,
    Combos,
    GlobalState,
    IdleCombo,
    KeyEvent,
    ResultAction,
    TimeOut,
    initialize_combos_state,
    key_event_handler,
)
from wombo_combo.type_hints import BufferEvent

TestActiveCombo = tuple[int, Set[Key]]
TestState = tuple[list[BufferEvent], list[TestActiveCombo]]


class BaseTestCase(unittest.TestCase):
    THRESHOLD_MS = 50
    CONFIG: list[ComboMap] = [
        ### 1
        {
            "activator": [Key.KEY_J, Key.KEY_K],
            "to": [Key.KEY_ESC],
        },
        ### 2
        {
            "activator": [Key.KEY_H, Key.KEY_J, Key.KEY_K],
            "to": [Key.KEY_2],
        },
        ### 3
        {
            "activator": [Key.KEY_S, Key.KEY_D],
            "to": [Key.KEY_F12],
        },
        ### 4
        {
            "activator": [Key.KEY_U, Key.KEY_J],
            "to": [Key.KEY_TAB],
        },
    ]

    def validate_handler_result(
        self,
        incoming_event: KeyEvent | TimeOut,
        # incoming_state: GlobalState,
        incoming_state: tuple[list[BufferEvent], list[TestActiveCombo]],
        expected_action: ResultAction,
        # expected_result_state: GlobalState,
        expected_result_state: tuple[list[BufferEvent], list[TestActiveCombo]],
    ):
        _incoming_state = GlobalState(
            Buffer(incoming_state[0]),
            self.create_combos_state(incoming_state[1]),
        )
        _expected_result_state: GlobalState = GlobalState(
            Buffer(expected_result_state[0]),
            self.create_combos_state(expected_result_state[1]),
        )
        action = key_event_handler(
            incoming=incoming_event, state=_incoming_state
        )
        self.assertEqual(action, expected_action)
        self.assertEqual(
            set(_incoming_state.buffer.keys),
            set(_expected_result_state.buffer.keys),
        )
        # self.assertEqual(incoming_state.combos, expected_result_state.combos)
        for combo, expected_combo in zip(
            _incoming_state.combos, _expected_result_state.combos
        ):
            self.assertEqual(combo.id, expected_combo.id, "combo.id faile")
            self.assertEqual(
                combo.source, expected_combo.source, "combo.source fail"
            )
            self.assertEqual(
                combo.target, expected_combo.target, "combo.target fail"
            )
            self.assertEqual(
                combo.state, expected_combo.state, "combo.state fail"
            )

    def create_combos_state(
        self, active_combos: list[TestActiveCombo]
    ) -> Combos:
        def mapper(combo: IdleCombo | ActiveCombo) -> ActiveCombo | IdleCombo:
            if m := next((x for x in active_combos if x[0] == combo.id), None):
                return ActiveCombo(
                    id=m[0],
                    source=combo.source,
                    target=combo.target,
                    state=m[1],
                )
            return combo

        return [mapper(combo) for combo in initialize_combos_state(self.CONFIG)]


def buf_keys(*keys: Key) -> list[BufferEvent]:
    return [{"key": key, "time_pressed_ns": 0} for key in keys]
