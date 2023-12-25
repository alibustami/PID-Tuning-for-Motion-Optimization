"""This module contains the differential evolution optimizer."""
from functools import lru_cache
from typing import Dict, Tuple

from scipy.optimize import NonlinearConstraint, differential_evolution

from src.scripts.motion_simulation import (
    find_movement_after_applying_pid_controller,
)
from src.utils.helper import (
    calculate_integral_of_squared_error,
    calculate_relative_overshoot,
    calculate_settling_time,
)


class DifferentialEvolutionOptimizer:
    """Optimize the PID controller parameters (Kp, Ki, Kd) using Differential Evolution Optimization."""

    def __init__(
        self,
        parameters_bounds: Dict[str, Tuple[float, float]],
        constraint: Dict[str, Tuple[float, float]] = None,
        n_iter: int = 50,
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
        """
        self.parameters_bounds = parameters_bounds
        self.constraint = constraint
        self.n_iter = n_iter
        self.errors_registery = []

    def constraint_function(self, inputs):
        """TO BE IMPLEMENTED."""
        kp, ki, kd = inputs[0], inputs[1], inputs[2]
        error_values = self._run_simulation(kp, ki, kd)
        overshoot = calculate_relative_overshoot(error_values)
        settling_time = calculate_settling_time(
            error_values, tolerance=0.08, final_value=90
        )
        return overshoot, settling_time

    def objective_function(self, inputs):
        """TO BE IMPLEMENTED."""
        kp, ki, kd = inputs[0], inputs[1], inputs[2]
        error_values = self._run_simulation(kp, ki, kd)
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

        self._run_simulation.cache_clear()

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
        ## Send commands to the controller
        ## Run the simulation
        ## Get the errors
        set_point = 90
        pid_output = find_movement_after_applying_pid_controller(
            kp, ki, kd, set_point=set_point
        )
        error_values = [output - set_point for output in pid_output]
        return error_values
