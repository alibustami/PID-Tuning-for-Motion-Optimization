"""This module contains the motion simulation script."""
import numpy as np
from matplotlib import pyplot as plt


def create_random_movement() -> np.ndarray:
    """Create a random movement of the robot arm.

    Returns
    -------
    np.ndarray
        The random movement.
    """
    movement_simulation_data = np.random.uniform(-np.pi, np.pi, size=1000)
    ## Add noise
    movement_simulation_data = np.random.normal(movement_simulation_data, 2)
    return movement_simulation_data


def plot_movement(movement: np.ndarray) -> None:
    """Plot the movement of the robot arm.

    Parameters
    ----------
    movement : np.ndarray
        The movement of the robot arm.
    """
    plt.plot(movement)
    plt.title("Movement")
    plt.show()


def find_movement_after_applying_pid_controller(
    kp: float, ki: float, kd: float, set_point: float
) -> np.ndarray:
    """Find the movement of the robot arm after applying a PID controller.

    Returns
    -------
    np.ndarray
        The movement of the robot arm after applying a PID controller.
    """
    intial_value = 50
    output = []
    output.append(intial_value)
    integral = 0
    derivative = 0
    previous_error = 0
    for i in range(1, 1500):
        error = set_point - output[i - 1]
        integral = integral + error
        derivative = error - previous_error
        u = kp * error + ki * integral + kd * derivative
        planet_function_output = np.round(planet_function(u), 10)
        output.append(planet_function_output)

        previous_error = error

    return output


def planet_function(u: float) -> np.ndarray:
    """Return the planet function results given the PID controller output.

    Parameters
    ----------
    u : float
        The u value.


    Returns
    -------
    np.ndarray
        The planet function.
    """
    # return u + 2*u + 1
    return (90 * np.sin(u)) + 1  # + 2 * np.sin(u) + 1


def plot_movement_after_applying_pid_controller(
    movement: np.ndarray, pid_output: np.ndarray
) -> None:
    """Plot the movement of the robot arm after applying a PID controller.

    Parameters
    ----------
    movement : np.ndarray
        The movement of the robot arm.
    pid_output : np.ndarray
        The movement of the robot arm after applying a PID controller.
    """
    plt.plot(movement, label="Movement")
    plt.plot(pid_output, label="PID output")
    plt.legend()
    plt.title("Movement after applying PID controller")
    plt.show()
