from dataclasses import dataclass
from enum import Enum
from types import NoneType
from typing import NewType, Set, Tuple, Literal, TypeVar, TypedDict, Union
from input_event_codes import Key

THRESHOLD_MS = 50

T = TypeVar("T")


class BufferedKey(TypedDict):
    key: Key
    time_pressed_ns: int


class ComboMap(TypedDict):
    id: int
    activator: list[Key]
    to: list[Key]

@dataclass
class Combo:
    id: int
    source: list[Key]
    target: list[Key]
    state: Literal["idle" , "active", "activated"] 

class KeyEvent(TypedDict):
    code: Key
    value: Literal["down", "up"]


class ActiveTarget(TypedDict):
    combo_idx: int
    downed_keys: Set[Key]
    target_down: bool


class KeyAlreadyInBuffer(Exception):
    # getting rid of `main.` when throwing this exception, i.e.
    # `main.KeyAlreadyInBuffer` should just be `KeyAlreadyInBuffer`
    # ref: https://stackoverflow.com/a/19419825
    # __module__ = "builtins"
    __module__ = Exception.__module__


@dataclass
class GlobalState:
    buffered_key_down_events: list[BufferedKey]
    # XXX WIP:
    active_targets: list[ActiveTarget]
    # active_targets: list[Combo]
    # combo_state: list[Combo]

    def get_buff_keys_as_keys(self) -> list[Key]:
        return [b["key"] for b in self.buffered_key_down_events]

    def get_buff_keys_as_key_event_list(self) -> list[KeyEvent]:
        return [
            {"code": b["key"], "value": "down"}
            for b in self.buffered_key_down_events
        ]

    def get_down_active_targets_by_key(self, key: Key):
        return [
            at
            for at in self.active_targets
            if at["target_down"] and key in at["downed_keys"]
        ]

    def get_active_targets_by_key(self, key: Key):
        return [at for at in self.active_targets if key in at["downed_keys"]]

    def is_key_pressed(self, key: Key) -> bool:
        down_keys_active_targets = set(
            dk for at in self.active_targets for dk in at["downed_keys"]
        )
        all_buffered_keys = set(k["key"] for k in self.buffered_key_down_events)
        return key in down_keys_active_targets.union(all_buffered_keys)


# XXX: mypy (v0.931) doesn't support `|` yet... 😕
# ResultAction = Tuple[list[KeyEvent], int] | list[KeyEvent] | int | None
ResultAction = Union[Tuple[list[KeyEvent], int], list[KeyEvent], int, None]

# TimeOut = NewType("TimeOut", NoneType)
class TimeOut(Enum):
    TIMEOUT = 0


def key_event_handler(
    config: list[ComboMap],
    # Impossible states can occur :'(
    # e.g. it should be impossible to have incoming that is
    # also in the buffered keys, b/c the buffered keys represent
    # keys that are held down currently
    # -> Can we handle this 'impossible' state somehow?
    incoming: KeyEvent | TimeOut,
    #
    state: GlobalState
    # this param makes sense I think, altho I suppose it is also part of the
    # `state` so maybe I should add it to a big ol' state object
    # buffered_keys: list[Key],
    # buffered_key_down_events: list[BufferedKey],
    # active_targets: list[ActiveTarget],
) -> ResultAction:
    """
    [key event] -> [key_event_handler()]{mutates global `state`} -> [action(s)]
    """
    if isinstance(incoming, TimeOut):
        # We have timed out
        events_to_write = state.get_buff_keys_as_key_event_list()
        state.buffered_key_down_events.clear()
        return events_to_write

    if incoming["value"] == "down":
        return handle_key_down_event(incoming, state, config)

    return handle_key_up_event(incoming, state, config)


