"""Helper functions used in the project."""
from typing import List

import numpy as np
from serial import Serial

from src.settings import logger


def calculate_relative_overshoot(
    error_values: List[float], final_value: float
) -> float:
    """Calculate response overshoot.

    Parameters
    ----------
    error_values : List[float]
        The error over time data

    final_value : float
        The desired final value of the system (set point)

    Returns
    -------
    float
        The overshoot
    """
    return ((max(error_values) - final_value) / final_value) * 100


def calculate_settling_time(
    error_values: List[float],
    final_value: float,
    tolerance: float = 0.05,
    per_value_time: int = 100,
):
    """Calculate the settling time of a system.

    Parameters
    ----------
    error_values : List[float]
        The error values over time
    final_value : float
        The desired final value of the system (set point)
    tolerance : float, optional
        The tolerance, by default 0.05
    per_value_time : int, optional
        The time between each value, by default 100 ms

    Returns
    -------
    int
        The settling time
    """
    for i in range(len(error_values)):
        if all(
            abs(error) < final_value * tolerance for error in error_values[i:]
        ):
            return i * per_value_time
    return len(error_values) * per_value_time


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


def check_recieving_angles(arduino_connection_object: Serial) -> List[float]:
    """Check if the readings are available from the serial port.

    Parameters
    ----------
    arduino_connection_object : Serial
        The serial object.

    Returns
    -------
    List[float]
        The angles data if available, else None.
    """
    if arduino_connection_object.in_waiting > 0:
        data_string = (
            arduino_connection_object.readline().decode("utf-8").strip()
        )
        angles_data = [float(x) for x in data_string.split(",") if x != ""]
        return angles_data
    return None


def start_experimental_run_on_robot(
    arduino_connection_object: Serial,
    kp: float,
    ki: float,
    kd: float,
    run_time: int,
    dump_rate: int,
) -> None:
    """Start the experimental run on the robot.

    Parameters
    ----------
    arduino_connection_object : Serial
        The serial object.
    kp : float
        The proportional gain.
    ki : float
        The integral gain.
    kd : float
        The derivative gain.
    run_time : int
        The run time (ms).
    dump_rate : int
        The dump rate (ms).
    """
    values = f"{kp} {ki} {kd} {run_time} {dump_rate}\n"
    arduino_connection_object.write(values.encode())

    try:
        while True:
            angles_data = check_recieving_angles(arduino_connection_object)
            if angles_data:
                logger.info(f">>> Angles data recieved: {angles_data}")
                return angles_data
    except Exception as e:
        logger.error(f"Error in <start_experimental_run_on_robot>: {e}")
        return None
