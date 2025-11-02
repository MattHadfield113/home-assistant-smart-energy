"""Energy management logic."""
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EnergyManager:
    """Manages energy automation and device control."""
    
    def __init__(self, ha_client, config):
        """Initialize the energy manager."""
        self.ha_client = ha_client
        self.config = config
        self.managed_devices = self.load_managed_devices()
        self.automation_enabled = config.get('automation_enabled', True)
        
    def load_managed_devices(self):
        """Load managed devices from storage."""
        devices_file = '/data/managed_devices.json'
        if os.path.exists(devices_file):
            try:
                with open(devices_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading managed devices: {e}")
        return {}
    
    def save_managed_devices(self):
        """Save managed devices to storage."""
        devices_file = '/data/managed_devices.json'
        try:
            os.makedirs('/data', exist_ok=True)
            with open(devices_file, 'w') as f:
                json.dump(self.managed_devices, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving managed devices: {e}")
    
    def add_device(self, entity_id, priority=5, power_consumption=0):
        """Add a device to energy management."""
        self.managed_devices[entity_id] = {
            'priority': priority,
            'power_consumption': power_consumption,
            'enabled': True,
            'last_controlled': None
        }
        self.save_managed_devices()
        logger.info(f"Added device {entity_id} to energy management")
    
    def remove_device(self, entity_id):
        """Remove a device from energy management."""
        if entity_id in self.managed_devices:
            del self.managed_devices[entity_id]
            self.save_managed_devices()
            logger.info(f"Removed device {entity_id} from energy management")
    
    def get_managed_devices(self):
        """Get all managed devices with current state."""
        devices = []
        for entity_id, device_info in self.managed_devices.items():
            state = self.ha_client.get_state(entity_id)
            if state:
                devices.append({
                    'entity_id': entity_id,
                    'name': state.get('attributes', {}).get('friendly_name', entity_id),
                    'state': state.get('state'),
                    'priority': device_info['priority'],
                    'power_consumption': device_info['power_consumption'],
                    'enabled': device_info['enabled']
                })
        return devices
    
    def get_solar_generation(self):
        """Get current solar generation."""
        sensor = self.config.get('solar_sensor')
        if sensor:
            return self.ha_client.get_sensor_value(sensor)
        return 0.0
    
    def get_electricity_cost(self):
        """Get current electricity cost."""
        sensor = self.config.get('electricity_cost_sensor')
        if sensor:
            return self.ha_client.get_sensor_value(sensor)
        return 0.0
    
    def get_gas_cost(self):
        """Get current gas cost."""
        sensor = self.config.get('gas_cost_sensor')
        if sensor:
            return self.ha_client.get_sensor_value(sensor)
        return 0.0
    
    def is_free_electric_session(self):
        """Check if currently in a free electric session."""
        sensors = self.config.get('free_session_sensors', [])
        for sensor in sensors:
            state = self.ha_client.get_state(sensor)
            if state and state.get('state') in ['on', 'true', 'active']:
                return True
        return False
    
    def is_saving_session(self):
        """Check if currently in a saving session (should turn off devices)."""
        sensors = self.config.get('saving_session_sensors', [])
        for sensor in sensors:
            state = self.ha_client.get_state(sensor)
            if state and state.get('state') in ['on', 'true', 'active']:
                return True
        return False
    
    def calculate_cop(self, heat_output_kwh, electrical_input_kwh):
        """
        Calculate Coefficient of Performance (COP) for heat pumps.
        COP = Heat Output / Electrical Input
        """
        if electrical_input_kwh > 0:
            return heat_output_kwh / electrical_input_kwh
        return 0.0
    
    def calculate_eer(self, cooling_output_btu, electrical_input_wh):
        """
        Calculate Energy Efficiency Ratio (EER) for cooling systems.
        EER = Cooling Output (BTU/h) / Electrical Input (Wh)
        """
        if electrical_input_wh > 0:
            return cooling_output_btu / electrical_input_wh
        return 0.0
    
    def calculate_heating_comparison(self):
        """
        Calculate cost comparison between heat pump and gas heating.
        """
        electricity_cost = self.get_electricity_cost()
        gas_cost = self.get_gas_cost()
        cop = self.config.get('cop_coefficient', 3.5)
        
        # Cost per kWh of heat
        heat_pump_cost_per_kwh = electricity_cost / cop if cop > 0 else 0
        gas_cost_per_kwh = gas_cost  # Assuming gas cost is already per kWh
        
        savings_percentage = 0
        if gas_cost_per_kwh > 0:
            savings_percentage = ((gas_cost_per_kwh - heat_pump_cost_per_kwh) / gas_cost_per_kwh) * 100
        
        return {
            'electricity_cost': electricity_cost,
            'gas_cost': gas_cost,
            'cop': cop,
            'heat_pump_cost_per_kwh': heat_pump_cost_per_kwh,
            'gas_cost_per_kwh': gas_cost_per_kwh,
            'savings_percentage': savings_percentage,
            'recommended': 'heat_pump' if heat_pump_cost_per_kwh < gas_cost_per_kwh else 'gas'
        }
    
    def get_status(self):
        """Get current energy status."""
        return {
            'solar_generation': self.get_solar_generation(),
            'electricity_cost': self.get_electricity_cost(),
            'gas_cost': self.get_gas_cost(),
            'is_free_session': self.is_free_electric_session(),
            'is_saving_session': self.is_saving_session(),
            'automation_enabled': self.automation_enabled,
            'managed_device_count': len(self.managed_devices),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_automation_status(self):
        """Get automation status."""
        return {
            'enabled': self.automation_enabled,
            'last_run': datetime.now().isoformat()
        }
    
    def set_automation_enabled(self, enabled):
        """Enable or disable automation."""
        self.automation_enabled = enabled
        logger.info(f"Automation {'enabled' if enabled else 'disabled'}")
    
    def is_automation_enabled(self):
        """Check if automation is enabled."""
        return self.automation_enabled
    
    async def update_and_control(self):
        """Main automation logic to control devices based on energy conditions."""
        if not self.automation_enabled:
            return
        
        logger.info("Running automation update...")
        
        # Get current conditions
        solar_generation = self.get_solar_generation()
        electricity_cost = self.get_electricity_cost()
        is_free_session = self.is_free_electric_session()
        is_saving_session = self.is_saving_session()
        
        logger.info(f"Solar: {solar_generation}W, Cost: {electricity_cost}, Free: {is_free_session}, Saving: {is_saving_session}")
        
        # During saving sessions, turn off non-essential devices
        if is_saving_session:
            await self.handle_saving_session()
            return
        
        # During free sessions, turn on all devices
        if is_free_session:
            await self.handle_free_session()
            return
        
        # Smart control based on solar and pricing
        await self.handle_smart_control(solar_generation, electricity_cost)
    
    async def handle_saving_session(self):
        """Turn off devices during saving sessions."""
        logger.info("Saving session active - turning off non-essential devices")
        
        for entity_id, device_info in self.managed_devices.items():
            if device_info['enabled'] and device_info['priority'] > 3:
                # Turn off lower priority devices (priority > 3)
                state = self.ha_client.get_state(entity_id)
                if state and state.get('state') in ['on', 'true']:
                    logger.info(f"Turning off {entity_id} for saving session")
                    self.ha_client.turn_off(entity_id)
                    device_info['last_controlled'] = datetime.now().isoformat()
        
        self.save_managed_devices()
    
    async def handle_free_session(self):
        """Turn on devices during free electric sessions."""
        logger.info("Free electric session active - turning on devices")
        
        for entity_id, device_info in self.managed_devices.items():
            if device_info['enabled']:
                state = self.ha_client.get_state(entity_id)
                if state and state.get('state') in ['off', 'false']:
                    logger.info(f"Turning on {entity_id} for free session")
                    self.ha_client.turn_on(entity_id)
                    device_info['last_controlled'] = datetime.now().isoformat()
        
        self.save_managed_devices()
    
    async def handle_smart_control(self, solar_generation, electricity_cost):
        """Smart control based on solar generation and electricity cost."""
        # Calculate total power consumption of managed devices
        total_consumption = sum(
            device['power_consumption'] 
            for device in self.managed_devices.values() 
            if device['enabled']
        )
        
        # Sort devices by priority (lower number = higher priority)
        sorted_devices = sorted(
            self.managed_devices.items(),
            key=lambda x: x[1]['priority']
        )
        
        # High solar generation - turn on devices
        if solar_generation > 1000:  # More than 1kW solar
            logger.info("High solar generation - enabling devices")
            for entity_id, device_info in sorted_devices:
                if device_info['enabled']:
                    state = self.ha_client.get_state(entity_id)
                    if state and state.get('state') in ['off', 'false']:
                        logger.info(f"Turning on {entity_id} due to solar generation")
                        self.ha_client.turn_on(entity_id)
                        device_info['last_controlled'] = datetime.now().isoformat()
        
        # High electricity cost - turn off lower priority devices
        elif electricity_cost > 0.30:  # Cost threshold
            logger.info("High electricity cost - disabling lower priority devices")
            for entity_id, device_info in sorted_devices:
                if device_info['enabled'] and device_info['priority'] > 5:
                    state = self.ha_client.get_state(entity_id)
                    if state and state.get('state') in ['on', 'true']:
                        logger.info(f"Turning off {entity_id} due to high cost")
                        self.ha_client.turn_off(entity_id)
                        device_info['last_controlled'] = datetime.now().isoformat()
        
        self.save_managed_devices()
