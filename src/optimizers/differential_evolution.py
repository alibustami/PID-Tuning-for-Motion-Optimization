"""This module contains the differential evolution optimizer."""
from functools import lru_cache
from typing import Dict, List, OrderedDict, Tuple, Union

from scipy.optimize import NonlinearConstraint, differential_evolution
from serial import Serial

from src.scripts.motion_simulation import (
    find_movement_after_applying_pid_controller,
)
from src.utils.helper import (
    calculate_integral_of_squared_error,
    calculate_relative_overshoot,
    calculate_settling_time,
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

    def constraint_function(self, inputs):
        """TO BE IMPLEMENTED."""
        kp, ki, kd = inputs[0], inputs[1], inputs[2]
        error_values = self._run_experiment(kp, ki, kd)
        overshoot = calculate_relative_overshoot(
            error_values, final_value=self.set_point
        )
        settling_time = calculate_settling_time(
            error_values, tolerance=0.09, final_value=self.set_point
        )
        return overshoot, settling_time

    def objective_function(self, inputs):
        """TO BE IMPLEMENTED."""
        kp, ki, kd = inputs[0], inputs[1], inputs[2]
        error_values = self._run_experiment(kp, ki, kd)
        integral_of_squared_error = calculate_integral_of_squared_error(
            error_values
        )
        return integral_of_squared_error

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
        self.optimizer = differential_evolution(
            disp=True,
            workers=-1,
            maxiter=self.n_iter,
            polish=False,
            func=self.objective_function,
            bounds=list(self.parameters_bounds.values()),
            constraints=NonlinearConstraint(
                fun=self.constraint_function,
                lb=lower_constraint_bounds,
                ub=upper_constraint_bounds,
            )
            if self.constraint
            else None,
        )

        self._run_experiment.cache_clear()

    @lru_cache(maxsize=None)
    def _run_experiment(self, kp: float, ki: float, kd: float) -> None:
        """Run the simulation with the given parameters.

        Parameters
        ----------
        kp : float
            The proportional gain.

        ki : float
            The integral gain.

        kd : float
            The derivative gain.
        """
        try:
            response_data: Union[
                List[float], None
            ] = start_experimental_run_on_robot(
                arduino_connection_object=self.arduino_connection_object,
                kp=kp,
                ki=ki,
                kd=kd,
                run_time=self.experiment_total_run_time,
                dump_rate=self.experiment_values_dump_rate,
            )
            error_values = [
                output - self.set_point for output in response_data
            ]
            return error_values
        except Exception as e:
            print(f"Error in <_run_experiment>: {e}")
            return None
