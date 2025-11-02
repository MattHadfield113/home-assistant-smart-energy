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
    
    def add_device(self, entity_id, priority=5, power_consumption=0, schedule=None, 
                   allow_direct_control=True, auto_start_automation=None, 
                   required_run_duration=0):
        """Add a device to energy management."""
        self.managed_devices[entity_id] = {
            'priority': priority,
            'power_consumption': power_consumption,
            'enabled': True,
            'last_controlled': None,
            'last_heating_change': None,
            'schedule': schedule or {},  # {'start': '08:00', 'end': '22:00', 'days': [0,1,2,3,4,5,6]}
            'allow_direct_control': allow_direct_control,
            'auto_start_automation': auto_start_automation,  # HA automation/script to trigger
            'required_run_duration': required_run_duration  # Minutes needed for device
        }
        self.save_managed_devices()
        logger.info(f"Added device {entity_id} to energy management")
        self._publish_device_entity(entity_id)
    
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
                if device_info['enabled'] and self._can_control_device(entity_id, device_info):
                    state = self.ha_client.get_state(entity_id)
                    if state and state.get('state') in ['off', 'false']:
                        logger.info(f"Turning on {entity_id} due to solar generation")
                        self._control_device(entity_id, True, 'solar_excess')
                        device_info['last_controlled'] = datetime.now().isoformat()
        
        # High electricity cost - turn off lower priority devices
        elif electricity_cost > 0.30:  # Cost threshold
            logger.info("High electricity cost - disabling lower priority devices")
            for entity_id, device_info in sorted_devices:
                if device_info['enabled'] and device_info['priority'] > 5 and self._can_control_device(entity_id, device_info):
                    state = self.ha_client.get_state(entity_id)
                    if state and state.get('state') in ['on', 'true']:
                        logger.info(f"Turning off {entity_id} due to high cost")
                        self._control_device(entity_id, False, 'high_cost')
                        device_info['last_controlled'] = datetime.now().isoformat()
        
        self.save_managed_devices()
    
    def _can_control_device(self, entity_id, device_info):
        """Check if device can be controlled based on schedule and settings."""
        # Check if direct control is allowed
        if not device_info.get('allow_direct_control', True):
            return False
        
        # Check schedule
        schedule = device_info.get('schedule', {})
        if schedule:
            now = datetime.now()
            current_day = now.weekday()
            current_time = now.strftime('%H:%M')
            
            # Check if current day is in allowed days
            allowed_days = schedule.get('days', [])
            if allowed_days and current_day not in allowed_days:
                return False
            
            # Check if current time is outside the scheduled window
            start_time = schedule.get('start')
            end_time = schedule.get('end')
            if start_time and end_time:
                # If we're outside the schedule window, don't control
                if not (start_time <= current_time <= end_time):
                    logger.debug(f"Device {entity_id} outside schedule window")
                    return False
        
        return True
    
    def _can_change_heating(self, device_info):
        """Check if enough time has passed since last heating change."""
        min_interval = self.config.get('heating_min_change_interval', 900)  # Default 15 minutes
        last_change = device_info.get('last_heating_change')
        
        if not last_change:
            return True
        
        try:
            last_change_dt = datetime.fromisoformat(last_change)
            elapsed = (datetime.now() - last_change_dt).total_seconds()
            return elapsed >= min_interval
        except:
            return True
    
    def _control_device(self, entity_id, turn_on, reason):
        """Control device and publish decision to HA."""
        domain = entity_id.split('.')[0]
        
        # Check if it's a heating device and respect min change interval
        is_heating = 'heat' in entity_id.lower() or 'thermostat' in entity_id.lower()
        device_info = self.managed_devices.get(entity_id, {})
        
        if is_heating and not self._can_change_heating(device_info):
            logger.info(f"Skipping {entity_id} - minimum heating change interval not met")
            return
        
        # Control the device
        if turn_on:
            success = self.ha_client.turn_on(entity_id)
            # Trigger auto-start automation if configured
            auto_start = device_info.get('auto_start_automation')
            if success and auto_start:
                self._trigger_automation(auto_start, entity_id, reason)
        else:
            success = self.ha_client.turn_off(entity_id)
        
        if success:
            # Update last change time for heating devices
            if is_heating:
                device_info['last_heating_change'] = datetime.now().isoformat()
            
            # Publish decision to Home Assistant
            self._publish_control_decision(entity_id, turn_on, reason)
    
    def _trigger_automation(self, automation_id, device_id, reason):
        """Trigger a Home Assistant automation or script."""
        try:
            domain = automation_id.split('.')[0]
            if domain in ['automation', 'script']:
                service_data = {
                    'entity_id': automation_id,
                    'variables': {
                        'triggered_by': 'smart_energy_controller',
                        'device': device_id,
                        'reason': reason
                    }
                }
                self.ha_client.call_service(domain, 'trigger' if domain == 'automation' else 'turn_on', 
                                           service_data=service_data)
                logger.info(f"Triggered {automation_id} for {device_id}")
        except Exception as e:
            logger.error(f"Error triggering automation {automation_id}: {e}")
    
    def _publish_control_decision(self, entity_id, turned_on, reason):
        """Publish control decision as a sensor in Home Assistant."""
        if not self.config.get('publish_ha_entities', True):
            return
        
        try:
            sensor_id = f"sensor.sec_{entity_id.replace('.', '_')}_decision"
            state_data = {
                'state': 'on' if turned_on else 'off',
                'attributes': {
                    'device': entity_id,
                    'action': 'turned_on' if turned_on else 'turned_off',
                    'reason': reason,
                    'timestamp': datetime.now().isoformat(),
                    'friendly_name': f"Smart Energy Decision: {entity_id}"
                }
            }
            self.ha_client.set_state(sensor_id, state_data)
        except Exception as e:
            logger.error(f"Error publishing decision for {entity_id}: {e}")
    
    def _publish_device_entity(self, entity_id):
        """Publish device configuration as a sensor in Home Assistant."""
        if not self.config.get('publish_ha_entities', True):
            return
        
        try:
            device_info = self.managed_devices.get(entity_id, {})
            sensor_id = f"sensor.sec_{entity_id.replace('.', '_')}_config"
            state_data = {
                'state': 'enabled' if device_info.get('enabled') else 'disabled',
                'attributes': {
                    'device': entity_id,
                    'priority': device_info.get('priority', 5),
                    'power_consumption': device_info.get('power_consumption', 0),
                    'schedule': device_info.get('schedule', {}),
                    'allow_direct_control': device_info.get('allow_direct_control', True),
                    'friendly_name': f"Smart Energy Config: {entity_id}"
                }
            }
            self.ha_client.set_state(sensor_id, state_data)
        except Exception as e:
            logger.error(f"Error publishing config for {entity_id}: {e}")
    
    def calculate_optimal_solar_slots(self, solar_forecast_data, required_duration_minutes):
        """
        Calculate optimal time slots based on solar forecast.
        
        Args:
            solar_forecast_data: List of {'timestamp': ISO time, 'power': watts}
            required_duration_minutes: How long device needs to run
        
        Returns:
            List of optimal time slots with expected solar generation
        """
        if not solar_forecast_data or required_duration_minutes <= 0:
            return []
        
        optimal_slots = []
        slot_duration = required_duration_minutes * 60  # Convert to seconds
        
        # Group forecast data into contiguous slots of required duration
        for i in range(len(solar_forecast_data) - 1):
            start_time = datetime.fromisoformat(solar_forecast_data[i]['timestamp'])
            total_power = 0
            slot_count = 0
            
            # Calculate average power for this slot
            for j in range(i, min(i + required_duration_minutes, len(solar_forecast_data))):
                total_power += solar_forecast_data[j]['power']
                slot_count += 1
            
            if slot_count > 0:
                avg_power = total_power / slot_count
                optimal_slots.append({
                    'start_time': start_time.isoformat(),
                    'duration_minutes': required_duration_minutes,
                    'avg_solar_power': avg_power,
                    'total_energy_kwh': (avg_power * required_duration_minutes) / 60000
                })
        
        # Sort by average solar power (highest first)
        optimal_slots.sort(key=lambda x: x['avg_solar_power'], reverse=True)
        return optimal_slots[:10]  # Return top 10 slots
    
    def calculate_cheapest_cost_slots(self, cost_forecast_data, required_duration_minutes):
        """
        Calculate cheapest time slots based on energy cost forecast.
        
        Args:
            cost_forecast_data: List of {'timestamp': ISO time, 'cost_per_kwh': float}
            required_duration_minutes: How long device needs to run
        
        Returns:
            List of cheapest time slots with expected costs
        """
        if not cost_forecast_data or required_duration_minutes <= 0:
            return []
        
        cheapest_slots = []
        
        # Group forecast data into contiguous slots of required duration
        for i in range(len(cost_forecast_data) - 1):
            start_time = datetime.fromisoformat(cost_forecast_data[i]['timestamp'])
            total_cost = 0
            slot_count = 0
            
            # Calculate average cost for this slot
            for j in range(i, min(i + required_duration_minutes, len(cost_forecast_data))):
                total_cost += cost_forecast_data[j]['cost_per_kwh']
                slot_count += 1
            
            if slot_count > 0:
                avg_cost = total_cost / slot_count
                cheapest_slots.append({
                    'start_time': start_time.isoformat(),
                    'duration_minutes': required_duration_minutes,
                    'avg_cost_per_kwh': avg_cost,
                    'estimated_total_cost': avg_cost * required_duration_minutes / 60
                })
        
        # Sort by average cost (lowest first)
        cheapest_slots.sort(key=lambda x: x['avg_cost_per_kwh'])
        return cheapest_slots[:10]  # Return top 10 cheapest slots
    
    def get_solar_forecast(self):
        """Get solar generation forecast from configured sensor."""
        sensor = self.config.get('solar_forecast_sensor')
        if not sensor:
            return []
        
        try:
            state = self.ha_client.get_state(sensor)
            if state:
                # Assume forecast data is in attributes
                forecast = state.get('attributes', {}).get('forecast', [])
                return forecast
        except Exception as e:
            logger.error(f"Error getting solar forecast: {e}")
        
        return []
    
    def get_cost_forecast(self):
        """Get energy cost forecast from configured sensor."""
        sensor = self.config.get('electricity_forecast_sensor')
        if not sensor:
            return []
        
        try:
            state = self.ha_client.get_state(sensor)
            if state:
                # Assume forecast data is in attributes
                forecast = state.get('attributes', {}).get('forecast', [])
                return forecast
        except Exception as e:
            logger.error(f"Error getting cost forecast: {e}")
        
        return []
    
    def get_device_optimal_schedule(self, entity_id):
        """Get optimal schedule for a device based on solar and cost forecasts."""
        device_info = self.managed_devices.get(entity_id)
        if not device_info:
            return None
        
        required_duration = device_info.get('required_run_duration', 0)
        if required_duration <= 0:
            return None
        
        result = {
            'entity_id': entity_id,
            'required_duration_minutes': required_duration
        }
        
        # Get solar forecast optimization if enabled
        if self.config.get('enable_solar_forecast_optimization', False):
            solar_forecast = self.get_solar_forecast()
            if solar_forecast:
                result['optimal_solar_slots'] = self.calculate_optimal_solar_slots(
                    solar_forecast, required_duration
                )
        
        # Get cost forecast optimization if enabled
        if self.config.get('enable_cost_forecast_optimization', False):
            cost_forecast = self.get_cost_forecast()
            if cost_forecast:
                result['cheapest_cost_slots'] = self.calculate_cheapest_cost_slots(
                    cost_forecast, required_duration
                )
        
        return result
