from input_event_codes import Key
from main import GlobalState
from tests.base_test_case import BaseTestCase, buf_keys


class TestKeySingleEvents(BaseTestCase):
    def test_target_up_returned(self):
        """
        Tests that the target-up event is returned and the active targets
        state is correctly updated
        """
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_J, "value": "up"},
            incoming_state=GlobalState(
                [],
                [
                    {
                        "combo_idx": 3,
                        "downed_keys": {Key.KEY_J, Key.KEY_U},
                        "target_down": True,
                    }
                ],
            ),
            expected_action=[{"code": Key.KEY_TAB, "value": "up"}],
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

    def test_target_up_key_in_multiple_targets(self):
        """
        Tests that the target-up event is returned and the active targets
        state is correctly updated
        """
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_J, "value": "up"},
            incoming_state=GlobalState(
                [],
                [
                    {
                        "combo_idx": 3,
                        "downed_keys": {Key.KEY_J, Key.KEY_U},
                        "target_down": True,
                    },
                    {
                        "combo_idx": 1,
                        "downed_keys": {Key.KEY_J, Key.KEY_K},
                        "target_down": False,
                    },
                ],
            ),
            expected_action=[{"code": Key.KEY_TAB, "value": "up"}],
            expected_result_state=GlobalState(
                buf_keys(),
                [
                    {
                        "combo_idx": 3,
                        "downed_keys": {Key.KEY_U},
                        "target_down": False,
                    },
                    {
                        "combo_idx": 1,
                        "downed_keys": {Key.KEY_K},
                        "target_down": False,
                    },
                ],
            ),
        )

    def test_target_up_key_in_multiple_targets_some_down(self):
        """
        Tests that the target-up event is returned and the active targets
        state is correctly updated
        """
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_J, "value": "up"},
            incoming_state=GlobalState(
                [],
                [
                    {
                        "combo_idx": 3,
                        "downed_keys": {Key.KEY_J},
                        "target_down": False,
                    },
                    {
                        "combo_idx": 1,
                        "downed_keys": {Key.KEY_J, Key.KEY_K, Key.KEY_H},
                        "target_down": True,
                    },
                ],
            ),
            expected_action=[{"code": Key.KEY_2, "value": "up"}],
            expected_result_state=GlobalState(
                buf_keys(),
                [
                    {
                        "combo_idx": 1,
                        "downed_keys": {Key.KEY_K, Key.KEY_H},
                        "target_down": False,
                    },
                ],
            ),
        )

    def test_handle_nck_up(self):
        """
        Checks if we handle a non-combo-key (nck) up event correctly when
        there are active targets
        """
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_Z, "value": "up"},
            incoming_state=GlobalState(
                [],
                [
                    {
                        "combo_idx": 3,
                        "downed_keys": {Key.KEY_J, Key.KEY_U},
                        "target_down": True,
                    }
                ],
            ),
            expected_action=[{"code": Key.KEY_Z, "value": "up"}],
            expected_result_state=GlobalState(
                buf_keys(),
                [
                    {
                        "combo_idx": 3,
                        "downed_keys": {Key.KEY_J, Key.KEY_U},
                        "target_down": True,
                    }
                ],
            ),
        )
