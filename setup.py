"""This module contains the package information."""

from setuptools import setup

with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name="PID Tuning for Motion Optimization",
    version="1.0.0",
    description="PID Tuning for Motion Optimization",
    python_requires=">=3.9",
    packages=["src"],
    install_requires=REQUIREMENTS,
    include_package_data=True,
)
