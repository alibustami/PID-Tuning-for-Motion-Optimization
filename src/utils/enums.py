"""This module contains the enums used in the project."""
from enum import Enum


class PeripheralName(Enum):
    """The names of the prepherals."""

    START_BUTTON = "start_button"
    SELECTOR_SWITCH = "selector_switch"
    OLED_DISPLAY = "oled_display"
