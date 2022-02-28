from main import (BufferedKey, ComboMap, Key, flatten_2d_seq,
                  get_possible_combos)

complex_config = dict(
    simul_combos=[
        dict(
            activator=[Key.KEY_J, Key.KEY_K],
            to=[Key.KEY_ESC],
            from_ordering=False,
        )
    ],
    chord_combos=[
        dict(
            activator=[Key.KEY_S, Key.KEY_D],
            chord_layer_map=[
                dict(from_=Key.KEY_H, to=Key.KEY_LEFT),
                dict(from_=Key.KEY_J, to=Key.KEY_DOWN),
                dict(from_=Key.KEY_K, to=Key.KEY_UP),
                dict(from_=Key.KEY_L, to=Key.KEY_RIGHT),
            ],
            activator_ordering=False,
        )
    ],
)

# Let's forget about chording for now
simple_config: list[ComboMap] = [
    {
        "id": 0,
        "activator": [Key.KEY_J, Key.KEY_K],
        "to": [Key.KEY_ESC],
    },
    {
        "id": 1,
        "activator": [Key.KEY_H, Key.KEY_J, Key.KEY_K],
        "to": [Key.KEY_2],
    },
    {
        "id": 2,
        "activator": [Key.KEY_S, Key.KEY_D],
        "to": [Key.KEY_F12],
    },
]


COMBO_KEYS = set(flatten_2d_seq([c["activator"] for c in simple_config]))


# Verify the config actually makes sense
# TODO
# see `notes.md` for the rules

sample_input = dict(
    # type: list of dict, each dict a mapping from combo keys to
    # some key or keys
    config=simple_config,
    # type: (immutable) Key ENUM value | None # None if timeout instead of key
    incoming_key=Key.KEY_R,
    # The keys we have received and buffered/swallowed thusfar
    # i.e. part of a combo (or combos) we are progressing with
    # type: mutable set/hashmap of key enum values
    buffered_keys=[
        dict(
            key=Key.KEY_J,
            time_pressed_ns=123123123,
        )
    ],
    # XXX: if we're using this one we don't need `combos_state` I think
    in_progress_combos_indices=[0, 1],
    # The state of all combos in progress:
    # (or all combos with their respective state? might be irrelevant info)
    # type: mutable reference to global state
    combos_state=[
        dict(
            # A way to uniquely refer to a combo
            idx=0,
            # For combos with more than 2 'activator/from' keys
            # i.e. for each subsequent combo key after the first one we can
            # quickly second the current time in ms is still within the
            # threshold we wanted
            # type: int | None
            timer_start_unix_ms=1612341234,  # making make `ns` because we get ns from `time.time_ns()` anyway?
            timer_expiry_ms=1623452345,  # to easily know the expiry, used to set the remaining threshold timeout time for `select`
            # Listing keys still avails in the combo
            remaining_key={Key.KEY_L, Key.KEY_K},
        ),
    ],
)

#   |    |    |    |    |    |    |    |
#   |    |    |    |    |    |    |    |
#  ---  going through event handler fn ----
#   |    |    |    |    |    |    |    |
#   v    v    v    v    v    v    v    v

# What should we do... Write some keys? Set a timeout?
sample_output = dict(
    # Type: immutable list of keys to write (in order of list) | int (ms timeout) or None (no action)
    # type: list[Key] | int | None
    action=[Key.KEY_J, Key.KEY_R]
)

if __name__ == "__main__":
    config = simple_config
    buffered_keys: list[BufferedKey] = [
        {"key": Key.KEY_J, "time_pressed_ns": 1}
    ]
    incoming_key = Key.KEY_D
    #
    print(f"config:")
    [print(f"\t{i}") for i in config]
    print(f"buffered keys:")
    [print(f"\t{i}") for i in buffered_keys]
    print(f"Incoming key: {incoming_key}")
    #
    # o = get_possible_combo_keys(buffered_keys, config)
    # print(o)
    #
    p = get_possible_combos(incoming_key, buffered_keys, config)
    print("Possible combos:")
    [print(f"\t{i}") for i in p]

################################################################################
# MISC (todo: review)
################################################################################
# if len(state.buffered_key_down_events) == 0:
#     # The relatively straightforward case:
#     state.buffered_key_down_events.append(
#         {
#             "key": incoming["code"],
#             "time_pressed_ns": 123,
#         }
#     )
#     return THRESHOLD_MS
# else:
# restrict to all combos that include buffered keys
# and the incoming key
# (we have already established there is at least one)
# if there is just one, we got a combo to execute
#   so we sent that target's `to` keys
# if there are 2 or more:
#   if all the still have 2 or more keys to go to complete:
#       we add incoming to buffered keys
#       we return threshold timeout - (already elapsed time)
#   if there's one that is complete but there's a superset
#       combo also stil possible:
#       we need to set a timer for the complete one:
#           if this timer expires that completely combo needs
#           to be written
#       we need to add incoming to buffered keys I think
# possible_combos = get_possible_combos(
#     incoming["code"], buffered_key_down_events, config
# )

# else:
#     # XXX: should prolly return adjust threshold ms
#     # something like:
#     # min(5, THRESHOLD_MS - (now_ms - last_buf_key.time_ms))
#     # `min(x,y)` bc negative is impossible and 5ms really
#     # small enough, could even allow 10ms I think
#     state.buffered_key_down_events.append(
#         {"key": incoming["code"], "time_pressed_ns": 1}
#     )
#     return THRESHOLD_MS

# else:
#     # NOTE: >= 1 buffered keys here
#     # Handle subset combo is done, superset still possible
#     # e.g. h,j,k and j,k -> buffer k -> j down incoming
#     print("MORE THAN 1 POSSIBLE COMBO!!")
#     print(f"state: {state}")
#     print(f"incoming: {incoming}")
#     [print(p) for p in possible_combos]
#     pass


# def combos_to_complete(new_key: Key, combos_state: list[dict]):
#     return None

# def are_done(buffered):
#     # activator=[Key.KEY_J, Key.KEY_K],
#     in_progress = [
#         c
#         for c in simple_config
#         if any(act in buffered for act in c["activator"])
#     ]
#     [print(i) for i in in_progress]
#     return in_progress


# def get_possible_combo_keys(
#     buffered_keys: list[BufferedKey],
#     config: list[ComboMap],
# ) -> Set[Key]:
#     if buffered_keys == []:
#         return COMBO_KEYS
#     # TODO: make nicer!
#     buff_keys: Set[Key] = set([bf["key"] for bf in buffered_keys])
#     a = [
#         set(cm["activator"]) - buff_keys
#         for cm in config
#         if buff_keys.issubset(set(cm["activator"]))
#     ]
#     b = set(k for x in a for k in x)
#     return b
