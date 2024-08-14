"""Pydantic schemas for the optimizer results."""

from pathlib import Path
from typing import Any, Optional, Tuple

import pandas as pd
from pydantic import BaseModel, validator


class ParametersBounds(BaseModel):
    """Parameters bounds for the PID controller."""

    Kp: Tuple[float, float]
    Ki: Tuple[float, float]
    Kd: Tuple[float, float]


class Constraint(BaseModel):
    """Constraints for the PID controller."""

    overshoot: Tuple[float, float]
    risetime: Tuple[float, float]


class Gains(BaseModel):
    """PID controller gains."""

    Kp: float
    Ki: float
    Kd: float


class TxtContent(BaseModel):
    """Text content."""

    parameters_bounds: ParametersBounds
    constraint: Constraint
    n_iter: int
    n_trials: int
    experiment_total_run_time: int
    experiment_values_dump_rate: int
    selected_init_state: int
    objective_value_limit_early_stop: float
    total_exp_time: float
    x: Gains
    settling_time: int


class Trial(BaseModel):
    """A single trial."""

    init_0_csv: Any
    init_1_csv: Any
    init_2_csv: Any
    init_3_csv: Any
    init_4_csv: Any
    init_5_csv: Any
    init_0_txt: Optional[TxtContent] = None
    init_1_txt: Optional[TxtContent] = None
    init_2_txt: Optional[TxtContent] = None
    init_3_txt: Optional[TxtContent] = None
    init_4_txt: Optional[TxtContent] = None
    init_5_txt: Optional[TxtContent] = None

    @validator(
        "init_0_csv",
        "init_1_csv",
        "init_2_csv",
        "init_3_csv",
        "init_4_csv",
        "init_5_csv",
        pre=True,
        always=True,
    )
    def validate_csv(cls, v):
        """Validate the CSV file."""
        if not isinstance(v, pd.DataFrame):
            raise ValueError("CSV file must be a pandas DataFrame")
        return v


class Config(BaseModel):
    """A single configuration."""

    trial_1: Trial
    # trial_2: Optional[Trial] = None
    # trial_3: Optional[Trial] = None
    configs_file: Path


class OptimizerResults(BaseModel):
    """Optimizer results."""

    config_1: Config
    config_2: Config
    config_3: Config


class DifferentialEvolutionResults(OptimizerResults):
    """Differential Evolution optimizer results."""

    pass


class BayesianOptimizerResults(OptimizerResults):
    """Bayesian optimizer results."""

    pass
