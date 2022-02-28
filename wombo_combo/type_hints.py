from dataclasses import dataclass
from enum import Enum
from typing import Literal, Set, Tuple, TypedDict, TypeVar, Union

from wombo_combo.input_event_codes import Key

################################################################################
# Type Var
################################################################################
T = TypeVar("T")

################################################################################
# Typed Dict
################################################################################
class BufferedKey(TypedDict):
    key: Key
    time_pressed_ns: int


class ComboMap(TypedDict):
    activator: list[Key]
    to: list[Key]


class KeyEvent(TypedDict):
    code: Key
    value: Literal["down", "up"]


class ActiveTarget(TypedDict):
    combo_idx: int
    downed_keys: Set[Key]
    target_down: bool


################################################################################
# Dataclass
################################################################################
@dataclass
class BaseCombo:
    id: int
    source: list[Key]
    target: list[Key]


@dataclass
class IdleCombo(BaseCombo):
    state: None

    def to_active_combo(self):
        return ActiveCombo(
            id=self.id,
            source=self.source,
            target=self.target,
            state=set(self.source),
        )


@dataclass
class ActiveCombo(BaseCombo):
    state: Set[Key]

    # active_keys: Set[Key] | None
    @property
    def is_fully_down(self) -> bool:
        return self.state == set(self.source)

    def to_idle_combo(self) -> IdleCombo:
        return IdleCombo(
            id=self.id, source=self.source, target=self.target, state=None
        )


################################################################################
# Exception
################################################################################
class KeyAlreadyPressed(Exception):
    # Getting rid of `main.` when throwing this exception, i.e.
    # `main.KeyAlreadyInBuffer` should just be `KeyAlreadyInBuffer`
    # ref: https://stackoverflow.com/a/19419825
    # __module__ = "builtins"
    __module__ = Exception.__module__


################################################################################
# Type Alias
################################################################################
Combos = list[ActiveCombo | IdleCombo]

# NOTE: mypy (v0.931) doesn't support `|` yet when defining type aliases... 😕
# ResultAction = Tuple[list[KeyEvent], int] | list[KeyEvent] | int | None
ResultAction = Union[Tuple[list[KeyEvent], int], list[KeyEvent], int, None]


################################################################################
# Enum
################################################################################
class TimeOut(Enum):
    TIMEOUT = 0
