# New Features Guide - v1.1.0

## Overview

Version 1.1.0 introduces advanced scheduling, forecast optimization, and Home Assistant integration features to provide even smarter energy management.

## 1. Device Scheduling

### What It Does
Prevents the system from controlling devices during specific time windows and days of the week.

### Use Cases
- Don't control bedroom lights during sleeping hours (23:00-07:00)
- Only manage work-from-home devices on weekdays (Mon-Fri)
- Prevent dishwasher control during quiet hours
- Exclude weekend automation for certain devices

### Configuration
```json
{
  "schedule": {
    "start": "08:00",
    "end": "22:00",
    "days": [0, 1, 2, 3, 4]  // 0=Monday, 6=Sunday
  }
}
```

### How It Works
- System checks schedule before any control action
- If current time is outside the window, device is not controlled
- If current day is not in the allowed list, device is skipped
- Manual control via Home Assistant still works

## 2. Heating Control with Minimum Interval

### What It Does
Enforces a minimum time between heating system state changes to prevent frequent cycling.

### Why It Matters
- Extends heating system lifespan
- Improves efficiency
- Reduces wear on components
- Prevents temperature fluctuations

### Configuration
```yaml
heating_min_change_interval: 900  # 15 minutes in seconds
```

### How It Works
- Automatically detects heating devices (name contains 'heat' or 'thermostat')
- Tracks `last_heating_change` timestamp per device
- Skips control action if minimum interval not elapsed
- Configurable from 5 minutes (300s) to 1 hour (3600s)

### Example
```
10:00 - Heating turned ON due to low cost
10:10 - System wants to turn OFF (cost increased)
       - Skipped: Only 10 minutes elapsed, need 15 minutes
10:20 - System turns OFF heating (20 minutes elapsed ✓)
```

## 3. Solar Forecast Optimization

### What It Does
Analyzes solar generation forecasts to identify the best time slots for running devices.

### Prerequisites
- Solar forecast sensor configured (e.g., from Solcast, Forecast.Solar)
- Sensor must have `forecast` attribute with time-series data
- Enable via `enable_solar_forecast_optimization: true`

### Configuration
```yaml
solar_forecast_sensor: sensor.solcast_forecast
enable_solar_forecast_optimization: true
```

Device config:
```json
{
  "required_run_duration": 120  // Device needs 2 hours
}
```

### How It Works
1. Retrieves forecast data from configured sensor
2. Calculates average solar generation for sliding windows
3. Each window matches the device's `required_run_duration`
4. Sorts slots by highest solar generation
5. Returns top 10 optimal time slots

### Output Example
```json
{
  "optimal_solar_slots": [
    {
      "start_time": "2024-11-04T12:00:00",
      "duration_minutes": 120,
      "avg_solar_power": 3200,
      "total_energy_kwh": 6.4
    },
    {
      "start_time": "2024-11-04T11:00:00",
      "duration_minutes": 120,
      "avg_solar_power": 2800,
      "total_energy_kwh": 5.6
    }
  ]
}
```

### Use Cases
- Schedule washing machine during peak solar
- Run pool pump when solar is highest
- Charge EV during optimal solar generation
- Time dishwasher for maximum self-consumption

## 4. Cost Forecast Optimization

### What It Does
Identifies the cheapest time slots for running devices based on energy cost forecasts.

### Prerequisites
- Electricity cost forecast sensor (e.g., from Octopus Energy, Tibber)
- Sensor must have `forecast` attribute with pricing data
- Enable via `enable_cost_forecast_optimization: true`

### Configuration
```yaml
electricity_forecast_sensor: sensor.octopus_energy_forecast
enable_cost_forecast_optimization: true
```

### How It Works
1. Retrieves cost forecast from configured sensor
2. Calculates average cost for time windows matching device duration
3. Sorts by lowest cost
4. Returns top 10 cheapest slots

### Output Example
```json
{
  "cheapest_cost_slots": [
    {
      "start_time": "2024-11-04T02:00:00",
      "duration_minutes": 90,
      "avg_cost_per_kwh": 0.08,
      "estimated_total_cost": 0.12
    },
    {
      "start_time": "2024-11-04T03:00:00",
      "duration_minutes": 90,
      "avg_cost_per_kwh": 0.09,
      "estimated_total_cost": 0.135
    }
  ]
}
```

### Use Cases
- Schedule high-consumption devices during cheap rates
- Avoid peak pricing periods
- Optimize for time-of-use tariffs
- Maximize savings on dynamic pricing plans

## 5. Home Assistant Entity Publishing

### What It Does
Creates sensors in Home Assistant showing automation decisions and device configurations.

### Configuration
```yaml
publish_ha_entities: true
```

### Created Entities

#### Decision Sensors
Format: `sensor.sec_{device}_decision`

Example: `sensor.sec_switch_washing_machine_decision`

Attributes:
```yaml
state: "on"
attributes:
  device: "switch.washing_machine"
  action: "turned_on"
  reason: "solar_excess"
  timestamp: "2024-11-04T12:30:00"
```

#### Config Sensors
Format: `sensor.sec_{device}_config`

Example: `sensor.sec_switch_washing_machine_config`

Attributes:
```yaml
state: "enabled"
attributes:
  device: "switch.washing_machine"
  priority: 5
  power_consumption: 2000
  schedule: {...}
  allow_direct_control: true
```

### Use Cases
- Create dashboards showing automation activity
- Set up notifications when devices are controlled
- Track automation history
- Debug control decisions
- Create conditional automations based on decisions

