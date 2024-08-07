"""This module contains the BayesianOptimizer optimizer class."""

import os
import sys
import time
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, OrderedDict, Tuple, Union

import pandas as pd
from bayes_opt import BayesianOptimization
from bayes_opt.acquisition import ExpectedImprovement
from bayes_opt.event import Events
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
        objective_value_limit_early_stop: int,
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

        self.selected_init_state = selected_init_state
        init_states = load_init_states("init_states.json")
        self.init_state = init_states[selected_init_state]
        self.objective_value_limit_early_stop = (
            objective_value_limit_early_stop
        )

        self._init_optimizer()

        self.results_df = pd.DataFrame(columns=results_columns)
        if not os.path.exists("BO-results"):
            os.makedirs("BO-results")
        self.file_path = os.path.join(
            "BO-results",
            f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_init_{selected_init_state}_bo.csv",
        )
        self.trials_counter = 0

    def run(self, exp_start_time: float) -> None:
        """Optimize the PID controller parameters using BayesianOptimizer Optimization."""
        self.exp_start_time = exp_start_time
        self.optimizer.probe(
            params={
                "Kp": self.init_state[0],
                "Ki": self.init_state[1],
                "Kd": self.init_state[2],
            },
            lazy=True,
        )
        self.optimizer.maximize(n_iter=self.n_iter, init_points=20)

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
        self.trials_counter += 1
        logger.info(f"Trial {self.trials_counter} started")
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
        _, angles_data = self._run_experiment((kp, ki, kd))
        settling_time = calculate_settling_time(
            angles_data, tolerance=0.05, final_value=self.set_point
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
        acquisition_function = ExpectedImprovement(xi=2)
        self.optimizer = BayesianOptimization(
            f=self.objective_function,
            pbounds=self.parameters_bounds,
            constraint=constraint_model,
            verbose=2,
            acquisition_function=acquisition_function,
        )
        self.optimizer.subscribe(
            event=Events.OPTIMIZATION_STEP,
            subscriber="logger",
            callback=self.results_callback,
        )

    def results_callback(self, event, x):
        """Call back function to log the results of the optimization."""
        print(
            "------------------------------- Results Callback -------------------------------"
        )
        if "optimization:step" != event:
            return
        if not x.res[-1]["allowed"]:
            return

        kp = x.res[-1]["params"]["Kp"]
        ki = x.res[-1]["params"]["Ki"]
        kd = x.res[-1]["params"]["Kd"]

        _, angle_values = self._run_experiment((kp, ki, kd))
        settling_time = calculate_settling_time(
            angle_values, tolerance=0.05, final_value=self.set_point
        )
        overshoot = calculate_relative_overshoot(angle_values, self.set_point)
        rise_time = calculate_rise_time(angle_values, self.set_point)

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

        if settling_time <= self.objective_value_limit_early_stop:
            self.finalize(x, settling_time)
            sys.exit()

    def finalize(self, x, settling_time):
        exp_end_time = time.time()
        total_exp_time = exp_end_time - self.exp_start_time
        txt_file_path = os.path.join(
            "BO-results",
            f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_init_{self.selected_init_state}_bo.txt",
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
            "x": x.max["params"],
            "settling_time": settling_time,
        }

        with open(txt_file_path, "w") as file:
            file.write(str(results_summery))

        print("--------- OPTIMIZATION DONE --------")
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
        # self.experiment_id += 1
        self.results_df.to_csv(self.file_path, index=False)
