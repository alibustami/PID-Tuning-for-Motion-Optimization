"""This module contains the differential evolution optimizer."""
import os
from datetime import datetime
from functools import lru_cache
from random import randint
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


class DifferentialEvolutionOptimizer:
    """Optimize the PID controller parameters (Kp, Ki, Kd) using Differential Evolution Optimization."""

    def __init__(
        self,
        arduino_connection_object: Serial,
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

        self.results_df = pd.DataFrame(columns=results_columns)
        if not os.path.exists("DE-results"):
            os.makedirs("DE-results")
        self.file_path = os.path.join(
            "DE-results",
            f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_de.csv",
        )

    def constraint_function(self, inputs):
        """TO BE IMPLEMENTED."""
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

    def run(self) -> None:
        """Optimize the PID controller parameters using Differential Evolution Optimization."""
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
            init="random",
            disp=True,
            tol=0.5,
            atol=0.5,
            workers=1,
            maxiter=self.n_iter,
            polish=False,
            func=self.objective_function,
            bounds=list(self.parameters_bounds.values()),
            popsize=2,
            constraints=NonlinearConstraint(
                fun=self.constraint_function,
                lb=lower_constraint_bounds,
                ub=upper_constraint_bounds,
            )
            if self.constraint
            else None,
        )
        print("--------- OPTIMIZATION DONE --------")
        print(self.optimizer.x)
        print(self.optimizer.fun)
        self._run_experiment.cache_clear()

    @lru_cache(maxsize=None)
    def _run_experiment(self, constants: Tuple[int]) -> None:
        """Run the simulation with the given parameters.

        Parameters
        ----------
        constants : Tuple[int]
            Kp, Ki, Kd values, converted to integers.
        """
        # try:
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
