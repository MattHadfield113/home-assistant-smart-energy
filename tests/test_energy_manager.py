"""Unit tests for energy_manager module."""

import os
import sys
import unittest
from unittest.mock import Mock

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from energy_manager import EnergyManager  # noqa: E402


class TestEnergyManager(unittest.TestCase):
    """Test cases for EnergyManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ha_client = Mock()
        self.config = {
            "solar_sensor": "sensor.solar",
            "electricity_cost_sensor": "sensor.cost",
            "gas_cost_sensor": "sensor.gas",
            "free_session_sensors": [],
            "saving_session_sensors": [],
            "cop_coefficient": 3.5,
            "eer_coefficient": 12.0,
            "automation_enabled": True,
        }
        # Mock file operations
        self.original_exists = os.path.exists
        self.original_makedirs = os.makedirs
        os.path.exists = Mock(return_value=False)
        os.makedirs = Mock()

        self.manager = EnergyManager(self.mock_ha_client, self.config)

    def tearDown(self):
        """Clean up after tests."""
        os.path.exists = self.original_exists
        os.makedirs = self.original_makedirs

    def test_initialization(self):
        """Test manager initialization."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.automation_enabled, True)
        self.assertEqual(len(self.manager.managed_devices), 0)

    def test_add_device(self):
        """Test adding a device."""
        self.manager.save_managed_devices = Mock()
        self.manager.add_device("switch.test", priority=5, power_consumption=100)

        self.assertIn("switch.test", self.manager.managed_devices)
        self.assertEqual(self.manager.managed_devices["switch.test"]["priority"], 5)
        self.assertEqual(self.manager.managed_devices["switch.test"]["power_consumption"], 100)
        self.manager.save_managed_devices.assert_called_once()

    def test_remove_device(self):
        """Test removing a device."""
        self.manager.save_managed_devices = Mock()
        self.manager.add_device("switch.test", priority=5, power_consumption=100)
        self.manager.remove_device("switch.test")

        self.assertNotIn("switch.test", self.manager.managed_devices)

    def test_calculate_cop(self):
        """Test COP calculation."""
        cop = self.manager.calculate_cop(10.0, 2.0)
        self.assertEqual(cop, 5.0)

        cop = self.manager.calculate_cop(10.0, 0.0)
        self.assertEqual(cop, 0.0)

    def test_calculate_eer(self):
        """Test EER calculation."""
        eer = self.manager.calculate_eer(12000, 1000)
        self.assertEqual(eer, 12.0)

        eer = self.manager.calculate_eer(12000, 0)
        self.assertEqual(eer, 0.0)

    def test_calculate_heating_comparison(self):
        """Test heating cost comparison."""
        self.mock_ha_client.get_sensor_value = Mock(side_effect=[0.25, 0.05])  # electricity, gas

        comparison = self.manager.calculate_heating_comparison()

        self.assertIn("heat_pump_cost_per_kwh", comparison)
        self.assertIn("gas_cost_per_kwh", comparison)
        self.assertIn("recommended", comparison)
        self.assertIn("savings_percentage", comparison)

    def test_get_solar_generation(self):
        """Test getting solar generation."""
        self.mock_ha_client.get_sensor_value = Mock(return_value=1500.0)
        solar = self.manager.get_solar_generation()
        self.assertEqual(solar, 1500.0)

    def test_get_electricity_cost(self):
        """Test getting electricity cost."""
        self.mock_ha_client.get_sensor_value = Mock(return_value=0.25)
        cost = self.manager.get_electricity_cost()
        self.assertEqual(cost, 0.25)

    def test_automation_enabled(self):
        """Test automation enable/disable."""
        self.manager.set_automation_enabled(False)
        self.assertFalse(self.manager.is_automation_enabled())

        self.manager.set_automation_enabled(True)
        self.assertTrue(self.manager.is_automation_enabled())

    def test_get_status(self):
        """Test getting status."""
        self.mock_ha_client.get_sensor_value = Mock(return_value=0.0)
        status = self.manager.get_status()

        self.assertIn("solar_generation", status)
        self.assertIn("electricity_cost", status)
        self.assertIn("gas_cost", status)
        self.assertIn("automation_enabled", status)
        self.assertIn("managed_device_count", status)


if __name__ == "__main__":
    unittest.main()
