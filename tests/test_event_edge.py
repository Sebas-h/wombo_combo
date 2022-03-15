from tests.base_test_case import BaseTestCase, buf_keys
from wombo_combo.global_state import Buffer, GlobalState
from wombo_combo.input_event_codes import Key
from wombo_combo.key_event_handler import key_event_handler
from wombo_combo.type_hints import KeyAlreadyPressed


class TestKeyEdgeCaseEvents(BaseTestCase):
    def test_target_second_combo_up_same_key(self):
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_J, "value": "up"},
            incoming_state=([], [(3, {Key.KEY_U})]),
            expected_action=[{"code": Key.KEY_J, "value": "up"}],
            expected_result_state=(buf_keys(), [(3, {Key.KEY_U})]),
        )

    def test_same_key_down_second_time(self):
        with self.assertRaises(KeyAlreadyPressed):
            key_event_handler(
                incoming={"code": Key.KEY_J, "value": "down"},
                state=GlobalState(
                    Buffer([{"key": Key.KEY_J, "time_pressed_ns": 0}]),
                    self.create_combos_state([(3, {Key.KEY_U})]),
                ),
            )

    def test_same_key_down_in_active_targets(self):
        with self.assertRaises(KeyAlreadyPressed):
            key_event_handler(
                incoming={"code": Key.KEY_U, "value": "down"},
                state=GlobalState(
                    Buffer([{"key": Key.KEY_J, "time_pressed_ns": 0}]),
                    self.create_combos_state([(3, {Key.KEY_U})]),
                ),
            )
