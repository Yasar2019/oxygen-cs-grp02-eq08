"""
This module contains tests for the Main class.
"""

import os
import unittest
from unittest.mock import Mock, patch
import pytest
from src.main import Main


@patch.dict(os.environ, {"TOKEN": "test-token"})
def test_analyze_datapoint_ac_on():
    """
    Test if the analyze_datapoint method correctly instructs the HVAC to turn on the AC
    when the temperature is above T_MAX.
    """
    main = Main()
    main.T_MAX = 30
    main.T_MIN = 10
    main.send_action_to_hvac = Mock()  # Mock the send_action_to_hvac method
    # A temperature above T_MAX
    main.analyze_datapoint("2023-07-04T12:00:00", 35)
    main.send_action_to_hvac.assert_called_with(
        "2023-07-04T12:00:00", "TurnOnAc", main.TICKETS
    )


@patch.dict(os.environ, {"TOKEN": "test-token"})
def test_analyze_datapoint_heater_on():
    """
    Test if the analyze_datapoint method correctly instructs the HVAC to turn on the heater
    when the temperature is below T_MIN.
    """
    main = Main()
    main.T_MAX = 30
    main.T_MIN = 10
    main.send_action_to_hvac = Mock()  # Mock the send_action_to_hvac method
    # A temperature below T_MIN
    main.analyze_datapoint("2023-07-04T12:00:00", 5)
    main.send_action_to_hvac.assert_called_with(
        "2023-07-04T12:00:00", "TurnOnHeater", main.TICKETS
    )


@patch.dict(os.environ, {"TOKEN": "test-token"})
def test_analyze_datapoint_no_action():
    """
    Test if the analyze_datapoint method correctly does not instruct the HVAC to take any action
    when the temperature is between T_MIN and T_MAX.
    """
    main = Main()
    main.T_MAX = 30
    main.T_MIN = 10
    main.send_action_to_hvac = Mock()  # Mock the send_action_to_hvac method
    # A temperature between T_MIN and T_MAX
    main.analyze_datapoint("2023-07-04T12:00:00", 20)
    main.send_action_to_hvac.assert_not_called()


@patch.dict(os.environ, {"TOKEN": "test-token"})
def test_init_with_token():
    """
    Test if the Main class correctly initializes with a TOKEN environment variable.
    """
    main = Main()
    assert main.TOKEN == "test-token"


@patch.dict(os.environ, {}, clear=True)
def test_init_without_token():
    with pytest.raises(ValueError):
        Main()


if __name__ == "__main__":
    unittest.main()
