# PID-Tuning-for-Motion-Optimization

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Arduino](https://img.shields.io/badge/-Arduino-00979D?style=for-the-badge&logo=Arduino&logoColor=white) ![nVIDIA](https://img.shields.io/badge/nVIDIA-%2376B900.svg?style=for-the-badge&logo=nVIDIA&logoColor=white) ![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?style=for-the-badge&logo=scipy&logoColor=%white) ![C](https://img.shields.io/badge/c-%2300599C.svg?style=for-the-badge&logo=c&logoColor=white) ![Bosch](https://a11ybadges.com/badge?logo=bosch) <img alt="Pandas" src="https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white" /> <img alt="Debian" src="https://img.shields.io/badge/Debian-D70A53?style=for-the-badge&logo=debian&logoColor=white" />

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

[![Generic badge](https://img.shields.io/badge/status-done-dark_green
)](https://shields.io/)


- [PID-Tuning-for-Motion-Optimization](#pid-tuning-for-motion-optimization)
  - [Methodology](#methodology)
  - [Experiments Settings](#experiments-settings)
  - [Results](#results)
    - [Key Findings](#key-findings)
  - [Replicate](#replicate)

## Methodology

The methodology involves three phases:

1. **Initial States Definition**: Six initial states were defined to influence the control system’s response during optimization. Each state adjusts the Proportional (P), Integral (I), and Derivative (D) gains differently to create diverse tuning scenarios.

2. **Finding Cartesian Product**: The Cartesian product of the defined configurations and initial states was computed, resulting in 18 unique trials.

3. **Run Trials and Save Results**: Trials were conducted using the specified configurations, and data were collected, including metrics like convergence speed, steady-state error, and optimal gain values.

## Experiments Settings

- **PID Gains Bounds**:
  - Proportional Gain (\(K_p\)): [1, 25]
  - Integral Gain (\(K_i\)): [0, 1]
  - Derivative Gain (\(K_d\)): [0, 1]

- **Constraints**:
  - Maximum Overshoot: 30%
  - Maximum Rise Time: 1000 ms

- **Configurations**:
  - **Balanced**: Mutation Rate: 60%, Crossover Rate: 60%
  - **Exploration Focused**: Mutation Rate: 80%, Crossover Rate: 30%
  - **Exploitation Focused**: Mutation Rate: 50%, Crossover Rate: 90%

## Results

The results demonstrate that DE consistently avoids local optima and achieves superior convergence rates, while BO excels in finding optimal solutions with fewer iterations but is more susceptible to becoming trapped in local optima.

### Key Findings
- DE outperforms BO in terms of robustness, maintaining a 100% convergence rate across all configurations.
- BO converges faster but occasionally fails to escape local optima.
- Initial states and configuration significantly impact optimizer performance, affecting convergence speed and steady-state error.

## Replicate

To replicate the study, check the [replicate.md](./replicate.md) file for detailed instructions on setting up the environment, running the experiments, and analyzing the results.
