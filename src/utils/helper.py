"""Helper functions used in the project."""
from typing import List

import numpy as np


def calculate_relative_overshoot(error_values: List[float]) -> float:
    """Calculate the relative overshoot (max_error / 180) of the error over time data.

    Parameters
    ----------
    error_values : List[float]
        The error over time data

    Returns
    -------
    float
        The relative overshoot
    """
    return (max(error_values) / 180) * 100


def calculate_settling_time(
    error_values: List[float], final_value: float = 0, tolerance: float = 0.05
):
    """Calculate the settling time of a system.

    Parameters
    ----------
    error_values : List[float]
        The error values over time
    final_value : float
        The final value of the system
    tolerance : float, optional
        The tolerance, by default 0.05

    Returns
    -------
    int
        The settling time
    """
    for i in range(len(error_values)):
        if all(
            abs(error) < final_value * tolerance for error in error_values[i:]
        ):
            return i
    return len(
        error_values
    )  # If it never settles, return the length of the array


def calculate_integral_of_squared_error(
    error_values: List[float], latest_proportion: float = 0.5
) -> float:
    """Calculate the integral of the squared error over time.

    Parameters
    ----------
    error_values : List[float]
        The error over time data
    latest_proportion : float, optional
        The proportion of the latest error values to consider, by default 0.5

    Returns
    -------
    float
        The integral of the squared error over time
    """
    return np.sum(
        np.square(error_values[-int(len(error_values) * latest_proportion) :])
    )
