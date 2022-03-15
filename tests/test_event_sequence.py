from typing import Tuple
from zlib import Z_FIXED

from tests.base_test_case import BaseTestCase, TestState, buf_keys
from wombo_combo.input_event_codes import Key
from wombo_combo.type_hints import KeyEvent, ResultAction


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

    def test_subcombo_switch(self):
        """
        Part of combo down -> switch to different combo
        """
        state = ([], [])
        test_events_sequence: list[Tuple[KeyEvent, ResultAction, TestState]] = [
            (
                {"code": Key.KEY_K, "value": "down"},
                50,
                (buf_keys(Key.KEY_K), []),
            ),
            (
                {"code": Key.KEY_U, "value": "down"},
                ([{"code": Key.KEY_K, "value": "down"}], 50),
                (buf_keys(Key.KEY_U), []),
            ),
            (
                {"code": Key.KEY_J, "value": "down"},
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

    def test_subcombo_switch_with_superset(self):
        """ """
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
                {"code": Key.KEY_U, "value": "down"},
                [
                    {"code": Key.KEY_ESC, "value": "down"},
                    {"code": Key.KEY_U, "value": "down"},
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
