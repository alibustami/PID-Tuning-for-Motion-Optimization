"""Helper functions used in the project."""

import datetime
import os
import struct
import time
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation
from serial import Serial

from src.settings import logger


def calculate_relative_overshoot(
    angle_values: List[float], final_value: float
) -> float:
    """Calculate response overshoot.

    Parameters
    ----------
    angle_values : List[float]
        The angles over tie

    final_value : float
        The desired final value of the system (set point)

    Returns
    -------
    float
        The overshoot
    """
    logger.info(f"Overshoot final value: {final_value}")
    logger.info(f"Overshoot max(angle_values): {max(angle_values)}")

    max_angle = max(angle_values)
    min_angle = min(angle_values)

    if final_value > 0 and max_angle < final_value:
        return -np.inf
    if final_value < 0 and min_angle > final_value:
        return -np.inf

    if final_value > 0:
        max_angle = max(angle_values)
    elif final_value < 0:
        max_angle = min(angle_values)
    else:
        min_angle = min(angle_values)
        max_angle = max(angle_values)
        max_angle = max(abs(max_angle), abs(min_angle))

    difference = abs(max_angle - final_value)
    overshoot = (difference / final_value) * 100
    logger.info(f"difference: {difference}")
    logger.info(f"Overshoot: {overshoot}")
    return overshoot


def calculate_settling_time(
    angle_values: List[float],
    final_value: float,
    tolerance: float = 0.05,
    per_value_time: int = 100,
) -> float:
    """
    Calculate the settling time of a system.

    Parameters
    ----------
    angle_values : List[float]
        The angle values over time.
    final_value : float
        The desired final value of the system (set point).
    tolerance : float, optional
        The tolerance band around the final value (default is 0.05).
    per_value_time : int, optional
        Time per value in milliseconds (default is 100).

    Returns
    -------
    float
        The settling time in milliseconds.
    """
    if not angle_values:
        raise ValueError("angle_values list cannot be empty")

    upper_bound = final_value * (1 + tolerance)
    lower_bound = final_value * (1 - tolerance)

    logger.info(f"Final value: {final_value}, Tolerance: {tolerance}")
    logger.info(f"Tolerance bounds: {lower_bound} to {upper_bound}")

    i = len(angle_values) - 1
    timing = per_value_time * len(angle_values)
    logger.info(f"Timing to be reduced: {timing}")
    while True:
        if angle_values[i] >= lower_bound and angle_values[i] <= upper_bound:
            i -= 1
            timing -= per_value_time
            # logger.info(f"New timing at index {i} => {timing}")
        else:
            break

    logger.info(f"Settling time: {timing} ms")

    return timing


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


def _check_recieving_angles(arduino_connection_object: Serial) -> List[float]:
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
        if len(data_string) < 40:
            logger.info(f"From Arduino: {data_string}")
        if len(data_string) >= 40:
            try:
                angles_data = [
                    float(x) for x in data_string.split(",") if x != ""
                ]
                return angles_data
            except:
                print(
                    f"<_check_recieving_angles> Error in parsing angles data: {data_string}"
                )
    return None


def clear_input_buffer(arduino_connection_object: Serial):
    """Get string object from connection object.

    Parameters
    ----------
    arduino_connection_object : Serial
        The serial object.
    """
    arduino_connection_object.close()
    arduino_connection_object.open()
    time.sleep(2)
    _ = arduino_connection_object.read_all()
    arduino_connection_object.timeout = 2


def check_received_angles(
    arduino_connection_object: Serial,
) -> Tuple[bool, List[float]]:
    """Check if the angles are received from the serial port.

    Parameters
    ----------
    arduino_connection_object : Serial
        The serial object.

    Returns
    -------
    Tuple[bool, List[float]]
        The status of the received angles and the angles data.
    """
    recv_status = False
    angles_data = []
    data_string = (
        arduino_connection_object.read_until().decode("utf-8").strip()
    )

    if len(data_string) > 80:
        try:
            angles_data = [
                float(angle) for angle in data_string.split(";") if angle != ""
            ]
            recv_status = True
            arduino_connection_object.write(bytes("angles received", "utf-8"))
        except:
            recv_status = False
    else:
        # logger.info(f"in exp got >>> {data_string}")
        pass

    return recv_status, angles_data


def start_experimental_run_on_robot(
    arduino_connection_object: Serial,
    constants: Tuple[int],
    run_time: int,
    dump_rate: int,
) -> None:
    """Start the experimental run on the robot.

    Parameters
    ----------
    arduino_connection_object : Serial
        The serial object.
    constants : Tuple[int]
        Kp, Ki, Kd values, converted to integers.
    run_time : int
        The run time (ms).
    dump_rate : int
        The dump rate (ms).
    """
    send_succ = False
    recv_succ = False

    kp, ki, kd = constants

    values = [kp, ki, kd, run_time, dump_rate]
    packed_values = struct.pack("f" * len(values), *values)

    clear_input_buffer(arduino_connection_object)

    while not send_succ:
        # arduino_connection_object.write(bytes(values, "utf-8"))
        arduino_connection_object.write(packed_values)
        time.sleep(0.05)
        logger.info(f"values sent to arduino >> {values}")
        # while "params done" != status:
        status = arduino_connection_object.read_until().decode("utf-8").strip()
        logger.info(f"got from arduino >>> {status}")
        send_succ = True if "done" in status else False
        # if send_succ:
        #     arduino_connection_object.write(bytes("params", "utf-8"))

    while not recv_succ:
        recv_succ, angles_data = check_received_angles(
            arduino_connection_object
        )
        time.sleep(0.05)
        if recv_succ:
            logger.info(f">>> Angles data recieved: {angles_data}")
            plt.clf()
            plt.axhline(y=90, color="r", linestyle="--", label="Set Point")
            plt.plot(
                [i for i in range(len(angles_data))], angles_data, color="b"
            )
            plt.ylabel("IMU")
            plt.xticks()
            plt.yticks()
            plt.show(block=False)
            plt.savefig(f"deo_logs/{datetime.datetime.now()}.png")
            plt.pause(5)
            return angles_data

    # except Exception as e:
    #     logger.error(f"Error in <start_experimental_run_on_robot>: {e}")
    #     return None


def log_optimizaer_data(
    angles: List[float],
    pid_ks: Dict["str", float],
    trial_id: int,
    file_path: str,
):
    """Log the optimizer data to a CSV file. If the file exists, append the data to it."""
    if not os.path.exists(file_path):
        df = pd.DataFrame(
            {
                "trial_id": trial_id,
                "angles": angles,
                # "errors": errors,
                "kp": pid_ks["kp"],
                "ki": pid_ks["ki"],
                "kd": pid_ks["kd"],
            }
        )
        df.to_csv(file_path, index=False)
    else:
        df = pd.read_csv(file_path)
        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    {
                        "trial_id": trial_id,
                        "angles": angles,
                        # "errors": errors,
                        "kp": pid_ks["kp"],
                        "ki": pid_ks["ki"],
                        "kd": pid_ks["kd"],
                    }
                ),
            ]
        )
        df.to_csv(file_path, index=False)
