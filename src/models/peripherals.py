"""Models for the Jetson Nano peripheral devices.""" ""
from typing import Dict, List

from Jetson.GPIO import GPIO

from interfaces.interfaces import BasePeripheral, BasePeripheralParameters
from src.settings import logger


class PeripheralsManager:
    """Manage the prepheral models."""

    def __init__(self, peripherals: Dict[str, BasePeripheral]):
        """Initialize the prepheral models.

        Parameters
        ----------
        peripherals : Dict[str, BasePeripheral]
            The prepheral models. keys are the names of the prepheral based on the user preference. values are the prepheral models.
        """
        self._peripherals = peripherals
        self._peripherals_last_read_data_registery = {
            peripheral_name: None
            for peripheral_name in self._peripherals.keys()
        }

    def read_data(self, prepheral_name: str):
        """Read data from a specific prepheral.

        Parameters
        ----------
        prepheral_name : str
            The name of the prepheral.

        Returns
        -------
        str
            The data read from the prepheral.
        """
        if prepheral_name not in self._peripherals:
            logger.error(
                f"<read_data>: Prepheral ({prepheral_name}) is not found."
            )
            raise ValueError(
                f"<read_data>: Prepheral ({prepheral_name}) is not found."
            )

        data = self._peripherals[prepheral_name].read_data()
        is_data_changed = (
            self._peripherals_last_read_data_registery.get(
                prepheral_name, None
            )
            != data
        )
        self._peripherals_last_read_data_registery[prepheral_name] = data
        return data, is_data_changed

    def write_data(self, prepheral_name: str, data: str):
        """Write data to a specific prepheral.

        Parameters
        ----------
        prepheral_name : str
            The name of the prepheral.
        data : str
            The data to write to the prepheral.
        """
        if prepheral_name not in self._peripherals:
            logger.error(
                f"<write_data>: Prepheral ({prepheral_name}) is not found."
            )
            raise ValueError(
                f"<write_data>: Prepheral ({prepheral_name}) is not found."
            )

        self._peripherals[prepheral_name].write_data(data)

    def get_registered_peripherals_names(self) -> List[str]:
        """Get the names of the registered prepherals.

        Returns
        -------
        List[str]
            The names of the registered prepherals.
        """
        return list(self._peripherals.keys())


class StartButtonParameters(BasePeripheralParameters):
    """Parameters for the start button."""

    input_pin_numbers: Dict[str, int] = {"start_button_pin": 6}


class StartButton:
    """A button that can be used to execute the robot's selected mode."""

    def __init__(self, parameters: StartButtonParameters):
        """Initialize the start button."""
        super().__init__(parameters)

    def read_data(self):
        """Read the data from the button.

        Returns
        -------
        int
            The state of the button.
        """
        return GPIO.input(self._input_pin_numbers["start_button_pin"])


class SelectorSwitchParameters(BasePeripheralParameters):
    """Parameters for the selector switch."""

    input_pin_numbers: Dict[str, int] = {
        "normal_pin": 1,
        "optimization_pin": 2,
        "idle_pin": 3,
    }


class SelectorSwitch:
    """A switch that can be used to change the robot's running mode."""

    def __init__(self, parameters: SelectorSwitchParameters):
        """Initialize the selector switch."""
        super().__init__(parameters)

    def read_data(self):
        """Read the data from the switch.

        Returns
        -------
        str
            The current mode of the robot.
        """
        if GPIO.input(self._input_pin_numbers["normal_pin"]):
            return "normal"
        elif GPIO.input(self._input_pin_numbers["optimization_pin"]):
            return "optimization"
        elif GPIO.input(self._input_pin_numbers["idle_pin"]):
            return "idle"
        else:
            logger.warning("No mode is selected. The robot is in idle mode.")
            return "idle"


class OLEDDisplayParameters(BasePeripheralParameters):
    """Parameters for the OLED display."""

    output_pin_numbers: Dict[str, int] = {"SDA_pin": 1, "SCL_pin": 2}


class OLEDDisplay:
    """A display that can be used to show the robot's running mode."""

    def __init__(self, parameters: OLEDDisplayParameters):
        """Initialize the OLED display."""
        super().__init__(parameters)

    def write_data(self, data: str):
        """Write the data to the display.

        Parameters
        ----------
        data : str
            The data to write to the display.
        """
        pass
