"""This module contains the BayesianOptimizer optimizer class."""
from functools import lru_cache
from typing import Dict, Tuple

from bayes_opt import BayesianOptimization
from scipy.optimize import NonlinearConstraint

from src.scripts.motion_simulation import (
    find_movement_after_applying_pid_controller,
)
from src.utils.helper import (
    calculate_integral_of_squared_error,
    calculate_relative_overshoot,
    calculate_settling_time,
)


class BayesianOptimizer:
    """Optimize the PID controller parameters (Kp, Ki, Kd) using BayesianOptimizer Optimization."""

    def __init__(
        self,
        set_point: float,
        parameters_bounds: Dict[str, Tuple[float, float]],
        constraint: Dict[str, Tuple[float, float]] = None,
        n_iter: int = 50,
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
        self.errors_registery = []

        self._init_optimizer()

    def optimize(self) -> None:
        """Optimize the PID controller parameters using BayesianOptimizer Optimization."""
        self.optimizer.maximize(n_iter=self.n_iter)

        # Clear the cache
        self._run_simulation.cache_clear()

    def constraint_function(self, **inputs):
        """Calculate the constraint values and return them as a tuple.

        Parameters
        ----------
        inputs : Dict[str, float]
            The inputs to the constraint function, which are the PID controller parameters (Kp, Ki, Kd)

        Returns
        -------
        Tuple[float, float]
            The constraint values (overshoot, settling_time)
        """
        kp, ki, kd = inputs["Kp"], inputs["Ki"], inputs["Kd"]
        error_values = self._run_simulation(kp, ki, kd)
        overshoot = calculate_relative_overshoot(error_values)
        settling_time = calculate_settling_time(
            error_values, tolerance=0.1, final_value=self.set_point
        )

        return overshoot, settling_time

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
        error_values = self._run_simulation(kp, ki, kd)
        sum_of_errors = calculate_integral_of_squared_error(error_values)

        return -sum_of_errors

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
    def _run_simulation(self, kp: float, ki: float, kd: float) -> None:
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
        pid_output = find_movement_after_applying_pid_controller(
            kp, ki, kd, set_point=self.set_point
        )
        error_values = [output - self.set_point for output in pid_output]
        return error_values