def handle_key_down_event(
    incoming: KeyEvent, state: GlobalState, config: list[ComboMap]
) -> ResultAction:
    # Check if down key already in buffer
    if state.is_key_pressed(incoming["code"]):
        # NOTE: Not sure how to handle this currently.
        # this situation shouldn't really occur in practice
        raise KeyAlreadyInBuffer

    possible_combos = get_possible_combos(
        incoming["code"], state.buffered_key_down_events, config
    )
    if len(possible_combos) == 0:
        if len(state.buffered_key_down_events) == 0:
            return [incoming]

        if combo := is_buffer_complete_combo(
            state.buffered_key_down_events, config
        ):
            write_events = activate_target(combo, state)
            return write_events + [incoming]

        # Cache buffered keys
        tmp_buffered_keys = state.get_buff_keys_as_key_event_list()

        # Clear buffer in global state
        state.buffered_key_down_events.clear()

        # Now we check if the incoming key on its own is part of a combo
        # If so, we buffer that one (i.e. will become the combo to
        # 'work' on next)
        if get_possible_combos(
            incoming["code"], state.buffered_key_down_events, config
        ):
            state.buffered_key_down_events.append(
                {"key": incoming["code"], "time_pressed_ns": 123}
            )
            return (tmp_buffered_keys, THRESHOLD_MS)
        return tmp_buffered_keys + [incoming]

    if (
        len(state.buffered_key_down_events) > 0
        and len(possible_combos) == 1
        and is_combo_complete(
            possible_combos[0],
            incoming["code"],
            state.buffered_key_down_events,
        )
    ):
        combo = possible_combos[0]
        return activate_target(combo, state)

    # Append incoming key to buffer and return threshold timer ms
    state.buffered_key_down_events.append(
        {
            "key": incoming["code"],
            "time_pressed_ns": 0,
        }
    )
    return THRESHOLD_MS


def handle_key_up_event(
    incoming: KeyEvent, state: GlobalState, config: list[ComboMap]
) -> ResultAction:
    inc_key = incoming["code"]
    if inc_key in state.get_buff_keys_as_keys():
        # return write all downs + latest up
        to_write = state.get_buff_keys_as_key_event_list()
        # empty buffer
        state.buffered_key_down_events.clear()
        return to_write + [incoming]

    if down_active_targets := state.get_down_active_targets_by_key(inc_key):
        # get the target events
        rel_combos = flatten_2d_seq(
            [
                [cm for cm in config if cm["id"] == x["combo_idx"]]
                for x in down_active_targets
            ]
        )
        # Set down active targets to non-down (by key)
        # XXX: will this use a ref to the dict in global state? I assume so
        for dat in down_active_targets:
            dat["target_down"] = False
            dat["downed_keys"] = set(
                filter(lambda x: x is not inc_key, dat["downed_keys"])
            )
        # Returns these (to be written)
        result: list[KeyEvent] = [
            {"code": tgt_key, "value": "up"}
            for t in rel_combos
            for tgt_key in t["to"]
        ]
        if rel_targets := state.get_active_targets_by_key(inc_key):
            for dat in rel_targets:
                dat["downed_keys"] = set(
                    filter(lambda x: x is not inc_key, dat["downed_keys"])
                )
        # Remove 'empty' targets
        state.active_targets = list(
            filter(lambda at: len(at["downed_keys"]), state.active_targets)
        )
        return result

    if rel_targets := state.get_active_targets_by_key(inc_key):
        for dat in rel_targets:
            dat["downed_keys"] = set(
                filter(lambda x: x is not inc_key, dat["downed_keys"])
            )
        # TODO: add this to others above as well!
        state.active_targets = list(
            filter(lambda at: len(at["downed_keys"]), state.active_targets)
        )
        return None

    return [incoming]


def get_possible_combos(
    incoming_key: Key, buffered_keys: list[BufferedKey], config: list[ComboMap]
) -> list[ComboMap]:
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
    # TODO:
    #   Should we make sure we do not return any combos that are currently in
    #   `state.active_targets`?
    #   Maybe it does not matter?
    bkeys = set(
        bf["key"]
        for bf in buffered_keys + [{"key": incoming_key, "time_pressed_ns": 0}]
    )
    return [
        combo for combo in config if bkeys.issubset(set(combo["activator"]))
    ]


def is_combo_complete(
    combo: ComboMap, incoming_key: Key, buffered_keys: list[BufferedKey]
):
    return set(combo["activator"]) == set(
        [b["key"] for b in buffered_keys] + [incoming_key]
    )


def is_buffer_complete_combo(
    buffered_key_down_events: list[BufferedKey], config: list[ComboMap]
) -> ComboMap | None:
    buff_keys = set(bk["key"] for bk in buffered_key_down_events)
    for cm in config:
        if buff_keys == set(cm["activator"]):
            return cm
    return None


def activate_target(combo: ComboMap, state: GlobalState) -> list[KeyEvent]:
    state.active_targets.append(
        {
            "combo_idx": combo["id"],
            "downed_keys": set(combo["activator"]),
            "target_down": True,
        }
    )
    # Reset buffer
    state.buffered_key_down_events.clear()
    # Return target (to be written out)
    return [{"code": k, "value": "down"} for k in combo["to"]]


def flatten_2d_seq(t: list[list[T]]) -> list[T]:
    return [item for sublist in t for item in sublist]
