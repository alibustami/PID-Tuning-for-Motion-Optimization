"""Utility functions for the project."""

import functools
import json
import time
from typing import List, Tuple

import psutil

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


def monitor_resources(func):
    """Decorate to monitor CPU and RAM usage of a function.

    Parameters
    ----------
    func : function
        The function to monitor

    Returns
    -------
    function
        The wrapped function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process()
        max_cpu = 0
        max_ram = 0

        def get_usage():
            nonlocal max_cpu, max_ram
            max_cpu = max(max_cpu, process.cpu_percent(interval=0.1))
            max_ram = max(max_ram, process.memory_info().rss)

        import threading

        def monitor():
            while not stop_event.is_set():
                get_usage()
                time.sleep(0.1)

        stop_event = threading.Event()
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.start()

        try:
            result = func(*args, **kwargs)
        finally:
            stop_event.set()
            monitor_thread.join()

        max_ram_mb = max_ram / (1024 * 1024)
        return result, max_cpu, max_ram_mb

    return wrapper
