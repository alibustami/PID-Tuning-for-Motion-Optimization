"""The modes of the robot."""
from interfaces.interfaces import BaseMode
from src.optimizers.bayesian_optimizer import BaeysianOptimizer
from src.settings import logger


class OptimizationMode(BaseMode):
    """Robot focuses on optimizing its movements."""

    def enter(self):
        """Enter this mode."""
        logger.info("Entering Optimization Mode.")

    def exit(self):
        """Exit this mode."""
        print("Exiting Optimization Mode.")

    def execute(self):
        """Execute this mode."""
        logger.info("Executing Optimization Mode.")
        Optimizer = BaeysianOptimizer()
        Optimizer.optimize()


class RunningMode(BaseMode):
    """Robot operates in a in the running mode."""

    def enter(self):
        """Enter this mode."""
        logger.info("Entering Running Mode.")

    def exit(self):
        """Exit this mode."""
        logger.info("Exiting Running Mode.")

    def execute(self):
        """Execute this mode."""
        logger.info("Executing Running Mode.")


class IdleMode(BaseMode):
    """Robot is in a low power state, waiting for user input."""

    def enter(self):
        """Enter this mode."""
        logger.info("Entering Idle Mode.")

    def exit(self):
        """Exit this mode."""
        logger.info("Exiting Idle Mode.")

    def execute(self):
        """Execute this mode."""
        logger.info("Executing Idle Mode.")
