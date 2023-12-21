"""This module contains the interfaces for the robot's peripherals and modes."""
from abc import ABC, abstractmethod
from typing import Dict, List

# from Jetson.GPIO import GPIO
from pydantic import BaseModel


class BasePeripheralParameters(BaseModel):
    """Parameters for Peripheral.

    Attributes
    ----------
    input_pin_numbers : Dict[str, int]
        The pin numbers for output Peripheral. keys are the names of the Peripheral based on the user preference. values are the pin numbers based on the GPIP.BOARD pins numbering.
    output_pin_numbers : Dict[str, int]
        The pin numbers for output Peripheral. keys are the names of the Peripheral based on the user preference. values are the pin numbers based on the GPIP.BOARD pins numbering.
    """

    input_pin_numbers: Dict[str, int] = {}
    output_pin_numbers: Dict[str, int] = {}


class BasePeripheral(ABC):
    """Base class for prepheral models."""

    def __init__(self, parameters: BasePeripheralParameters):
        """Initialize the Peripheral."""
        self._input_pin_numbers = parameters.input_pin_numbers
        self._output_pin_numbers = parameters.output_pin_numbers
        self.initialize()

    def initialize(self):
        """Initialize the Peripheral' pins (input and output)."""
        # Pass for now
        pass
        # GPIO.setmode(GPIO.BOARD)
        # for pin_number in self._input_pin_numbers.values():
        #     GPIO.setup(pin_number, GPIO.IN)
        # for pin_number in self._output_pin_numbers.values():
        #     GPIO.setup(pin_number, GPIO.OUT)

    @abstractmethod
    def read_data(self):
        """Read data from the Peripheral."""
        NotImplementedError("read_data method is not implemented.")

    @abstractmethod
    def write_data(self):
        """Write data to the Peripheral."""
        NotImplementedError("write_data method is not implemented.")


class BaseMode(ABC):
    """Abstract class representing a robot running mode."""

    @abstractmethod
    def enter(self):
        """Enter this mode."""
        NotImplementedError("enter method is not implemented.")

    @abstractmethod
    def exit(self):
        """Exit this mode."""
        NotImplementedError("exit method is not implemented.")

    @abstractmethod
    def execute(self, action):
        """Execute this mode operations."""
        NotImplementedError("execute method is not implemented.")
