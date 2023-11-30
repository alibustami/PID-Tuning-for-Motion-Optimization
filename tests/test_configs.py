"""This module contains tests for configs.py module."""
import unittest
from unittest.mock import patch

from src.configs import get_config


class TestConfigs(unittest.TestCase):
    """This class contains tests for configs.py module."""

    @patch(
        "src.configs.load_yaml",
        return_value={
            "test1": "test1",
            "test2": 10,
            "test3": True,
            "test4": [1, 2, 3],
        },
    )
    def test_get_config(self, mock_load_yaml):
        """Test get_config function."""
        self.assertEqual(get_config("test1"), "test1")
        self.assertEqual(get_config("test2"), 10)
        self.assertEqual(get_config("test3"), True)
        self.assertEqual(get_config("test4"), [1, 2, 3])

    def test_get_config_key_error(self):
        """Test get_config function with KeyError."""
        with self.assertRaises(KeyError):
            get_config("test5")
