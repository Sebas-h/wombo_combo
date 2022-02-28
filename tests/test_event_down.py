import unittest
from typing import Tuple

from tests.base_test_case import BaseTestCase, TestState, buf_keys
from wombo_combo.input_event_codes import Key
from wombo_combo.main import KeyEvent, ResultAction


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


class TestKeyEventSequence(BaseTestCase):
    def test_five_combo_key_events(self):
        """
        Test: j down -> k down -> j up -> j down -> h down
        """
        state = ([], [])
        test_events_sequence = [
            (
                {"code": Key.KEY_J, "value": "down"},
                50,
                (buf_keys(Key.KEY_J), []),
            ),
            (
                {"code": Key.KEY_K, "value": "down"},
                50,
                (buf_keys(Key.KEY_J, Key.KEY_K), []),
            ),
            (
                {"code": Key.KEY_J, "value": "up"},
                [
                    {"code": Key.KEY_J, "value": "down"},
                    {"code": Key.KEY_K, "value": "down"},
                    {"code": Key.KEY_J, "value": "up"},
                ],
                (buf_keys(), []),
            ),
            (
                {"code": Key.KEY_J, "value": "down"},
                50,
                (buf_keys(Key.KEY_J), []),
            ),
            (
                {"code": Key.KEY_H, "value": "down"},
                50,
                (buf_keys(Key.KEY_J, Key.KEY_H), []),
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
        state = ([], [])
        test_events_sequence: list[Tuple[KeyEvent, ResultAction, TestState]] = [
            (
                {"code": Key.KEY_J, "value": "down"},
                50,
                (buf_keys(Key.KEY_J), []),
            ),
            (
                {"code": Key.KEY_U, "value": "down"},
                [{"code": Key.KEY_TAB, "value": "down"}],
                (buf_keys(), [(3, {Key.KEY_J, Key.KEY_U})]),
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
        state = ([], [])
        test_events_sequence: list[Tuple[KeyEvent, ResultAction, TestState]] = [
            (
                {"code": Key.KEY_K, "value": "down"},
                50,
                (buf_keys(Key.KEY_K), []),
            ),
            (
                {"code": Key.KEY_J, "value": "down"},
                50,
                (buf_keys(Key.KEY_K, Key.KEY_J), []),
            ),
            (
                {"code": Key.KEY_A, "value": "down"},
                [
                    {"code": Key.KEY_ESC, "value": "down"},
                    {"code": Key.KEY_A, "value": "down"},
                ],
                (buf_keys(), [(0, {Key.KEY_J, Key.KEY_K})]),
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
        state = ([], [])
        test_events_sequence: list[Tuple[KeyEvent, ResultAction, TestState]] = [
            (
                {"code": Key.KEY_K, "value": "down"},
                50,
                (buf_keys(Key.KEY_K), []),
            ),
            (
                {"code": Key.KEY_J, "value": "down"},
                50,
                (buf_keys(Key.KEY_K, Key.KEY_J), []),
            ),
            (
                {"code": Key.KEY_H, "value": "down"},
                [{"code": Key.KEY_2, "value": "down"}],
                (buf_keys(), [(1, {Key.KEY_J, Key.KEY_K, Key.KEY_H})]),
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
