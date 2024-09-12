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
  - [References](#references)

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

## References

The references for this study are available in the full research paper.
