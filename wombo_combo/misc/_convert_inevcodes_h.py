import re
from typing import Any, Callable, Iterable, TypeVar

# linux input-event-codes.h
# ref: https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
PATH = "/home/sebas/code/test_files/psuedo-simul/_input-event-codes.h"

PREFIX_ENUM_MAP = {
    "INPUT_PROP_": "InputProp",
    "EV_": "Event",
    "SYN_": "Syn",
    "KEY_": "Key",
    "BTN_": "Key",
    "REL_": "Rel",
    "ABS_": "Abs",
    "SW_": "Sw",
    "MSC_": "Msc",
    "LED_": "Led",
    "REP_": "Rep",
    "SND_": "Snd",
}


def main():
    with open(PATH) as fd:
        lines = fd.readlines()

    cleaned_lines = []
    for line in lines:
        # 1: Remove lines without leading "#define" (exluding the guard) and
        # empty lines
        prog = re.compile(r"^\#define")
        result = prog.match(line)
        if (
            not result
            or "_UAPI_INPUT_EVENT_CODES_H" in line
            or line.strip() == ""
        ):
            continue
        # 2: remove all trailing comments
        if "/*" in line:
            line = re.sub(r"(.*)\/\*.*", r"\1", line)
        # 3: remove the leading `#define`s
        line = line.replace("#define ", "")
        # 4: insert `=` between const name and value
        regex_search_term = r"^([\S]+)(.*)"
        regex_replacement = r"\1=\2"
        line = re.sub(regex_search_term, regex_replacement, line)
        # 5: remove all whitespace
        line = line.replace(" ", "")
        line = line.replace("\t", "")
        # collect lines
        cleaned_lines += [line]

    resolved_lines = []
    # 6: resolves variable assingments
    for line in cleaned_lines:
        m = re.match(r".*=(\D.*)", line)
        if not m:
            resolved_lines += [line]
            continue

        var = m.group(1)

        # 6.1: Simple var replace with its value
        if "(" not in var:
            value_of_var = get_var_value(var, cleaned_lines)
            if value_of_var is None:
                raise ValueError("Did not expect None here!")
            line = line.replace(var, value_of_var)
            resolved_lines += [line]
            continue

        # 6.2: need to evaluate the expression
        expression = var
        var_match = re.match(r"\(([A-Z|_]+).*", expression)
        if var_match is None:
            raise ValueError()
        var = var_match.group(1)
        value_of_var = get_var_value(var, cleaned_lines)
        if value_of_var is None:
            raise ValueError("Did not expect None here!")
        exrpr_value = eval(expression.replace(var, value_of_var))
        line = (
            re.sub(r"(.*=)(\D.*)", r"\1", line).strip()
            + str(exrpr_value)
            + "\n"
        )
        resolved_lines += [line]

    # [DEBUG]: Get prefixes
    # prefixes = get_prefixes(resolved_lines)
    # print("prefixes:", prefixes)

    # 7: Define and verify the Enum classes to add
    # Steps:
    #   for each line in resolved lines:
    #     get the prefix
    #     if it is not in the prefix map -> throw error!
    #     get first and last with this prefix
    #         we assume the come in blocks/sections
    #     indent with 4 spaces
    #     add new line above first prefix line `class [NAME](Enum):`
    changes = []
    seen = set()
    for idx, line in enumerate(resolved_lines):
        pe = first(lambda item: item[0] in line, PREFIX_ENUM_MAP.items())
        if pe is None:
            raise ValueError(
                (
                    "No prefix found for var in line {line}, maybe we need "
                    "to add a new prefix to the prefix enum map..."
                )
            )
        _, enum_name = pe
        if enum_name in seen:
            continue
        seen.add(enum_name)
        changes += [(idx + len(changes), f"class {enum_name}(Enum):\n")]

    # 8: insert the enum classes (and the appropriate indendation )
    resolved_lines = ["    " + line for line in resolved_lines]
    for idx, lta in changes:
        resolved_lines.insert(idx, lta)

    # 9: Add import statement
    resolved_lines = ["from enum import Enum\n"] + resolved_lines

    # Send to stdout
    print("".join(resolved_lines))


T = TypeVar("T")


def first(
    predicate_filter: Callable[[Any], bool], iterable: Iterable[T]
) -> T | None:
    return next(filter(predicate_filter, iterable), None)


def get_var_value(var: str, lines: list[str]) -> str | None:
    line_with_var_value = first(lambda l: f"{var}=" in l, lines)
    if line_with_var_value is None:
        return None
    value_of_var = line_with_var_value.split("=")[1].strip()
    return value_of_var


def get_prefixes(lines: list[str]):
    prefixes = {}
    for idx, line in enumerate(lines):
        splitted = line.split("_")
        if len(splitted) < 1:
            continue
        prefix = splitted[0]
        if prefix not in prefixes.values():
            prefixes[idx] = prefix


if __name__ == "__main__":
    main()
