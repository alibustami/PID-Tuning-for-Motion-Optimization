"""This module contains the BayesianOptimizer optimizer class."""

import os
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, OrderedDict, Tuple, Union

import pandas as pd
from bayes_opt import BayesianOptimization
from scipy.optimize import NonlinearConstraint
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
from src.utils.utils_funcs import load_init_states


class BayesianOptimizer:
    """Optimize the PID controller parameters (Kp, Ki, Kd) using BayesianOptimizer Optimization."""

    def __init__(
        self,
        set_point: float,
        selected_init_state: int,
        parameters_bounds: Dict[str, Tuple[float, float]],
        constraint: OrderedDict[str, Tuple[float, float]] = None,
        n_iter: int = 50,
        experiment_total_run_time: int = 10000,
        experiment_values_dump_rate: int = 100,
        arduino_connection_object: Serial = None,
    ):
        """Initialize the optimizer.

        Parameters
        ----------
        set_point : float
            The set point of the system, which is the desired value of the system.

        parameters_bounds : Dict[str, Tuple[float,  float]]
            The bounds for the PID controller parameters (Kp, Ki, Kd)

        constraints : Dict[str, Tuple[float,  float]], optional
            The constraints for the PID controller, by default None

        n_iter : int, optional
            The number of iterations to run the optimizer, by default 50
        """
        self.set_point = set_point
        self.parameters_bounds = parameters_bounds
        self.constraint = constraint
        self.n_iter = n_iter
        self.experiment_id = 1
        self.experiment_total_run_time = experiment_total_run_time
        self.experiment_values_dump_rate = experiment_values_dump_rate
        self.arduino_connection_object = arduino_connection_object

        init_states = load_init_states("init_states.json")
        self.init_state = init_states[selected_init_state]

        self._init_optimizer()

        self.results_df = pd.DataFrame(columns=results_columns)
        if not os.path.exists("BO-results"):
            os.makedirs("BO-results")
        self.file_path = os.path.join(
            "BO-results",
            f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_init_{selected_init_state}_bo.csv",
        )

    def run(self) -> None:
        """Optimize the PID controller parameters using BayesianOptimizer Optimization."""
        self.optimizer.probe(
            params={
                "Kp": self.init_state[0],
                "Ki": self.init_state[1],
                "Kd": self.init_state[2],
            },
            lazy=True,
        )
        self.optimizer.maximize(n_iter=self.n_iter, init_points=2)

        print(self.optimizer.max)

    def constraint_function(self, **inputs):
        """Calculate the constraint values and return them as a tuple.

        Parameters
        ----------
        inputs : Dict[str, float]
            The inputs to the constraint function, which are the PID controller parameters (Kp, Ki, Kd)

        Returns
        -------
        Tuple[float, float]
            The constraint values (overshoot, raise_time)
        """
        kp, ki, kd = inputs["Kp"], inputs["Ki"], inputs["Kd"]
        error_values, angles_data = self._run_experiment((kp, ki, kd))
        overshoot = calculate_relative_overshoot(angles_data, self.set_point)
        raise_time = calculate_rise_time(angles_data, self.set_point)

        return overshoot, raise_time

    def objective_function(self, **inputs):
        """Calculate the objective value and return it.

        Parameters
        ----------
        inputs : Dict[str, float]
            The inputs to the objective function, which are the PID controller parameters (Kp, Ki, Kd)

        Returns
        -------
        float
            The objective value, which is the negative of the sum of the integral of the squared error over time
        """
        kp, ki, kd = inputs["Kp"], inputs["Ki"], inputs["Kd"]
        error_values, angles_data = self._run_experiment((kp, ki, kd))
        settling_time = calculate_settling_time(
            angles_data, tolerance=0.05, final_value=self.set_point
        )
        overshoot = calculate_relative_overshoot(angles_data, self.set_point)
        rise_time = calculate_rise_time(angles_data, self.set_point)

        self.log_trial_results(
            kp=kp,
            ki=ki,
            kd=kd,
            overshoot=overshoot,
            rise_time=rise_time,
            settling_time=settling_time,
            angle_values=angles_data,
            set_point=self.set_point,
        )

        return -settling_time

    def _init_optimizer(self) -> None:
        """Initialize the optimizer."""
        lower_constraint_bounds = [
            self.constraint[constraint_name][0]
            for constraint_name in self.constraint
        ]
        upper_constraint_bounds = [
            self.constraint[constraint_name][1]
            for constraint_name in self.constraint
        ]
        constraint_model = NonlinearConstraint(
            fun=self.constraint_function,
            lb=lower_constraint_bounds,
            ub=upper_constraint_bounds,
        )
        self.optimizer = BayesianOptimization(
            f=self.objective_function,
            pbounds=self.parameters_bounds,
            constraint=constraint_model,
            verbose=2,
        )

    @lru_cache(maxsize=None)
    def _run_experiment(self, constants: Tuple[int]) -> None:
        """Run the simulation with the given parameters.

        Parameters
        ----------
        constants : Tuple[int]
            Kp, Ki, Kd values, converted to integers.
        """
        # try:
        response_data: Union[List[float], None] = (
            start_experimental_run_on_robot(
                arduino_connection_object=self.arduino_connection_object,
                constants=constants,
                run_time=self.experiment_total_run_time,
                dump_rate=self.experiment_values_dump_rate,
            )
        )
        error_values = [output - self.set_point for output in response_data]
        # log_optimizaer_data(
        #     experiment_id=self.experiment_id,
        #     angles=response_data,
        #     pid_ks=pid_ks,
        #     file_path=f"deo_logs/result_{self.experiment_id}.csv",
        # )
        self.experiment_id += 1
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
