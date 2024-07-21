"""Trail Module."""

from collections import OrderedDict
from random import randint

from serial import Serial

from src.optimizers.bayesian_optimizer import BayesianOptimizer
from src.optimizers.differential_evolution import (
    DifferentialEvolutionOptimizer,
)
from src.utils.helper import clear_input_buffer

set_point = 90
# while 0 == set_point:
#     set_point = randint(-180, 180)

connection_object = Serial(
    port="/dev/ttyACM0",
    baudrate=9600,
    timeout=0.1,
)
print("done connecting !")
optimizer = BayesianOptimizer(
    parameters_bounds={
        "Kp": (1, 25),
        "Ki": (0.0, 1.0),
        "Kd": (0.0, 1.0),
    },
    constraint=OrderedDict(
        [
            ("overshoot", (0.0, 30)),
            ("risetime", (0.0, 600)),
        ]
    ),
    n_iter=30,
    experiment_total_run_time=5000,
    experiment_values_dump_rate=100,
    set_point=set_point,
    arduino_connection_object=connection_object,
    selected_init_state=0,
)
clear_input_buffer(connection_object)
optimizer.run()

# print(optimizer.optimizer.x)
