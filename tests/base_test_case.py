import time
import unittest
from typing import Set

from wombo_combo.global_state import Buffer, GlobalState
from wombo_combo.input_event_codes import Key
from wombo_combo.key_event_handler import key_event_handler
from wombo_combo.main import initialize_combos_state
from wombo_combo.type_hints import (
    ActiveCombo,
    BufferEvent,
    ComboMap,
    CombosState,
    IdleCombo,
    KeyEvent,
    ResultAction,
    TimeOut,
)

TestActiveCombo = tuple[int, Set[Key]]
TestState = tuple[list[BufferEvent], list[TestActiveCombo]]


class BaseTestCase(unittest.TestCase):
    THRESHOLD_MS = 50
    CONFIG: list[ComboMap] = [
        ### 0
        {
            "activator": (Key.KEY_J, Key.KEY_K),
            "to": (Key.KEY_ESC,),
        },
        ### 1
        {
            "activator": (Key.KEY_H, Key.KEY_J, Key.KEY_K),
            "to": (Key.KEY_2,),
        },
        ### 2
        {
            "activator": (Key.KEY_S, Key.KEY_D),
            "to": (Key.KEY_F12,),
        },
        ### 3
        {
            "activator": (Key.KEY_U, Key.KEY_J),
            "to": (Key.KEY_TAB,),
        },
    ]

    def validate_handler_result(
        self,
        incoming_event: KeyEvent | TimeOut,
        incoming_state: tuple[list[BufferEvent], list[TestActiveCombo]],
        expected_action: ResultAction,
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
        # s = time.time()
        action = key_event_handler(
            incoming=incoming_event, state=_incoming_state
        )
        # print(f"Key event handler took {(time.time() - s) * 1000} ms")
        self.assertEqual(action, expected_action)
        self.assertEqual(
            set(_incoming_state.buffer.keys),
            set(_expected_result_state.buffer.keys),
        )
        for combo, expected_combo in zip(
            _incoming_state.combos, _expected_result_state.combos
        ):
            self.assertEqual(combo.id, expected_combo.id, "combo.id fail")
            self.assertEqual(
                combo.source, expected_combo.source, "combo.source fail"
            )
            self.assertEqual(
                combo.target, expected_combo.target, "combo.target fail"
            )
            self.assertEqual(
                combo.pressed_keys,
                expected_combo.pressed_keys,
                "combo.state fail",
            )

    def create_combos_state(
        self, active_combos: list[TestActiveCombo]
    ) -> CombosState:
        def mapper(combo: IdleCombo | ActiveCombo) -> ActiveCombo | IdleCombo:
            if m := next((x for x in active_combos if x[0] == combo.id), None):
                return ActiveCombo(
                    id=m[0],
                    source=combo.source,
                    target=combo.target,
                    pressed_keys=m[1],
                )
            return combo

        return [mapper(combo) for combo in initialize_combos_state(self.CONFIG)]


def buf_keys(*keys: Key) -> list[BufferEvent]:
    return [{"key": key, "time_pressed_ns": 0} for key in keys]
