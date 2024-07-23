"""This module contains the differential evolution optimizer."""
import json
import os
import sys
import time
from datetime import datetime
from functools import lru_cache
from random import randint, random
from typing import Dict, List, OrderedDict, Tuple, Union

import numpy as np
import pandas as pd
from scipy.optimize import NonlinearConstraint, differential_evolution
from serial import Serial

from src.scripts.motion_simulation import (
    find_movement_after_applying_pid_controller,
)
from src.settings import logger
from src.utils.helper import (
    calculate_integral_of_squared_error,
    calculate_relative_overshoot,
    calculate_rise_time,
    calculate_settling_time,
    log_optimizaer_data,
    results_columns,
    start_experimental_run_on_robot,
)
from src.utils.utils_funcs import load_init_states, monitor_resources


class DifferentialEvolutionOptimizer:
    """Optimize the PID controller parameters (Kp, Ki, Kd) using Differential Evolution Optimization."""

    def __init__(
        self,
        arduino_connection_object: Serial,
        selected_init_state: int,
        objective_value_limit_early_stop: int,
        parameters_bounds: Dict[str, Tuple[float, float]],
        constraint: OrderedDict[str, Tuple[float, float]] = None,
        n_iter: int = 50,
        experiment_total_run_time: int = 10000,
        experiment_values_dump_rate: int = 100,
        set_point: float = 90,
    ):
        """Initialize the optimizer.

        Parameters
        ----------
        parameters_bounds : Dict[str, Tuple[float,  float]]
            The bounds for the PID controller parameters (Kp, Ki, Kd)

        constraints : Dict[str, Tuple[float,  float]], optional
            The constraints for the PID controller, by default None

        n_iter : int, optional
            The number of iterations to run the optimizer, by default 50

        experiment_total_run_time : int, optional
            The total time to run the experiment, by default 10000

        experiment_values_dump_rate : int, optional
            The rate at which the values are dumped, by default 100

        set_point : float, optional
            The desired angle value, by default 90
        """
        self.parameters_bounds = parameters_bounds
        self.constraint = constraint
        self.n_iter = n_iter
        self.errors_registery = []
        self.arduino_connection_object = arduino_connection_object
        self.experiment_total_run_time = experiment_total_run_time
        self.experiment_values_dump_rate = experiment_values_dump_rate
        self.set_point = set_point
        self.experiment_id = 1
        self.selected_init_state = selected_init_state
        self.objective_value_limit_early_stop = (
            objective_value_limit_early_stop
        )

        init_states = load_init_states("init_states.json")
        self.init_state = init_states[selected_init_state]

        self.results_df = pd.DataFrame(columns=results_columns)
        if not os.path.exists("DE-results"):
            os.makedirs("DE-results")
        self.file_path = os.path.join(
            "DE-results",
            f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_init_{selected_init_state}_de.csv",
        )
        self.trials_counter = 0

    def constraint_function(self, inputs):
        """TO BE IMPLEMENTED."""
        self.trials_counter += 1
        kp, ki, kd = inputs[0], inputs[1], inputs[2]

        # self.set_point = 0
        # while 0 == self.set_point:
        #     self.set_point = randint(-180, 180)

        logger.info("=" * 35)
        logger.info("Start running experiment in <constraint_function>.")
        error_values, angle_values = self._run_experiment((kp, ki, kd))
        logger.info(
            "End running experiment in <constraint_function>; Error values:"
        )
        logger.info(f"error values in constraint_function: {error_values}")
        overshoot = calculate_relative_overshoot(
            angle_values, final_value=self.set_point
        )
        rise_time = calculate_rise_time(angle_values, set_point=self.set_point)
        logger.info(f"Overshoot: {overshoot}")
        retrun_array = np.array([overshoot, rise_time])
        return retrun_array

    def objective_function(self, inputs):
        """TO BE IMPLEMENTED."""
        kp, ki, kd = inputs[0], inputs[1], inputs[2]

        # self.set_point = 0
        # while 0 == self.set_point:
        #     self.set_point = randint(-180, 180)

        logger.info("-" * 35)
        logger.info("Start running experiment in <objective_function>.")
        error_values, angle_values = self._run_experiment((kp, ki, kd))
        settling_time = calculate_settling_time(
            angle_values, tolerance=0.05, final_value=self.set_point
        )
        overshoot = calculate_relative_overshoot(
            angle_values, final_value=self.set_point
        )
        rise_time = calculate_rise_time(angle_values, set_point=self.set_point)
        self.log_trial_results(
            kp=kp,
            ki=ki,
            kd=kd,
            overshoot=overshoot,
            rise_time=rise_time,
            settling_time=settling_time,
            angle_values=angle_values,
            set_point=self.set_point,
        )

        return settling_time

    # @monitor_resources
    def run(self, exp_start_time: float) -> None:
        """Optimize the PID controller parameters using Differential Evolution Optimization."""
        self.exp_start_time = exp_start_time
        lower_constraint_bounds = [
            self.constraint[constraint_name][0]
            for constraint_name in self.constraint
        ]
        upper_constraint_bounds = [
            self.constraint[constraint_name][1]
            for constraint_name in self.constraint
        ]

        logger.info("Start running optimizer...")
        logger.info(
            f"lower_constraint_bounds {lower_constraint_bounds}   -- upper_constraint_bounds {upper_constraint_bounds}"
        )

        self.optimizer = differential_evolution(
            init=np.array(
                [
                    self.init_state,
                    [
                        randint(1, 25),
                        randint(0, 100) / 100,
                        randint(0, 100) / 100,
                    ],
                    [
                        randint(1, 25),
                        randint(0, 100) / 100,
                        randint(0, 100) / 100,
                    ],
                    [
                        randint(1, 25),
                        randint(0, 100) / 100,
                        randint(0, 100) / 100,
                    ],
                    [
                        randint(1, 25),
                        randint(0, 100) / 100,
                        randint(0, 100) / 100,
                    ],
                ],
                dtype=np.float32,
            ),
            disp=True,
            tol=0,
            atol=0,
            workers=1,
            maxiter=self.n_iter,
            polish=False,
            func=self.objective_function,
            bounds=list(self.parameters_bounds.values()),
            popsize=2,
            constraints=(
                NonlinearConstraint(
                    fun=self.constraint_function,
                    lb=lower_constraint_bounds,
                    ub=upper_constraint_bounds,
                )
                if self.constraint
                else None
            ),
            callback=self.results_callback,
        )
        self.finalize(self.optimizer.x, self.optimizer.fun)

    def results_callback(self, x, convergence):
        print(
            "------------------------------- Results Callback -------------------------------"
        )
        print(x)

        kp, ki, kd = x
        _, angle_values = self._run_experiment((kp, ki, kd))
        settling_time = calculate_settling_time(
            angle_values, tolerance=0.05, final_value=self.set_point
        )

        if settling_time <= self.objective_value_limit_early_stop:
            self.finalize(x, settling_time)
            sys.exit()

    @lru_cache(maxsize=None)
    def _run_experiment(self, constants: Tuple[int]) -> None:
        """Run the simulation with the given parameters.

        Parameters
        ----------
        constants : Tuple[int]
            Kp, Ki, Kd values, converted to integers.
        """
        response_data: Union[
            List[float], None
        ] = start_experimental_run_on_robot(
            arduino_connection_object=self.arduino_connection_object,
            constants=constants,
            run_time=self.experiment_total_run_time,
            dump_rate=self.experiment_values_dump_rate,
        )
        error_values = [output - self.set_point for output in response_data]

        return error_values, response_data

    def finalize(self, x, settling_time):
        exp_end_time = time.time()
        total_exp_time = exp_end_time - self.exp_start_time
        txt_file_path = os.path.join(
            "DE-results",
            f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_init_{self.selected_init_state}_de.txt",
        )

        # lines = [
        #     str(self.parameters_bounds),
        #     str(self.constraint),
        #     str(self.n_iter),
        #     str(self.experiment_total_run_time),
        #     str(self.experiment_values_dump_rate),
        #     str(self.selected_init_state),
        #     str(self.objective_value_limit_early_stop),
        #     str(total_exp_time),
        #     str(x),
        #     str(settling_time),

        # ]
        results_summery = {
            "parameters_bounds": self.parameters_bounds,
            "constraint": self.constraint,
            "n_iter": self.n_iter,
            "n_trials": self.trials_counter,
            "experiment_total_run_time": self.experiment_total_run_time,
            "experiment_values_dump_rate": self.experiment_values_dump_rate,
            "selected_init_state": self.selected_init_state,
            "objective_value_limit_early_stop": self.objective_value_limit_early_stop,
            "total_exp_time": total_exp_time,
            "x": x,
            "settling_time": settling_time,
        }

        with open(txt_file_path, "w") as file:
            file.write(str(results_summery))


        print("--------- OPTIMIZATION DONE --------")
        self._run_experiment.cache_clear()

    def log_trial_results(
        self,
        kp,
        ki,
        kd,
        overshoot,
        rise_time,
        settling_time,
        angle_values,
        set_point,
    ):
        """Log the results of the trial. Used only in the objective function."""
        self.results_df = pd.concat(
            [
                self.results_df,
                pd.DataFrame(
                    {
                        "experiment_id": self.experiment_id,
                        "kp": kp,
                        "ki": ki,
                        "kd": kd,
                        "overshoot": overshoot,
                        "rise_time": rise_time,
                        "settling_time": settling_time,
                        "angle_values": [angle_values],
                        "set_point": set_point,
                    },
                    index=[0],
                ),
            ],
            ignore_index=True,
        )
        self.experiment_id += 1
        self.results_df.to_csv(self.file_path, index=False)
