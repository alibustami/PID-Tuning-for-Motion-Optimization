"""Utility functions for the project."""

import json
from typing import List, Tuple

# def floats_converter(num: float) -> Tuple[int, int]:
#     dec_len = len(str(num)) - len(str(int(num))) - 1

#     int_num = int(str(num).replace(".", ""))

#     return int_num, max(dec_len, 0)


def load_init_states(json_path: str) -> List[List[float]]:
    """Load the initial states from the given JSON file.

    Parameters
    ----------
    json_path : str
        Path to the JSON file containing the initial states.

    Returns
    -------
    List[List[float]]
        List of initial states.
    """
    with open(json_path, "r") as f:
        init_states = json.load(f)

    init_states_list = []
    for value in init_states.values():
        init_states_list.append(eval(value))

    return init_states_list
