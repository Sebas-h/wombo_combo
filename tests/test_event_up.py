from tests.base_test_case import BaseTestCase, buf_keys
from wombo_combo.input_event_codes import Key


class TestKeySingleEvents(BaseTestCase):
    def test_target_up_returned(self):
        """
        Tests that the target-up event is returned and the active targets
        state is correctly updated
        """
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_J, "value": "up"},
            incoming_state=([], [(3, {Key.KEY_J, Key.KEY_U})]),
            expected_action=[{"code": Key.KEY_TAB, "value": "up"}],
            expected_result_state=(buf_keys(), [(3, {Key.KEY_U})]),
        )

    def test_target_up_key_in_multiple_targets(self):
        """
        Tests that the target-up event is returned and the active targets
        state is correctly updated
        """
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_J, "value": "up"},
            incoming_state=(
                [],
                [(3, {Key.KEY_J, Key.KEY_U}), (1, {Key.KEY_J, Key.KEY_K})],
            ),
            expected_action=[{"code": Key.KEY_TAB, "value": "up"}],
            expected_result_state=(
                buf_keys(),
                [(3, {Key.KEY_U}), (1, {Key.KEY_K})],
            ),
        )

    def test_target_up_key_in_multiple_targets_some_down(self):
        """
        Tests that the target-up event is returned and the active targets
        state is correctly updated
        """
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_J, "value": "up"},
            incoming_state=(
                [],
                [(3, {Key.KEY_J}), (1, {Key.KEY_J, Key.KEY_K, Key.KEY_H})],
            ),
            expected_action=[{"code": Key.KEY_2, "value": "up"}],
            expected_result_state=(buf_keys(), [(1, {Key.KEY_K, Key.KEY_H})]),
        )

    def test_handle_nck_up(self):
        """
        Checks if we handle a non-combo-key (nck) up event correctly when
        there are active targets
        """
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_Z, "value": "up"},
            incoming_state=([], [(3, {Key.KEY_J, Key.KEY_U})]),
            expected_action=[{"code": Key.KEY_Z, "value": "up"}],
            expected_result_state=(buf_keys(), [(3, {Key.KEY_J, Key.KEY_U})]),
        )
