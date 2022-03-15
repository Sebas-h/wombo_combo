from wombo_combo.input_event_codes import Key
from wombo_combo.type_hints import ComboMap

THRESHOLD_MS = 50
COMBOS: list[ComboMap] = [
    {
        "activator": (Key.KEY_J, Key.KEY_K),
        "to": (Key.KEY_1,),
    },
    {
        "activator": (Key.KEY_H, Key.KEY_J, Key.KEY_K),
        "to": (Key.KEY_2,),
    },
    {
        "activator": (Key.KEY_S, Key.KEY_D),
        "to": (Key.KEY_3,),
    },
    {
        "activator": (Key.KEY_U, Key.KEY_J),
        "to": (Key.KEY_4, Key.KEY_5),
    },
]
