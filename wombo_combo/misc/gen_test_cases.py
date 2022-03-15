import random
from itertools import combinations, permutations, product

from wombo_combo.input_event_codes import Key
from wombo_combo.type_hints import ComboMap

CONFIG: list[ComboMap] = [
    ### 0
    {
        "activator": (Key.KEY_J, Key.KEY_K),
        "to": (Key.KEY_ESC,),
    },
    ### 1
    {
        "activator": (Key.KEY_H, Key.KEY_J, Key.KEY_K),
        "to": (Key.KEY_2,),
    },
    ### 2
    {
        "activator": (Key.KEY_S, Key.KEY_D),
        "to": (Key.KEY_F12,),
    },
    ### 3
    {
        "activator": (Key.KEY_U, Key.KEY_J),
        "to": (Key.KEY_TAB,),
    },
]


def main():
    combo_keys = set(a for cm in CONFIG for a in cm["activator"])

    possible_input_key_events = [
        (key, d)
        for key in list(combo_keys) + [Key.KEY_BACKSLASH]
        for d in ["down", "up"]
    ]
    print("len pos inputs:", len(possible_input_key_events))

    all_buffer_perms = []
    for i in range(len(combo_keys)):
        a = permutations(combo_keys, r=i + 1)
        all_buffer_perms += list(a)
    print("all buffer perms len:", len(all_buffer_perms))

    combos_state = [
        x
        for cm in CONFIG
        for r in range(len(cm["activator"]) + 1)
        for x in combinations(cm["activator"], r=r)
    ]
    # [print(i) for i in combos_state]
    print("len combos states:", len(combos_state))

    pp = product(all_buffer_perms, combos_state)
    lpp = list(pp)
    print("len possible States:", len(lpp))

    pip = product(possible_input_key_events, lpp)
    lpip = list(pip)
    print("len all 'possible' inputs to key event handler:", len(lpip))
    print("INPUT EV -- BUFFER -- COMBOS STATE")
    # [print(i) for i in lpip[:10]]
    print("len before filter:", len(lpip))
    lpip = list(
        filter(lambda x: set(x[1][0]).intersection(set(x[1][1])) == set(), lpip)
    )
    print("len after filter:", len(lpip))
    lpip = list(
        filter(
            lambda x: x[0][0] not in set(x[1][0])
            if x[0][1] == "down"
            else True,
            lpip,
        )
    )
    print("len after after filter:", len(lpip))
    lpip = list(
        filter(
            lambda x: not any(
                set(cm["activator"]) in set(x[1][0]) for cm in CONFIG[1:]
            ),
            lpip,
        )
    )
    print("len after after after filter:", len(lpip))

    [print(lpip[i]) for i in random.choices(range(len(lpip)), k=10)]


def main_all():
    possible_input_key_events = [
        (key, d)
        for key in Key
        for d in ["down", "up"]
        if key.value > 0 and key.value < 90
    ]
    print("len pos inputs:", len(possible_input_key_events))

    combo_keys = set(a for cm in CONFIG for a in cm["activator"])

    all_buffer_perms = []
    for i in range(len(combo_keys)):
        a = permutations(combo_keys, r=i + 1)
        all_buffer_perms += list(a)
    print("all buffer perms len:", len(all_buffer_perms))

    combos_state = [
        x
        for cm in CONFIG
        for r in range(len(cm["activator"]) + 1)
        for x in combinations(cm["activator"], r=r)
    ]
    # [print(i) for i in combos_state]
    print("len combos states:", len(combos_state))

    pp = product(all_buffer_perms, combos_state)
    lpp = list(pp)
    print("len possible States:", len(lpp))

    pip = product(possible_input_key_events, lpp)
    lpip = list(pip)
    print("len all 'possible' inputs to key event handler:", len(lpip))
    print("INPUT EV -- BUFFER -- COMBOS STATE")
    # [print(i) for i in lpip[:10]]
    [print(lpip[i]) for i in random.choices(range(len(lpip)), k=10)]


def test_ds():
    state = dict(down_active=["a"], down_timed_out=["b"], down_stale=["c"])
    pass


if __name__ == "__main__":
    main()
