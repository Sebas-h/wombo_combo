from tests.base_test_case import BaseTestCase, buf_keys
from wombo_combo.input_event_codes import Key
from wombo_combo.type_hints import TimeOut


class TestKeySingleEvents(BaseTestCase):
    def test_init_j_incoming(self):
        """Test J key incoming"""
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_J, "value": "down"},
            incoming_state=([], []),
            expected_action=50,
            expected_result_state=(buf_keys(Key.KEY_J), []),
        )

    def test_init_nc_incoming(self):
        """Test non-combo key incoming"""
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_0, "value": "down"},
            incoming_state=([], []),
            expected_action=[{"code": Key.KEY_0, "value": "down"}],
            expected_result_state=(buf_keys(), []),
        )

    def test_second_combo_key_incoming(self):
        """Second combo key for a 2 key combo with no overlap superset combo"""
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_D, "value": "down"},
            incoming_state=([{"key": Key.KEY_S, "time_pressed_ns": 0}], []),
            expected_action=[{"code": Key.KEY_F12, "value": "down"}],
            expected_result_state=(buf_keys(), [(2, {Key.KEY_S, Key.KEY_D})]),
        )

    def test_second_combo_key_incoming_ignore_cross(self):
        """
        Cross combo key -> key from a different combo

        We write the keys of the combo we were working on
        and buffer the incombing combo (i.e. this becomes the new combo we are
        working on)
        """
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_D, "value": "down"},
            incoming_state=([{"key": Key.KEY_J, "time_pressed_ns": 0}], []),
            expected_action=([{"code": Key.KEY_J, "value": "down"}], 50),
            expected_result_state=(buf_keys(Key.KEY_D), []),
        )

    def test_new_combo_start_with_active_target(self):
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_J, "value": "down"},
            incoming_state=([], [(3, {Key.KEY_U})]),
            expected_action=50,
            expected_result_state=(buf_keys(Key.KEY_J), [(3, {Key.KEY_U})]),
        )

    def test_timeout_simple(self):
        self.validate_handler_result(
            incoming_event=TimeOut.TIMEOUT,
            incoming_state=(
                [{"key": Key.KEY_J, "time_pressed_ns": 0}],
                [],
            ),
            expected_action=[{"code": Key.KEY_J, "value": "down"}],
            expected_result_state=(buf_keys(), []),
        )

    def test_timeout_subcombo_buffer(self):
        # TODO: Double check. I think this is a valid test/scenario that should
        # actually pass the test
        self.validate_handler_result(
            incoming_event=TimeOut.TIMEOUT,
            incoming_state=(
                [
                    {"key": Key.KEY_J, "time_pressed_ns": 0},
                    {"key": Key.KEY_K, "time_pressed_ns": 0},
                ],
                [],
            ),
            expected_action=[{"code": Key.KEY_ESC, "value": "down"}],
            expected_result_state=(buf_keys(), [(0, {Key.KEY_J, Key.KEY_K})]),
        )
