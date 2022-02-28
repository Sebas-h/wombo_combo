import unittest
from input_event_codes import Key
from main import (
    BufferedKey,
    ComboMap,
    GlobalState,
    KeyEvent,
    ResultAction,
    TimeOut,
    key_event_handler,
)


class BaseTestCase(unittest.TestCase):
    THRESHOLD_MS = 50
    CONFIG: list[ComboMap] = [
        {
            "id": 0,
            "activator": [Key.KEY_J, Key.KEY_K],
            "to": [Key.KEY_ESC],
        },
        {
            "id": 1,
            "activator": [Key.KEY_H, Key.KEY_J, Key.KEY_K],
            "to": [Key.KEY_2],
        },
        {
            "id": 2,
            "activator": [Key.KEY_S, Key.KEY_D],
            "to": [Key.KEY_F12],
        },
        {
            "id": 3,
            "activator": [Key.KEY_U, Key.KEY_J],
            "to": [Key.KEY_TAB],
        },
    ]

    def validate_handler_result(
        self,
        incoming_event: KeyEvent | TimeOut,
        incoming_state: GlobalState,
        expected_action: ResultAction,
        expected_result_state: GlobalState,
    ):
        action = key_event_handler(
            config=self.CONFIG,
            incoming=incoming_event,
            state=incoming_state,
        )
        self.assertEqual(action, expected_action)
        self.assertEqual(
            set(b["key"] for b in incoming_state.buffered_key_down_events),
            set(
                b["key"] for b in expected_result_state.buffered_key_down_events
            ),
        )
        self.assertEqual(
            incoming_state.active_targets, expected_result_state.active_targets
        )


def buf_keys(*keys: Key) -> list[BufferedKey]:
    return [{"key": key, "time_pressed_ns": 0} for key in keys]
