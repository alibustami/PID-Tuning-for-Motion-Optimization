"""This module contains the robot context class where the robot's running mode is managed."""
from src.models.modes import OptimizationMode
from src.models.peripherals import PeripheralsManager
from src.settings import logger
from src.utils.enums import PeripheralName


class RobotContext:
    """Holds the current running mode and manages state transitions."""

    def __init__(self, peripherals_manager: PeripheralsManager):
        """Initialize the robot context.

        Parameters
        ----------
        peripherals_manager : PeripheralsManager
            The peripheral devices manager.
        """
        self._current_mode = None
        self._observers = []
        self._peripherals_manager = peripherals_manager

    def set_mode(self, mode: object):
        """Set the current running mode.

        Parameters
        ----------
        mode : object
            The mode to set.
        """
        if self._current_mode:
            self._current_mode.exit()
        self._current_mode = mode
        mode.enter()

    def get_mode(self) -> object:
        """Get the current running mode.

        Returns
        -------
        object
            The current running mode.
        """
        return self._current_mode

    def run_mode(self):
        """Execute the current running mode operations."""
        if self._current_mode:
            self._current_mode.execute()

    def update(self):
        """Update the robot context."""
        self._check_if_mode_changed()
        self._check_start_button()

    def _check_if_mode_changed(self):
        """Check if the mode was changed by the user."""
        selector_switch = self._peripherals_manager.get_peripheral(
            PeripheralName.SELECTOR_SWITCH
        )
        selected_mode = selector_switch.get_selected_mode()
        return type(selected_mode) == type(self._current_mode)

    def _check_start_button(self):
        """Check if the start button was pressed to run the selected mode."""
        start_button_state = self._peripherals_manager.read_data(
            PeripheralName.START_BUTTON
        )
        if start_button_state == 1:
            self.run_mode()
