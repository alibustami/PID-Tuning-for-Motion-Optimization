"""This module contains the Bayesian optimizer class."""
from typing import Dict, Tuple

from bayes_opt import BayesianOptimization


class BaeysianOptimizer:
    """Optimize the PID controller parameters (Kp, Ki, Kd) using Bayesian Optimization."""

    def __init__(
        self,
        parameters_bounds: Dict[str, Tuple[float, float]],
        costraints: Dict[str, Tuple[float, float]] = None,
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
        self.n_iter = n_iter
        self.errors_registery = []

        self._init_optimizer()

    def optimize(self) -> None:
        """Optimize the PID controller parameters using Bayesian Optimization."""
        self.optimizer.maximize(init_points=2, n_iter=3)

    def constraint_function(self, **inputs):
        """TO BE IMPLEMENTED."""
        pass

    def objective_function(self, **inputs):
        """TO BE IMPLEMENTED."""
        pass

    def _init_optimizer(self) -> None:
        """Initialize the optimizer."""
        self.optimizer = BayesianOptimization(
            f=...,
            parameters_bounds=self.parameters_bounds,
            random_state=1,
        )
