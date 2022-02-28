import unittest
from input_event_codes import Key
from main import GlobalState, KeyAlreadyInBuffer, key_event_handler
from tests.base_test_case import BaseTestCase, buf_keys


class TestKeyEdgeCaseEvents(BaseTestCase):
    def test_target_second_combo_up_same_key(self):
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_J, "value": "up"},
            incoming_state=GlobalState(
                [],
                [
                    {
                        "combo_idx": 3,
                        "downed_keys": {Key.KEY_U},
                        "target_down": False,
                    }
                ],
            ),
            expected_action=[{"code": Key.KEY_J, "value": "up"}],
            expected_result_state=GlobalState(
                buf_keys(),
                [
                    {
                        "combo_idx": 3,
                        "downed_keys": {Key.KEY_U},
                        "target_down": False,
                    }
                ],
            ),
        )

    def test_same_key_down_second_time(self):
        with self.assertRaises(KeyAlreadyInBuffer):
            key_event_handler(
                config=self.CONFIG,
                incoming={"code": Key.KEY_J, "value": "down"},
                state=GlobalState(
                    [{"key": Key.KEY_J, "time_pressed_ns": 0}],
                    [
                        {
                            "combo_idx": 3,
                            "downed_keys": {Key.KEY_U},
                            "target_down": False,
                        }
                    ],
                ),
            )

    def test_same_key_down_in_active_targets(self):
        with self.assertRaises(KeyAlreadyInBuffer):
            key_event_handler(
                config=self.CONFIG,
                incoming={"code": Key.KEY_U, "value": "down"},
                state=GlobalState(
                    [{"key": Key.KEY_J, "time_pressed_ns": 0}],
                    [
                        {
                            "combo_idx": 3,
                            "downed_keys": {Key.KEY_U},
                            "target_down": False,
                        }
                    ],
                ),
            )
