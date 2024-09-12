# Evaluating Differential Evolution and Bayesian Optimization for Auto-Tuning Autonomous Mobile Robotics Systems

This repository contains the implementation and evaluation code for the research paper **"Evaluating Differential Evolution and Bayesian Optimization for Auto-Tuning Autonomous Mobile Robotics Systems."** The study explores the use of Differential Evolution (DE) and Bayesian Optimization (BO) to automatically tune PID controllers for Differential Drive Mobile Robots (DDMRs), focusing on convergence behavior, robustness, and the impact of initial states on optimization performance.

## Table of Contents

- [Evaluating Differential Evolution and Bayesian Optimization for Auto-Tuning Autonomous Mobile Robotics Systems](#evaluating-differential-evolution-and-bayesian-optimization-for-auto-tuning-autonomous-mobile-robotics-systems)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Methodology](#methodology)
  - [Experimental Settings](#experimental-settings)
  - [Results](#results)
    - [Key Findings](#key-findings)
    - [Performance Metrics](#performance-metrics)
  - [Conclusion](#conclusion)
  - [Replicate](#replicate)
  - [Repository Structure](#repository-structure)
    - [Repository Structure Overview](#repository-structure-overview)
    - [Repository Tree](#repository-tree)

## Introduction

PID controllers are widely used in control systems for precise motion control in mobile robotics. However, manual tuning of PID parameters is complex and time-consuming. This study investigates the effectiveness of Differential Evolution (DE) and Bayesian Optimization (BO) for automating PID tuning in DDMRs, focusing on optimizing controllers for in-place rotation tasks. The study evaluates the performance of DE and BO by defining various initial states and search configurations, comparing convergence speed, steady-state error, and the influence of initial parameters on convergence behavior.

## Methodology

The evaluation involves three main phases:

1. **Initial States Definition**: Six initial states are defined, each impacting the control system’s response differently during optimization.
2. **Finding Cartesian Product**: The Cartesian Product of the initial states and configurations is computed, resulting in 18 unique pairs for each optimizer.
3. **Run Trials and Save Results**: Trials are conducted using DE and BO, with each optimizer adjusting PID gains to achieve the desired performance criteria.

The key optimizers used are:

- **Differential Evolution (DE)**: A stochastic, population-based optimization algorithm known for its robustness in avoiding local optima.
- **Bayesian Optimization (BO)**: A probabilistic model-based approach using Gaussian processes, effective for expensive, noisy optimization tasks.

## Experimental Settings

The study uses a custom-built Differential Drive Mobile Robot (DDMR) equipped with sensors and actuators, controlled via a Jetson Nano platform. The robot’s control system aims to achieve a 90-degree in-place rotation, with the following settings:

- **PID Gains**:
  - Proportional Gain (Kp): [1, 25]
  - Integral Gain (Ki): [0, 1]
  - Derivative Gain (Kd): [0, 1]

- **Constraints**:
  - Maximum Overshoot: 30%
  - Maximum Rise Time: 1000 ms
  - Objective: Settling Time ≤ 2500 ms

- **Configurations**:
  - **Configuration 0**: Balanced exploration and exploitation
  - **Configuration 1**: Exploration-focused
  - **Configuration 2**: Exploitation-focused

## Results

### Key Findings

- **RQ1 What is the propensity of BO and DE optimization algorithms to end up in local optima?** DE consistently outperforms BO in avoiding local optima, achieving a perfect convergence rate, while BO, though faster in convergence speed, is more susceptible to local traps.
- **RQ2 What is the impact of the initial state on the optimizers' convergence speed, settling time, and optimal gain values?** The initial state significantly impacts optimizer performance, with BO achieving lower steady-state errors in some cases but struggling in certain initial conditions.
- **RQ3 How do different configurations of the optimizers influence their final convergence behavior, including the likelihood of getting trapped in local optima, convergence speed, settling time and the determination of optimal gain values?** Configuration settings significantly influence the convergence behavior of DE and BO, with DE showing greater resilience against local optima at the cost of slower convergence.

### Performance Metrics
- DE shows robust convergence with slightly higher steady-state errors compared to BO.
- BO offers faster convergence but occasionally gets trapped in local optima, especially under certain initial states.

## Conclusion

The results demonstrate that DE provides a more reliable solution for tuning PID controllers in DDMRs by avoiding local optima, while BO offers faster convergence at the risk of getting trapped. The choice of the optimizer and configuration should be tailored to the specific needs of the application, balancing exploration and exploitation based on performance requirements.

## Replicate

To replicate the study, follow the instructions in the [replicate.md](./replicate.md) file. The replication guide provides detailed steps for setting up the environment, running the experiments, and analyzing the results.


## Repository Structure

### Repository Structure Overview

- **BO-results**: Contains results from Bayesian Optimization experiments organized by different configurations (`config_1`, `config_2`, etc.). Each configuration folder contains experiment settings (`configs.txt`) and trial data in `.csv` and `.txt` formats, detailing different initialization runs.

- **DE-results**: Similar to `BO-results`, this directory holds results from Differential Evolution experiments, with configuration folders and trial data files for different initialization runs.

- **Makefile**: A file containing build automation commands.

- **README.md**: The main documentation file explaining the repository's purpose, structure, and usage.

- **STL_files**: Contains 3D model files (`.stl`) for physical components such as `lower_body.stl` and `upper_body.stl`.

- **_deps**: Contains dependencies, such as the `bayesian-optimization` folder.

- **arduino**: Includes Arduino scripts (`main.ino`, `nicla.ino`, `pid.ino`, `updated.ino`).

- **assets**: Holds media files (images, gifs) used for visual documentation, such as `assemble.gif` and `wires_connection.png`.

- **configurations.yaml**: A configuration file for setting up experiments and environment settings, this is the interface of the user with the project.

- **environment.yml**: Specifies the environment dependencies, useful for setting up with Conda.

- **evaluation**: Contains Jupyter Notebooks (`rq1.ipynb`, `rq2.ipynb`, `rq3.ipynb`) for analyzing research questions and experimental results.

- **init_states.json**: A JSON file that contains initial states used in experiments.

- **notebooks**: Includes various notebooks for data analysis.

- **pyproject.toml**: A configuration file for Python project settings, dependencies, and build system requirements.

- **replicate.md**: Documentation file that likely describes how to replicate this project, containting all the information about the hardware components and the environment preparation.

- **requirements.txt**: Lists Python dependencies required for the project.

- **setup.py**: Script used to set up and install the package.

- **src**: Main source code directory containing modules and scripts:
  - **analysis**: Scripts and schemas for analyzing optimization results.
  - **optimizers**: Code for the Bayesian and Differential Evolution optimizers, also has `trial.py`, which is the script executed to .
  - **models**: Contains modules defining system models (`modes.py`, `peripherals.py`).
  - **scripts**: Includes custom scripts like `motion_simulation.py`.
  - **utils**: Utility functions and helper scripts.

- **tests**: Holds test scripts.

- **trials_results.md**: A markdown file documenting results from various trials.

### Repository Tree
The repository is structured as follows:

```bash
├── BO-results
│   ├── config_1
│   │   ├── configs.txt
│   │   └── trial_1
│   │       ├── 13-39-12_init_0_bo.csv
│   │       ├── 13-39-58_init_0_bo.txt
│   │       ├── 13-41-53_init_1_bo.csv
│   │       ├── 13-43-09_init_1_bo.txt
│   │       ├── 13-43-28_init_2_bo.csv
│   │       ├── 13-45-26_init_2_bo.txt
│   │       ├── 13-45-44_init_3_bo.csv
│   │       ├── 15-49-02_init_3_bo.txt
│   │       ├── 16-29-08_init_4_bo.csv
│   │       ├── 17-41-48_init_4_bo.txt
│   │       ├── 17-50-26_init_5_bo.csv
│   │       └── 17-59-59_init_5_bo.txt
│   ├── config_2
│   │   ├── configs.txt
│   │   └── trial_1
│   │       ├── 19-14-07_init_0_bo.csv
│   │       ├── 19-22-57_init_0_bo.txt
│   │       ├── 19-24-30_init_1_bo.csv
│   │       ├── 19-56-03_init_2_bo.csv
│   │       ├── 19-57-17_init_2_bo.txt
│   │       ├── 20-58-01_init_3_bo.csv
│   │       ├── 21-03-40_init_3_bo.txt
│   │       ├── 22-03-55_init_4_bo.csv
│   │       ├── 22-09-28_init_4_bo.txt
│   │       └── 22-09-43_init_5_bo.csv
│   └── config_3
│       ├── configs.txt
│       └── trial_1
│           ├── 16-31-50_init_0_bo.csv
│           ├── 19-34-18_init_1_bo.csv
│           ├── 19-37-26_init_1_bo.txt
│           ├── 19-37-54_init_2_bo.csv
│           ├── 20-32-44_init_2_bo.txt
│           ├── 20-33-18_init_3_bo.csv
│           ├── 20-39-47_init_3_bo.txt
│           ├── 21-55-20_init_4_bo.csv
│           ├── 21-59-24_init_4_bo.txt
│           └── 22-00-00_init_5_bo.csv
├── DE-results
│   ├── config_1
│   │   ├── configs.txt
│   │   └── trial_1
│   │       ├── 15-54-45_init_0_de.csv
│   │       ├── 15-57-14_init_0_de.txt
│   │       ├── 15-57-58_init_1_de.csv
│   │       ├── 16-00-27_init_1_de.txt
│   │       ├── 16-02-28_init_2_de.csv
│   │       ├── 16-04-56_init_2_de.txt
│   │       ├── 16-57-02_init_3_de.csv
│   │       ├── 17-00-44_init_3_de.txt
│   │       ├── 17-01-36_init_4_de.csv
│   │       ├── 17-08-39_init_4_de.txt
│   │       ├── 17-17-05_init_5_de.csv
│   │       └── 17-39-51_init_5_de.txt
│   ├── config_2
│   │   ├── configs.txt
│   │   └── trial_1
│   │       ├── 17-42-33_init_0_de.csv
│   │       ├── 17-45-03_init_0_de.txt
│   │       ├── 17-45-29_init_1_de.csv
│   │       ├── 18-06-07_init_1_de.txt
│   │       ├── 18-50-42_init_2_de.csv
│   │       ├── 18-53-09_init_2_de.txt
│   │       ├── 19-53-48_init_3_de.csv
│   │       ├── 20-10-05_init_3_de.txt
│   │       ├── 20-10-39_init_4_de.csv
│   │       ├── 20-14-19_init_4_de.txt
│   │       ├── 20-14-48_init_5_de.csv
│   │       └── 20-36-06_init_5_de.txt
│   └── config_3
│       ├── configs.txt
│       └── trial_1
│           ├── 13-46-03_init_0_de.csv
│           ├── 13-51-56_init_0_de.txt
│           ├── 13-52-30_init_1_de.csv
│           ├── 14-16-45_init_1_de.txt
│           ├── 14-17-37_init_2_de.csv
│           ├── 14-23-43_init_2_de.txt
│           ├── 14-24-11_init_3_de.csv
│           ├── 14-33-54_init_3_de.txt
│           ├── 14-34-37_init_4_de.csv
│           ├── 14-37-06_init_4_de.txt
│           ├── 14-37-44_init_5_de.csv
│           └── 14-45-03_init_5_de.txt
├── Makefile
├── README.md
├── README2.md
├── STL_files
│   ├── lower_body.stl
│   └── upper_body.stl
├── _deps
│   └── bayesian-optimization
├── arduino
│   ├── main.ino
│   ├── nicla.ino
│   ├── pid.ino
│   └── updated.ino
├── assets
│   ├── IMG_8154.heic
│   ├── IMG_8155.heic
│   ├── assemble.gif
│   ├── image-1.jpg
│   ├── image-2.jpg
│   ├── merged.jpg
│   └── wires_connection.png
├── configurations.yaml
├── environment.yml
├── evaluation
│   ├── rq1.ipynb
│   ├── rq2.ipynb
│   └── rq3.ipynb
├── init_states.json
├── notebooks
│   ├── RQ2_visuals.ipynb
│   ├── analyze.ipynb
│   ├── de_1.png
│   ├── de_2.png
│   ├── de_3.png
│   ├── de_4.png
│   ├── de_5.png
│   ├── de_6.png
│   ├── de_best.png
│   ├── final_results_analysis.ipynb
│   ├── pid_gains_balanced.png
│   ├── results_analysis.ipynb
│   ├── results_with_init_stats_analysis.ipynb
│   ├── rq2_iterations_time_balanced.png
│   ├── rq2_pid_gains_scatter_balanced.png
│   ├── settling_time.png
│   ├── settling_time_low_res.png
│   ├── steady_state_error.png
│   └── steady_state_error_low_res.png
├── pyproject.toml
├── replicate.md
├── requirements.txt
├── setup.py
├── src
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-38.pyc
│   │   ├── __init__.cpython-39.pyc
│   │   ├── config.cpython-39.pyc
│   │   ├── configs.cpython-38.pyc
│   │   ├── configs.cpython-39.pyc
│   │   └── settings.cpython-39.pyc
│   ├── analysis
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-39.pyc
│   │   │   ├── analysis_utils.cpython-39.pyc
│   │   │   └── optimizers_results_schemas.cpython-39.pyc
│   │   ├── analysis_utils.py
│   │   ├── optimizers_configuration_schema.json
│   │   └── optimizers_results_schemas.py
│   ├── configs.py
│   ├── interfaces
│   │   └── interfaces.py
│   ├── models
│   │   ├── modes.py
│   │   └── peripherals.py
│   ├── optimizers
│   │   ├── __pycache__
│   │   │   ├── bayesian_optimizer.cpython-38.pyc
│   │   │   ├── bayesian_optimizer.cpython-39.pyc
│   │   │   └── differential_evolution.cpython-39.pyc
│   │   ├── bayesian_optimizer.py
│   │   ├── differential_evolution.py
│   │   ├── optimizer.py
│   │   └── trial.py
│   ├── robot_context.py
│   ├── scripts
│   │   ├── __pycache__
│   │   │   └── motion_simulation.cpython-39.pyc
│   │   └── motion_simulation.py
│   ├── settings.py
│   └── utils
│       ├── __pycache__
│       │   ├── helper.cpython-39.pyc
│       │   └── utils_funcs.cpython-39.pyc
│       ├── enums.py
│       ├── helper.py
│       └── utils_funcs.py
├── tests
│   ├── __init__.py
│   └── test_configs.py
└── trials_results.md
```