### Example Automation
```yaml
automation:
  - alias: "Notify on Device Control"
    trigger:
      - platform: state
        entity_id: sensor.sec_switch_washing_machine_decision
    action:
      - service: notify.mobile_app
        data:
          message: "Washing machine {{ trigger.to_state.attributes.action }} - {{ trigger.to_state.attributes.reason }}"
```

## 6. Auto-Start Device Triggers

### What It Does
Automatically triggers Home Assistant automations or scripts when devices are turned on by the energy controller.

### Configuration
Per-device setting:
```json
{
  "auto_start_automation": "automation.start_washing_cycle"
}
```

Or:
```json
{
  "auto_start_automation": "script.dishwasher_eco_cycle"
}
```

### How It Works
1. Energy controller decides to turn on a device
2. Device is turned on via Home Assistant API
3. If `auto_start_automation` is configured, it's triggered
4. Context variables are passed to automation/script

### Context Variables
```yaml
variables:
  triggered_by: "smart_energy_controller"
  device: "switch.washing_machine"
  reason: "solar_excess"  # or "cheap_rate", "free_session"
```

### Use Cases

#### Start Appliance Programs
```yaml
automation:
  - alias: "Start Washing Machine"
    id: start_washing_cycle
    trigger:
      - platform: event
        event_type: automation_triggered
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.triggered_by == 'smart_energy_controller' }}"
    action:
      - service: button.press
        target:
          entity_id: button.washing_machine_start
```

#### Smart Device Control
```yaml
script:
  dishwasher_eco_cycle:
    sequence:
      - service: select.select_option
        target:
          entity_id: select.dishwasher_program
        data:
          option: "Eco 50°C"
      - service: button.press
        target:
          entity_id: button.dishwasher_start
```

#### Conditional Actions
```yaml
automation:
  - alias: "Pool Pump Smart Start"
    trigger:
      - platform: event
        event_type: automation_triggered
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ reason == 'solar_excess' }}"
            sequence:
              - service: switch.turn_on
                target:
                  entity_id: switch.pool_pump_high_speed
          - conditions:
              - condition: template
                value_template: "{{ reason == 'cheap_rate' }}"
            sequence:
              - service: switch.turn_on
                target:
                  entity_id: switch.pool_pump_low_speed
```

## 7. Direct Control Allowance

### What It Does
Allows you to prevent automation from controlling specific devices while keeping them in the system for monitoring.

### Configuration
Per-device:
```json
{
  "allow_direct_control": false
}
```

Global (affects all devices):
```yaml
allow_direct_device_control: false
```

### Use Cases
- Monitor device without automation
- Temporarily disable control during testing
- Keep device configuration but prevent actions
- Manual control only mode

### Behavior
- Device still appears in managed devices list
- Optimal schedules still calculated
- No automatic control actions taken
- Can still be controlled manually via Home Assistant

## 8. Required Run Duration

### What It Does
Specifies how long a device needs to run for forecast optimization calculations.

### Configuration
```json
{
  "required_run_duration": 90  // Minutes
}
```

### Use Cases
- Washing machine: 90 minutes
- Dishwasher: 120 minutes  
- EV charger: 360 minutes (6 hours)
- Pool pump: 240 minutes (4 hours)

### How It Affects Optimization
- Solar forecast: Finds 90-minute windows with best solar
- Cost forecast: Finds cheapest 90-minute periods
- Ensures full device cycle can complete in optimal conditions

## Best Practices

### Start Simple
1. Enable basic features first
2. Add scheduling to prevent unwanted control
3. Enable forecast features when sensors available
4. Use auto-start for advanced device control

### Testing
1. Set `allow_direct_control: false` for testing
2. Monitor decision sensors in Home Assistant
3. Verify schedules work as expected
4. Check forecast calculations make sense

### Optimization
1. Set accurate `required_run_duration` values
2. Use device schedules to avoid conflicts
3. Set appropriate heating intervals
4. Monitor published entities for insights

### Integration
1. Create HA dashboards for visibility
2. Set up notifications for important decisions
3. Use auto-start for smart appliances
4. Build conditional automations on decisions

## Troubleshooting

### Forecasts Not Working
- Check sensor is configured correctly
- Verify sensor has `forecast` attribute
- Enable feature flags in configuration
- Check logs for errors

### Device Not Being Controlled
- Verify `allow_direct_control` is true
- Check device schedule allows current time
- Ensure device priority and conditions met
- Review published decision sensor

### Heating Changes Too Frequent
- Increase `heating_min_change_interval`
- Check if device name contains 'heat' or 'thermostat'
- Review logs for skip messages

### Auto-Start Not Triggering
- Verify automation/script ID is correct
- Check automation is enabled in HA
- Review HA logs for trigger events
- Ensure device was turned on by controller

## Migration from v1.0.0

Existing configurations work without changes. New features are opt-in:

1. Existing devices maintain backward compatibility
2. New fields have sensible defaults
3. Features only active when explicitly enabled
4. No breaking changes to existing functionality

To use new features, update device configs:
```json
{
  "entity_id": "switch.existing_device",
  // Keep existing settings
  "priority": 5,
  "power_consumption": 1000,
  // Add new optional settings
  "schedule": {"start": "08:00", "end": "22:00", "days": [0,1,2,3,4]},
  "required_run_duration": 60,
  "allow_direct_control": true
}
```
