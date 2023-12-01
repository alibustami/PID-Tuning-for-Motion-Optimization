"""This module contains the package information."""
from setuptools import setup

with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name="PID Tuning for Motion Optimization",
    version="0.0.1",
    description="PID Tuning for Motion Optimization",
    author=["Ali Albustami", "Zaid Ghazal", "Aseel Al-Wazani"],
    author_email=[
        "alialbustami@gmail.com",
        "zaid.ghazal20@gmail.com",
        "A.alwazani02@gmail.com",
    ],
    python_requires=">=3.8",
    packages=["src"],
    install_requires=REQUIREMENTS,
    include_package_data=True,
)
