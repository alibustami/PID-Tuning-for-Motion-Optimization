"""Settings for the smoky_flare_detection package."""
import logging

from src.models.modes import IdleMode, OptimizationMode, RunningMode

logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


SELECTOR_SWITCH_PINS_TO_MODES_MAPPER = {
    0: RunningMode(),
    1: IdleMode(),
    2: OptimizationMode(),
}
