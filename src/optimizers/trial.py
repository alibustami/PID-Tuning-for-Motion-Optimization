"""Trail Module."""

import time

from serial import Serial

from src.configs import get_config
from src.utils.helper import clear_input_buffer
from src.utils.utils_funcs import select_optimizer

arduino_connection_configs = get_config("arduino_connection")

connection_object = Serial(**arduino_connection_configs)
print("done connecting !")

selected_optimizer = get_config("optimizer")
optimizer = select_optimizer(selected_optimizer, connection_object)

clear_input_buffer(connection_object)
exp_start_time = time.time()
optimizer.run(exp_start_time=exp_start_time)
