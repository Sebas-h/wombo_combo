from typing import Tuple
import unittest
from input_event_codes import Key
from main import GlobalState, KeyEvent, ResultAction
from tests.base_test_case import BaseTestCase, buf_keys


class TestKeySingleEvents(BaseTestCase):
    def test_init_j_incoming(self):
        """Test J key incoming"""
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_J, "value": "down"},
            incoming_state=GlobalState([], []),
            expected_action=50,
            expected_result_state=GlobalState(buf_keys(Key.KEY_J), []),
        )

    def test_init_nc_incoming(self):
        """Test non-combo key incoming"""
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_0, "value": "down"},
            incoming_state=GlobalState([], []),
            expected_action=[{"code": Key.KEY_0, "value": "down"}],
            expected_result_state=GlobalState(buf_keys(), []),
        )

    def test_second_combo_key_incoming(self):
        """Second combo key for a 2 key combo with no overlap superset combo"""
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_D, "value": "down"},
            incoming_state=GlobalState(
                [{"key": Key.KEY_S, "time_pressed_ns": 0}], []
            ),
            expected_action=[{"code": Key.KEY_F12, "value": "down"}],
            expected_result_state=GlobalState(
                buf_keys(),
                [
                    {
                        "combo_idx": 2,
                        "downed_keys": {Key.KEY_S, Key.KEY_D},
                        "target_down": True,
                    }
                ],
            ),
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
            incoming_state=GlobalState(
                [{"key": Key.KEY_J, "time_pressed_ns": 0}], []
            ),
            expected_action=([{"code": Key.KEY_J, "value": "down"}], 50),
            expected_result_state=GlobalState(buf_keys(Key.KEY_D), []),
        )
        
    def test_new_combo_start_with_active_target(self):
        self.validate_handler_result(
            incoming_event={"code": Key.KEY_J, "value": "down"},
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
            expected_action=50,
            expected_result_state=GlobalState(
                buf_keys(Key.KEY_J),
                [
                    {
                        "combo_idx": 3,
                        "downed_keys": {Key.KEY_U},
                        "target_down": False,
                    }
                ],
            ),
        )






class TestKeyEventSequence(BaseTestCase):
    def test_five_combo_key_events(self):
        """
        Test: j down -> k down -> j up -> j down -> h down
        """
        state = GlobalState([], [])
        test_events_sequence = [
            (
                {"code": Key.KEY_J, "value": "down"},
                50,
                GlobalState(buf_keys(Key.KEY_J), []),
            ),
            (
                {"code": Key.KEY_K, "value": "down"},
                50,
                GlobalState(buf_keys(Key.KEY_J, Key.KEY_K), []),
            ),
            (
                {"code": Key.KEY_J, "value": "up"},
                [
                    {"code": Key.KEY_J, "value": "down"},
                    {"code": Key.KEY_K, "value": "down"},
                    {"code": Key.KEY_J, "value": "up"},
                ],
                GlobalState(buf_keys(), []),
            ),
            (
                {"code": Key.KEY_J, "value": "down"},
                50,
                GlobalState(buf_keys(Key.KEY_J), []),
            ),
            (
                {"code": Key.KEY_H, "value": "down"},
                50,
                GlobalState(buf_keys(Key.KEY_J, Key.KEY_H), []),
            ),
        ]
        for test_event in test_events_sequence:
            self.validate_handler_result(
                incoming_event=test_event[0],
                incoming_state=state,
                expected_action=test_event[1],
                expected_result_state=test_event[2],
            )

    def test_subset_combo(self):
        """
        Test: j-down -> u-down
        """
        state = GlobalState([], [])
        test_events_sequence: list[
            Tuple[KeyEvent, ResultAction, GlobalState]
        ] = [
            (
                {"code": Key.KEY_J, "value": "down"},
                50,
                GlobalState(buf_keys(Key.KEY_J), []),
            ),
            (
                {"code": Key.KEY_U, "value": "down"},
                [{"code": Key.KEY_TAB, "value": "down"}],
                GlobalState(
                    buf_keys(),
                    [
                        {
                            "combo_idx": 3,
                            "downed_keys": {Key.KEY_J, Key.KEY_U},
                            "target_down": True,
                        }
                    ],
                ),
            ),
        ]
        for test_event in test_events_sequence:
            self.validate_handler_result(
                incoming_event=test_event[0],
                incoming_state=state,
                expected_action=test_event[1],
                expected_result_state=test_event[2],
            )

    def test_subset_combo_tricky(self):
        """
        Test: j-down -> k-down -> nc-down
        """
        state = GlobalState([], [])
        test_events_sequence: list[
            Tuple[KeyEvent, ResultAction, GlobalState]
        ] = [
            (
                {"code": Key.KEY_K, "value": "down"},
                50,
                GlobalState(buf_keys(Key.KEY_K), []),
            ),
            (
                {"code": Key.KEY_J, "value": "down"},
                50,
                GlobalState(buf_keys(Key.KEY_K, Key.KEY_J), []),
            ),
            (
                {"code": Key.KEY_A, "value": "down"},
                [
                    {"code": Key.KEY_ESC, "value": "down"},
                    {"code": Key.KEY_A, "value": "down"},
                ],
                GlobalState(
                    buf_keys(),
                    [
                        {
                            "combo_idx": 0,
                            "downed_keys": {Key.KEY_J, Key.KEY_K},
                            "target_down": True,
                        }
                    ],
                ),
            ),
        ]
        for test_event in test_events_sequence:
            self.validate_handler_result(
                incoming_event=test_event[0],
                incoming_state=state,
                expected_action=test_event[1],
                expected_result_state=test_event[2],
            )

    def test_superset_combo(self):
        """
        Test: j-down -> u-down
        """
        state = GlobalState([], [])
        test_events_sequence: list[
            Tuple[KeyEvent, ResultAction, GlobalState]
        ] = [
            (
                {"code": Key.KEY_K, "value": "down"},
                50,
                GlobalState(buf_keys(Key.KEY_K), []),
            ),
            (
                {"code": Key.KEY_J, "value": "down"},
                50,
                GlobalState(buf_keys(Key.KEY_K, Key.KEY_J), []),
            ),
            (
                {"code": Key.KEY_H, "value": "down"},
                [{"code": Key.KEY_2, "value": "down"}],
                GlobalState(
                    buf_keys(),
                    [
                        {
                            "combo_idx": 1,
                            "downed_keys": {
                                Key.KEY_J,
                                Key.KEY_K,
                                Key.KEY_H,
                            },
                            "target_down": True,
                        },
                    ],
                ),
            ),
        ]
        for test_event in test_events_sequence:
            self.validate_handler_result(
                incoming_event=test_event[0],
                incoming_state=state,
                expected_action=test_event[1],
                expected_result_state=test_event[2],
            )


if __name__ == "__main__":
    unittest.main()
