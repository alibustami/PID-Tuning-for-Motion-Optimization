from collections import OrderedDict

from src.optimizers.differential_evolution import (
    DifferentialEvolutionOptimizer,
)

optimizer = DifferentialEvolutionOptimizer(
    parameters_bounds={
        "Kp": (-1.0, 1.0),
        "Ki": (0.0, 1.0),
        "Kd": (0.0, 1.0),
    },
    constraint=OrderedDict(
        [
            ("overshoot", (0.0, 100)),
            ("settling_time", (0.0, 9000)),
        ]
    ),
    n_iter=30,
    experiment_total_run_time=10000,
    experiment_values_dump_rate=100,
    set_point=90,
)

optimizer.run()

print(optimizer.optimizer.x)
