"""Models for the Jetson Nano peripheral devices.""" ""
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel

from src.interfaces.interfaces import BasePeripheral, BasePeripheralParameters
from src.models.modes import IdleMode, OptimizationMode, RunningMode
from src.settings import logger
from src.utils.enums import PeripheralName

# from Jetson.GPIO import GPIO


class PeripheralsManager:
    """Manage the prepheral models."""

    def __init__(self, peripherals: Dict[PeripheralName, BasePeripheral]):
        """Initialize the prepheral models.

        Parameters
        ----------
        peripherals : Dict[str, BasePeripheral]
            The prepheral models. keys are the names of the prepheral based on the user preference. values are the prepheral models.
        """
        self._peripherals = peripherals

    def read_data(self, prepheral_name: PeripheralName):
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
        return data

    def write_data(self, prepheral_name: PeripheralName, data: Any):
        """Write data to a specific prepheral.

        Parameters
        ----------
        prepheral_name : PeripheralName
            The name of the prepheral.
        data : Any
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

    def get_peripheral(self, prepheral_name: PeripheralName) -> BasePeripheral:
        """Get a specific prepheral.

        Parameters
        ----------
        prepheral_name : PeripheralName
            The name of the prepheral.

        Returns
        -------
        BasePeripheral
            The prepheral model.
        """
        if prepheral_name not in self._peripherals:
            logger.error(
                f"<get_peripheral>: Prepheral ({prepheral_name}) is not found."
            )
            raise ValueError(
                f"<get_peripheral>: Prepheral ({prepheral_name}) is not found."
            )

        return self._peripherals[prepheral_name]

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
        pass
        # return GPIO.input(self._input_pin_numbers["start_button_pin"])


class SelectorSwitchParameters(BasePeripheralParameters):
    """Parameters for the selector switch."""

    input_pin_numbers: Dict[str, int] = {
        "normal_pin": 1,
        "optimization_pin": 2,
        "idle_pin": 3,
    }
    pins_to_mode_mapper: Dict[str, object] = {
        "normal_pin": RunningMode(),
        "optimization_pin": IdleMode(),
        "idle_pin": OptimizationMode(),
    }


class SelectorSwitch:
    """A switch that can be used to change the robot's running mode."""

    def __init__(self, parameters: SelectorSwitchParameters):
        """Initialize the selector switch."""
        super().__init__(parameters)
        self.pins_to_mode_mapper = parameters.pins_to_mode_mapper

    def read_data(self) -> Tuple[int, int, int]:
        """Read the data from the switch.

        Returns
        -------
        Tuple[int, int, int]
            The states of the switch pins (normal, optimization, idle).
        """
        pass
        # return (
        #     GPIO.input(self._input_pin_numbers["normal_pin"]),
        #     GPIO.input(self._input_pin_numbers["optimization_pin"]),
        #     GPIO.input(self._input_pin_numbers["idle_pin"]),
        # )

    def get_selected_mode(self):
        """Get the selected mode.

        Returns
        -------
        object
            The selected mode.
        """
        normal_pin, optimization_pin, idle_pin = self.read_data()
        if normal_pin == 1:
            return self.pins_to_mode_mapper["normal_pin"]
        elif optimization_pin == 1:
            return self.pins_to_mode_mapper["optimization_pin"]
        elif idle_pin == 1:
            return self.pins_to_mode_mapper["idle_pin"]
        else:
            return None


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
