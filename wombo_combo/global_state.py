from dataclasses import dataclass
from typing import Set

from wombo_combo.input_event_codes import Key
from wombo_combo.type_hints import (
    ActiveCombo,
    BufferEvent,
    CombosState,
    IdleCombo,
    KeyEvent,
)


@dataclass
class Buffer:
    events: list[BufferEvent]

    @property
    def keys(self) -> list[Key]:
        return [e["key"] for e in self.events]

    def to_key_events(self, clear_buffer: bool) -> list[KeyEvent]:
        key_events: list[KeyEvent] = [
            {"code": e["key"], "value": "down"} for e in self.events
        ]
        if clear_buffer:
            self.events.clear()
        return key_events


@dataclass
class GlobalState:
    buffer: Buffer
    combos: CombosState

    def get_active_combos(self, key: Key) -> list[ActiveCombo]:
        return [
            combo
            for combo in self.combos
            if isinstance(combo, ActiveCombo) and key in combo.pressed_keys
        ]

    def get_fully_downed_combos(self, key: Key) -> list[ActiveCombo]:
        return [
            combo
            for combo in self.combos
            if isinstance(combo, ActiveCombo)
            and combo.is_fully_down
            and key in combo.pressed_keys
        ]

    def is_key_pressed(self, key: Key) -> bool:
        active_combos_keys = set(
            active_key
            for combo in self.combos
            if isinstance(combo, ActiveCombo)
            for active_key in combo.pressed_keys
        )
        return key in active_combos_keys.union(set(self.buffer.keys))

    def is_buffer_complete_combo(self) -> IdleCombo | None:
        for combo in self.combos:
            if isinstance(combo, IdleCombo) and set(self.buffer.keys) == set(
                combo.source
            ):
                return combo
        return None

    def activate_combo(self, combo: IdleCombo) -> list[KeyEvent]:
        self.combos = list(
            map(
                lambda cb: cb.to_active_combo()
                if cb.id == combo.id and isinstance(cb, IdleCombo)
                else cb,
                self.combos,
            )
        )
        # Reset buffer
        self.buffer.events.clear()
        # Return target (to be written out)
        return [{"code": k, "value": "down"} for k in combo.target]

    def get_possible_combos(self, incoming_key: Key) -> list[IdleCombo]:
        """
        Retruns list of combos that are possible given the buffered keys in
        combination with the incoming key.
        Note that possible combos do not have to be complete yet (i.e. all its
        source keys do not have to be pressed yet)
        """
        keys: Set[Key] = set(self.buffer.keys).union({incoming_key})
        return [
            combo
            for combo in self.combos
            if isinstance(combo, IdleCombo) and keys.issubset(set(combo.source))
        ]

    def is_combo_complete(self, combo: IdleCombo, incoming_key: Key):
        """
        Check whether the buffered keys in combination with the incoming key
        matches/completes the given combo.
        """
        return set(combo.source) == set(self.buffer.keys + [incoming_key])

    def is_combo_key(self, key: Key) -> bool:
        for combo in self.combos:
            if key in combo.source:
                return True
        return False
