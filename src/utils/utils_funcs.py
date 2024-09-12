"""Utility functions for the project."""

import functools
import json
import threading
import time
from collections import OrderedDict
from random import randint
from typing import List, Tuple, Union

import psutil
from serial import Serial

from src.configs import get_config
from src.optimizers.bayesian_optimizer import BayesianOptimizer
from src.optimizers.differential_evolution import (
    DifferentialEvolutionOptimizer,
)
from src.utils.helper import clear_input_buffer


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
        usage_stats = {"max_cpu": 0, "max_ram": 0}

        def get_usage():
            while not stop_event.is_set():
                usage_stats["max_cpu"] = max(
                    usage_stats["max_cpu"], process.cpu_percent(interval=0.1)
                )
                usage_stats["max_ram"] = max(
                    usage_stats["max_ram"],
                    process.memory_info().rss / (1024 * 1024),
                )
                time.sleep(0.1)

        process.cpu_percent(interval=0.1)

        stop_event = threading.Event()
        monitor_thread = threading.Thread(target=get_usage)
        monitor_thread.start()

        try:
            result = func(*args, usage_stats=usage_stats, **kwargs)
        finally:
            stop_event.set()
            monitor_thread.join()

        return result

    return wrapper


def select_optimizer(
    selected_optimizer: str, connection_object: Serial
) -> Union[DifferentialEvolutionOptimizer, BayesianOptimizer]:
    """Select the optimizer based on the given name.

    Parameters
    ----------
    selected_optimizer : str
        The name of the optimizer to select.
    connection_object : Serial
        The serial connection object to the Arduino.

    Returns
    -------
    Union[DifferentialEvolutionOptimizer, BayesianOptimizer]
        The selected optimizer.
    """
    set_point = get_config("setpoint")
    if "BO" == selected_optimizer:
        optimizer = BayesianOptimizer(
            parameters_bounds={
                "Kp": (
                    get_config("parameters_bounds.kp_lower_bound"),
                    get_config("parameters_bounds.kp_upper_bound"),
                ),
                "Ki": (
                    get_config("parameters_bounds.ki_lower_bound"),
                    get_config("parameters_bounds.ki_upper_bound"),
                ),
                "Kd": (
                    get_config("parameters_bounds.kd_lower_bound"),
                    get_config("parameters_bounds.kd_upper_bound"),
                ),
            },
            constraint=OrderedDict(
                [
                    (
                        "overshoot",
                        (
                            get_config("constraint.overshoot_lower_bound"),
                            get_config("constraint.overshoot_upper_bound"),
                        ),
                    ),
                    (
                        "risetime",
                        (
                            get_config("constraint.rise_time_lower_bound"),
                            get_config("constraint.rise_time_upper_bound"),
                        ),
                    ),
                ]
            ),
            n_iter=get_config("n_iterations"),
            experiment_total_run_time=get_config("experiment_total_run_time"),
            experiment_values_dump_rate=100,
            set_point=set_point,
            arduino_connection_object=connection_object,
            selected_init_state=get_config("init_state"),
            objective_value_limit_early_stop=2500,
            selected_config=get_config("configuration"),
        )
    elif "DE" == selected_optimizer:
        optimizer = DifferentialEvolutionOptimizer(
            parameters_bounds={
                "Kp": (
                    get_config("parameters_bounds.kp_lower_bound"),
                    get_config("parameters_bounds.kp_upper_bound"),
                ),
                "Ki": (
                    get_config("parameters_bounds.ki_lower_bound"),
                    get_config("parameters_bounds.ki_upper_bound"),
                ),
                "Kd": (
                    get_config("parameters_bounds.kd_lower_bound"),
                    get_config("parameters_bounds.kd_upper_bound"),
                ),
            },
            constraint=OrderedDict(
                [
                    (
                        "overshoot",
                        (
                            get_config("constraint.overshoot_lower_bound"),
                            get_config("constraint.overshoot_upper_bound"),
                        ),
                    ),
                    (
                        "risetime",
                        (
                            get_config("constraint.rise_time_lower_bound"),
                            get_config("constraint.rise_time_upper_bound"),
                        ),
                    ),
                ]
            ),
            n_iter=get_config("n_iterations"),
            experiment_total_run_time=get_config("experiment_total_run_time"),
            experiment_values_dump_rate=100,
            set_point=set_point,
            arduino_connection_object=connection_object,
            selected_init_state=get_config("init_state"),
            objective_value_limit_early_stop=2500,
            selected_config=get_config("configuration"),
        )
    else:
        raise ValueError(
            "Invalid optimizer selected, please check configurations.yaml"
        )

    return optimizer
