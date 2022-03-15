import itertools
import random
from math import comb

from wombo_combo.input_event_codes import Key
from wombo_combo.type_hints import ComboMap

CONFIG: list[ComboMap] = [
    ### 1
    {
        "activator": (Key.KEY_J, Key.KEY_K),
        "to": (Key.KEY_ESC,),
    },
    ### 2
    {
        "activator": (Key.KEY_H, Key.KEY_J, Key.KEY_K),
        "to": (Key.KEY_2,),
    },
    ### 3
    {
        "activator": (Key.KEY_S, Key.KEY_D),
        "to": (Key.KEY_F12,),
    },
    ### 4
    {
        "activator": (Key.KEY_U, Key.KEY_J),
        "to": (Key.KEY_TAB,),
    },
]


def main():
    keys = [k for idx, k in enumerate(Key) if idx < 70]
    values = ["up", "down"]
    pp = itertools.product(keys, values)
    # for p in pp:
    #     print(p)
    print(len(list(pp)))

    combo_keys = set(
        [
            Key.KEY_J,
            Key.KEY_K,
            Key.KEY_H,
            Key.KEY_S,
            Key.KEY_D,
            Key.KEY_U,
        ]
    )

    random.seed(4)

    buffers = []
    for l in range(1, len(combo_keys) + 1):
        for _ in range(5):
            mc = random.sample(combo_keys, k=l)
            buffers.append(mc)
            print(mc)
        print("*" * 50)

    print(len(buffers))

    for _ in range(5):
        r_idx = random.choice(range(len(CONFIG)))
        r_combo = CONFIG[r_idx]
        for size in range(1, len(r_combo["activator"])):
            ss = random.sample(r_combo["activator"], k=size)
            print(size, r_idx, r_combo, ss)

    # perms = itertools.permutations(combo_keys)
    # print(len(list(perms)))
    # for p in perms:
    #     print(p)

    # combs = itertools.combinations(combo_keys, len(combo_keys))
    # # print(len(list(combs)))
    # for c in combs:
    #     print(c)

    # combs_wr = itertools.combinations_with_replacement(combo_keys, 3)
    # print(len(list(combs_wr)))
    # for c in combs_wr:
    #     print(c)


if __name__ == "__main__":
    main()
