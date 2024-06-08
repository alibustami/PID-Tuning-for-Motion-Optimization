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
        logger.info(f"in exp got >>> {data_string}")

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
            plt.pause(5)
            return angles_data

    # except Exception as e:
    #     logger.error(f"Error in <start_experimental_run_on_robot>: {e}")
    #     return None


def log_optimizaer_data(
    angles: List[float],
    pid_ks: Dict["str", float],
    experiment_id: int,
    file_path: str,
):
    """Log the optimizer data to a CSV file. If the file exists, append the data to it."""
    if not os.path.exists(file_path):
        df = pd.DataFrame(
            {
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
