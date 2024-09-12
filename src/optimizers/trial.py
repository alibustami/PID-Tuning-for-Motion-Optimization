"""Trail Module."""

import time
from collections import OrderedDict
from random import randint

from serial import Serial

from src.configs import get_config
from src.optimizers.bayesian_optimizer import BayesianOptimizer
from src.optimizers.differential_evolution import (
    DifferentialEvolutionOptimizer,
)
from src.utils.helper import clear_input_buffer

arduino_connection_configs = get_config("arduino_connection")

connection_object = Serial(**arduino_connection_configs)
print("done connecting !")

set_point = get_config("setpoint")

selected_optimizer = get_config("optimizer")
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
    ptimizer = DifferentialEvolutionOptimizer(
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

clear_input_buffer(connection_object)
exp_start_time = time.time()
optimizer.run(exp_start_time=exp_start_time)
