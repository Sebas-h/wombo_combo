from dataclasses import dataclass
from typing import Set

from wombo_combo.input_event_codes import Key
from wombo_combo.type_hints import ActiveCombo, BufferedKey, Combos, IdleCombo, KeyEvent


@dataclass
class GlobalState:
    buffered_events: list[BufferedKey]
    combos: Combos

    @property
    def buffered_keys(self) -> list[Key]:
        return [b["key"] for b in self.buffered_events]

    def create_key_events_from_buffer(self) -> list[KeyEvent]:
        return [
            {"code": b["key"], "value": "down"} for b in self.buffered_events
        ]

    def get_active_combos(self, key: Key) -> list[ActiveCombo]:
        return [
            combo
            for combo in self.combos
            if isinstance(combo, ActiveCombo) and key in combo.state
        ]

    def get_fully_downed_combos(self, key: Key) -> list[ActiveCombo]:
        return [
            combo
            for combo in self.combos
            if isinstance(combo, ActiveCombo)
            and combo.is_fully_down
            and key in combo.state
        ]

    def is_key_pressed(self, key: Key) -> bool:
        active_combos_keys = set(
            active_key
            for combo in self.combos
            if isinstance(combo, ActiveCombo)
            for active_key in combo.state
        )
        return key in active_combos_keys.union(set(self.buffered_keys))

    def is_buffer_complete_combo(self) -> IdleCombo | None:
        for combo in self.combos:
            if isinstance(combo, IdleCombo) and set(self.buffered_keys) == set(
                combo.source
            ):
                return combo
        return None

    def activate_target(self, combo: IdleCombo) -> list[KeyEvent]:
        self.combos = list(
            map(
                lambda cb: cb.to_active_combo()
                if cb.id == combo.id and isinstance(cb, IdleCombo)
                else cb,
                self.combos,
            )
        )
        # Reset buffer
        self.buffered_events.clear()
        # Return target (to be written out)
        return [{"code": k, "value": "down"} for k in combo.target]

    def get_possible_combos(self, incoming_key: Key) -> list[IdleCombo]:
        """
        Retruns list of combos that are possible given the keys being buffered and
        the incoming key

        Example:
            if incoming = KEY_J
               and buffered = [ KEY_K ]
               and config includes the map `{KEY_J, KEY_K} to KEY_ESC`
            then
                `{KEY_J, KEY_K} to KEY_ESC` will be returned as one of the
                possible combos
        """
        # TODO: Should we make sure we do not return any combos that are currently
        # in `state.active_targets`?  Maybe it does not matter?
        buff_keys: Set[Key] = set(self.buffered_keys).union({incoming_key})
        return [
            combo
            for combo in self.combos
            if isinstance(combo, IdleCombo)
            and buff_keys.issubset(set(combo.source))
        ]

    def is_combo_complete(self, combo: IdleCombo, incoming_key: Key):
        return set(combo.source) == set(self.buffered_keys + [incoming_key])
