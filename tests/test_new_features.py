"""Unit tests for new energy manager features."""
import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from energy_manager import EnergyManager


class TestEnergyManagerNewFeatures(unittest.TestCase):
    """Test cases for new energy manager features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_ha_client = Mock()
        self.config = {
            'solar_sensor': 'sensor.solar',
            'electricity_cost_sensor': 'sensor.cost',
            'gas_cost_sensor': 'sensor.gas',
            'solar_forecast_sensor': 'sensor.solar_forecast',
            'electricity_forecast_sensor': 'sensor.electricity_forecast',
            'free_session_sensors': [],
            'saving_session_sensors': [],
            'cop_coefficient': 3.5,
            'eer_coefficient': 12.0,
            'automation_enabled': True,
            'heating_min_change_interval': 900,
            'publish_ha_entities': True,
            'allow_direct_device_control': True,
            'enable_solar_forecast_optimization': True,
            'enable_cost_forecast_optimization': True
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
    
    def test_add_device_with_schedule(self):
        """Test adding a device with schedule."""
        self.manager.save_managed_devices = Mock()
        self.manager._publish_device_entity = Mock()
        
        schedule = {
            'start': '08:00',
            'end': '22:00',
            'days': [0, 1, 2, 3, 4]
        }
        
        self.manager.add_device(
            'switch.test',
            priority=5,
            power_consumption=100,
            schedule=schedule,
            allow_direct_control=True,
            auto_start_automation='automation.test',
            required_run_duration=60
        )
        
        self.assertIn('switch.test', self.manager.managed_devices)
        device = self.manager.managed_devices['switch.test']
        self.assertEqual(device['schedule'], schedule)
        self.assertEqual(device['auto_start_automation'], 'automation.test')
        self.assertEqual(device['required_run_duration'], 60)
        self.manager._publish_device_entity.assert_called_once_with('switch.test')
    
    def test_can_control_device_with_schedule(self):
        """Test schedule-based control restrictions."""
        self.manager.save_managed_devices = Mock()
        self.manager._publish_device_entity = Mock()
        
        # Add device with weekday-only schedule
        schedule = {
            'start': '08:00',
            'end': '22:00',
            'days': [0, 1, 2, 3, 4]  # Monday to Friday
        }
        
        self.manager.add_device(
            'switch.test',
            schedule=schedule,
            allow_direct_control=True
        )
        
        device_info = self.manager.managed_devices['switch.test']
        
        # Mock datetime to be within schedule
        with patch('energy_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 11, 4, 10, 0)  # Monday 10:00
            mock_datetime.fromisoformat = datetime.fromisoformat
            can_control = self.manager._can_control_device('switch.test', device_info)
            self.assertTrue(can_control)
    
    def test_can_control_device_outside_schedule(self):
        """Test device cannot be controlled outside schedule."""
        self.manager.save_managed_devices = Mock()
        self.manager._publish_device_entity = Mock()
        
        schedule = {
            'start': '08:00',
            'end': '22:00',
            'days': [0, 1, 2, 3, 4]
        }
        
        self.manager.add_device(
            'switch.test',
            schedule=schedule,
            allow_direct_control=True
        )
        
        device_info = self.manager.managed_devices['switch.test']
        
        # Mock datetime to be outside schedule (weekend)
        with patch('energy_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 11, 3, 10, 0)  # Sunday 10:00
            mock_datetime.fromisoformat = datetime.fromisoformat
            can_control = self.manager._can_control_device('switch.test', device_info)
            self.assertFalse(can_control)
    
    def test_heating_min_change_interval(self):
        """Test minimum change interval for heating devices."""
        device_info = {
            'last_heating_change': (datetime.now() - timedelta(seconds=600)).isoformat()
        }
        
        # 600 seconds elapsed, min interval 900 - should not allow change
        can_change = self.manager._can_change_heating(device_info)
        self.assertFalse(can_change)
        
        # Mock old change time
        device_info['last_heating_change'] = (datetime.now() - timedelta(seconds=1000)).isoformat()
        can_change = self.manager._can_change_heating(device_info)
        self.assertTrue(can_change)
    
    def test_calculate_optimal_solar_slots(self):
        """Test solar forecast optimization."""
        forecast_data = [
            {'timestamp': '2024-11-04T08:00:00', 'power': 500},
            {'timestamp': '2024-11-04T09:00:00', 'power': 1500},
            {'timestamp': '2024-11-04T10:00:00', 'power': 2500},
            {'timestamp': '2024-11-04T11:00:00', 'power': 3000},
            {'timestamp': '2024-11-04T12:00:00', 'power': 3200},
            {'timestamp': '2024-11-04T13:00:00', 'power': 3000},
            {'timestamp': '2024-11-04T14:00:00', 'power': 2500},
            {'timestamp': '2024-11-04T15:00:00', 'power': 1500},
            {'timestamp': '2024-11-04T16:00:00', 'power': 500},
        ]
        
        slots = self.manager.calculate_optimal_solar_slots(forecast_data, 60)
        
        self.assertIsInstance(slots, list)
        self.assertGreater(len(slots), 0)
        
        # Check first slot has highest average power
        first_slot = slots[0]
        self.assertIn('start_time', first_slot)
        self.assertIn('avg_solar_power', first_slot)
        self.assertIn('total_energy_kwh', first_slot)
        
        # Verify sorting (highest power first)
        for i in range(len(slots) - 1):
            self.assertGreaterEqual(slots[i]['avg_solar_power'], slots[i+1]['avg_solar_power'])
    
    def test_calculate_cheapest_cost_slots(self):
        """Test cost forecast optimization."""
        forecast_data = [
            {'timestamp': '2024-11-04T00:00:00', 'cost_per_kwh': 0.15},
            {'timestamp': '2024-11-04T01:00:00', 'cost_per_kwh': 0.12},
            {'timestamp': '2024-11-04T02:00:00', 'cost_per_kwh': 0.10},
            {'timestamp': '2024-11-04T03:00:00', 'cost_per_kwh': 0.10},
            {'timestamp': '2024-11-04T04:00:00', 'cost_per_kwh': 0.12},
            {'timestamp': '2024-11-04T05:00:00', 'cost_per_kwh': 0.20},
            {'timestamp': '2024-11-04T06:00:00', 'cost_per_kwh': 0.25},
            {'timestamp': '2024-11-04T07:00:00', 'cost_per_kwh': 0.30},
        ]
        
        slots = self.manager.calculate_cheapest_cost_slots(forecast_data, 120)
        
        self.assertIsInstance(slots, list)
        self.assertGreater(len(slots), 0)
        
        # Check first slot has lowest cost
        first_slot = slots[0]
        self.assertIn('start_time', first_slot)
        self.assertIn('avg_cost_per_kwh', first_slot)
        self.assertIn('estimated_total_cost', first_slot)
        
        # Verify sorting (lowest cost first)
        for i in range(len(slots) - 1):
            self.assertLessEqual(slots[i]['avg_cost_per_kwh'], slots[i+1]['avg_cost_per_kwh'])
    
    def test_get_device_optimal_schedule(self):
        """Test getting optimal schedule for a device."""
        self.manager.save_managed_devices = Mock()
        self.manager._publish_device_entity = Mock()
        
        # Add device with required run duration
        self.manager.add_device(
            'switch.test',
            required_run_duration=60
        )
        
        # Mock forecast data
        self.manager.get_solar_forecast = Mock(return_value=[
            {'timestamp': '2024-11-04T12:00:00', 'power': 3000}
        ])
        self.manager.get_cost_forecast = Mock(return_value=[
            {'timestamp': '2024-11-04T02:00:00', 'cost_per_kwh': 0.10}
        ])
        
        schedule = self.manager.get_device_optimal_schedule('switch.test')
        
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule['entity_id'], 'switch.test')
        self.assertIn('optimal_solar_slots', schedule)
        self.assertIn('cheapest_cost_slots', schedule)
    
    def test_control_device_triggers_automation(self):
        """Test that controlling a device triggers configured automation."""
        self.manager.save_managed_devices = Mock()
        self.manager._publish_device_entity = Mock()
        
        # Add device with auto-start automation
        self.manager.add_device(
            'switch.test',
            auto_start_automation='automation.start_washing'
        )
        
        self.mock_ha_client.turn_on = Mock(return_value=True)
        self.mock_ha_client.call_service = Mock(return_value=True)
        self.manager._publish_control_decision = Mock()
        
        self.manager._control_device('switch.test', True, 'test_reason')
        
        # Verify automation was triggered
        self.mock_ha_client.call_service.assert_called_once()
        call_args = self.mock_ha_client.call_service.call_args
        self.assertEqual(call_args[0][0], 'automation')
        self.assertEqual(call_args[0][1], 'trigger')
    
    def test_publish_control_decision(self):
        """Test publishing control decisions to HA."""
        self.mock_ha_client.set_state = Mock(return_value=True)
        
        self.manager._publish_control_decision('switch.test', True, 'solar_excess')
        
        self.mock_ha_client.set_state.assert_called_once()
        call_args = self.mock_ha_client.set_state.call_args[0]
        
        # Check sensor ID format
        self.assertTrue(call_args[0].startswith('sensor.sec_'))
        
        # Check state data
        state_data = call_args[1]
        self.assertEqual(state_data['state'], 'on')
        self.assertEqual(state_data['attributes']['reason'], 'solar_excess')
    
    def test_empty_forecast_data(self):
        """Test handling of empty forecast data."""
        slots = self.manager.calculate_optimal_solar_slots([], 60)
        self.assertEqual(slots, [])
        
        slots = self.manager.calculate_cheapest_cost_slots([], 60)
        self.assertEqual(slots, [])
    
    def test_zero_duration(self):
        """Test handling of zero duration."""
        forecast_data = [{'timestamp': '2024-11-04T12:00:00', 'power': 3000}]
        
        slots = self.manager.calculate_optimal_solar_slots(forecast_data, 0)
        self.assertEqual(slots, [])
    
    def test_battery_level_retrieval(self):
        """Test getting battery level."""
        # Enable battery management
        self.manager.config['enable_battery_management'] = True
        self.manager.config['battery_level_sensor'] = 'sensor.battery_level'
        
        self.mock_ha_client.get_sensor_value = Mock(return_value=75.0)
        level = self.manager.get_battery_level()
        
        self.assertEqual(level, 75.0)
        self.mock_ha_client.get_sensor_value.assert_called_with('sensor.battery_level')
    
    def test_battery_level_disabled(self):
        """Test battery level returns None when disabled."""
        self.manager.config['enable_battery_management'] = False
        level = self.manager.get_battery_level()
        self.assertIsNone(level)
    
    def test_battery_power_retrieval(self):
        """Test getting battery power."""
        self.manager.config['enable_battery_management'] = True
        self.manager.config['battery_power_sensor'] = 'sensor.battery_power'
        
        self.mock_ha_client.get_sensor_value = Mock(return_value=500.0)  # Charging
        power = self.manager.get_battery_power()
        
        self.assertEqual(power, 500.0)
    
    def test_status_includes_battery_when_enabled(self):
        """Test status includes battery info when enabled."""
        self.manager.config['enable_battery_management'] = True
        self.manager.config['battery_level_sensor'] = 'sensor.battery_level'
        self.manager.config['battery_power_sensor'] = 'sensor.battery_power'
        
        self.mock_ha_client.get_sensor_value = Mock(side_effect=[0.0, 0.0, 0.0, 80.0, 300.0])
        
        status = self.manager.get_status()
        
        self.assertIn('battery_level', status)
        self.assertIn('battery_power', status)
        self.assertIn('battery_state', status)
        self.assertEqual(status['battery_level'], 80.0)
        self.assertEqual(status['battery_power'], 300.0)
        self.assertEqual(status['battery_state'], 'charging')
    
    def test_battery_state_determination(self):
        """Test battery state is correctly determined."""
        self.manager.config['enable_battery_management'] = True
        self.manager.config['battery_level_sensor'] = 'sensor.battery_level'
        self.manager.config['battery_power_sensor'] = 'sensor.battery_power'
        
        # Test charging state
        self.mock_ha_client.get_sensor_value = Mock(side_effect=[0.0, 0.0, 0.0, 50.0, 500.0])
        status = self.manager.get_status()
        self.assertEqual(status['battery_state'], 'charging')
        
        # Test discharging state
        self.mock_ha_client.get_sensor_value = Mock(side_effect=[0.0, 0.0, 0.0, 50.0, -300.0])
        status = self.manager.get_status()
        self.assertEqual(status['battery_state'], 'discharging')
        
        # Test idle state
        self.mock_ha_client.get_sensor_value = Mock(side_effect=[0.0, 0.0, 0.0, 50.0, 0.0])
        status = self.manager.get_status()
        self.assertEqual(status['battery_state'], 'idle')
    
    def test_publish_system_sensors(self):
        """Test publishing system-wide sensors to HA."""
        self.mock_ha_client.get_sensor_value = Mock(side_effect=[1000.0, 0.25, 0.05])
        self.mock_ha_client.set_state = Mock(return_value=True)
        
        self.manager.publish_system_sensors()
        
        # Should have called set_state for multiple sensors
        self.assertGreater(self.mock_ha_client.set_state.call_count, 0)
        
        # Check that solar generation sensor was published
        calls = self.mock_ha_client.set_state.call_args_list
        sensor_ids = [call[0][0] for call in calls]
        self.assertIn('sensor.sec_solar_generation', sensor_ids)
        self.assertIn('sensor.sec_electricity_cost', sensor_ids)
        self.assertIn('sensor.sec_automation_status', sensor_ids)


if __name__ == '__main__':
    unittest.main()
