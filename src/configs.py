"""This module contains the configs functions."""
import os
from pathlib import Path
from typing import Any

import yaml


def load_yaml() -> dict:
    """
    Load yaml file into memory.

    Returns
    -------
    dict
        configurations dictionary

    Raises
    ------
    FileNotFoundError
        If no configurations.yaml file found on project path.
    """
    yaml_path: str = os.path.join(
        Path(__file__).parent.parent, "configurations.yaml"
    )
    if not os.path.isfile(yaml_path):
        raise FileNotFoundError("No configurations.yaml found on project path")

    with open(yaml_path, encoding="utf-8") as cfgs_file:
        cfgs_dict: dict = yaml.safe_load(cfgs_file)

    return cfgs_dict if cfgs_dict else {}


def get_config(config_name: str) -> Any:
    """
    Get specific configuration from configurations.yaml file.

    Parameters
    ----------
    config_name : str
        The configuration name to get from configurations.yaml file.

    Returns
    -------
    dict
        The configuration dictionary.

    Raises
    ------
    KeyError
        If configuration name not found in configurations.yaml file.
    """
    cfgs_dict: dict = load_yaml()

    if "." in config_name:
        config_name_list: list = config_name.split(".")
        return cfgs_dict[config_name_list[0]][config_name_list[-1]]

    if config_name not in cfgs_dict:
        raise KeyError(
            f"Configuration name {config_name} not found in configurations.yaml file"
        )

    return cfgs_dict[config_name]
