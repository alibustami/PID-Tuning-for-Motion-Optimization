"""Utility functions for analysis scripts."""

import os
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

from src.analysis.optimizers_results_schemas import Gains

ALLOWED_CONFIGS = [f"config_{i}" for i in range(1, 4)]


def generate_dict(
    configs: List[str], trials: List[str], init_files: List[str]
) -> Dict:
    """Generate a dictionary with the given keys.

    Parameters
    ----------
    configs : List[str]
        List of configuration names.
    trials : List[str]
        List of trial names.
    init_files : List[str]
        List of init files.

    Returns
    -------
    Dict
        A dictionary with the given keys.
    """
    result_dict = {}

    for config in configs:
        result_dict[config] = {}
        for trial in trials:
            init_dict = {}
            for init_file in init_files:
                for i in range(6):
                    key = f"init_{i}_{init_file}"
                    init_dict[key] = None
            result_dict[config][trial] = init_dict
        result_dict[config]["configs_file"] = None

    return result_dict


def read_txt_file(file_path: Path) -> Dict:
    """Read a text file and return its content. With conversion of Gains to numpy array if needed.

    Parameters
    ----------
    file_path : Path
        The path to the file.

    Returns
    -------
    Dict
        The content of the file.
    """
    with open(file_path, "r") as file:
        data = file.read()
        data = eval(data)

        if isinstance(data["x"], np.ndarray):
            data["x"] = Gains(
                Kp=data["x"][0], Ki=data["x"][1], Kd=data["x"][2]
            )

    return data


def populate_optimizer_results(
    optimizer_results: Path, empty_dict: Dict
) -> Dict:
    """Populate optimizer results dictionary.

    Parameters
    ----------
    optimizer_results : Path
        Optimizer results root path.
    empty_dict : Dict
        Optimizer empty dictionary.

    Returns
    -------
    Dict
        Optimizers filled dictionary.
    """
    for root, dirs, files in os.walk(optimizer_results):
        for file_ in files:
            if not any(
                allowed_config in root for allowed_config in ALLOWED_CONFIGS
            ):
                continue  # to skip config_4 and above

            if "configs" in file_:
                for config in ALLOWED_CONFIGS:
                    if config in root:
                        empty_dict[config]["configs_file"] = os.path.join(
                            root, file_
                        )

                continue
            config = root.split(os.sep)[-2]
            trial = root.split(os.sep)[-1]
            selected_file = (
                "_".join(file_.split("-")[-1].split("_")[1:][:2])
                + "_"
                + file_.split("-")[-1].split("_")[-1].split(".")[1]
            )
            if "csv" in file_:
                empty_dict[config][trial][selected_file] = pd.read_csv(
                    os.path.join(root, file_)
                )
            elif "txt" in file_:
                results = read_txt_file(os.path.join(root, file_))
                empty_dict[config][trial][selected_file] = results

    return empty_dict
