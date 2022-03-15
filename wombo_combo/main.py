from wombo_combo.type_hints import ComboMap, CombosState, IdleCombo
from wombo_combo.config import COMBOS


def main():
    _ = initialize_combos_state(COMBOS)


def initialize_combos_state(config: list[ComboMap]) -> CombosState:
    return [
        IdleCombo(
            id=idx,
            source=combo_map["activator"],
            target=combo_map["to"],
            pressed_keys=None,
        )
        for idx, combo_map in enumerate(config)
    ]


if __name__ == "__main__":
    main()
