# Smart Energy Controller Add-on

Intelligent energy management for Home Assistant with solar, pricing, and heat pump optimization.

## Features

### Device Management
- Import switches, lights, and buttons from Home Assistant
- Set device priorities for intelligent control
- Configure estimated power consumption per device
- Real-time device status monitoring

### Automation Based On
- **Solar Generation**: Automatically turn on devices when excess solar power is available
- **Power Costs**: Control devices based on current electricity pricing
- **Free Electric Sessions**: Enable all devices during free electricity periods
- **Saving Sessions**: Turn off non-essential devices during demand response events

### Heating System Analysis
- **COP Calculation**: Calculate Coefficient of Performance for heat pumps
- **EER Calculation**: Energy Efficiency Ratio for cooling systems
- **Cost Comparison**: Compare heat pump vs. gas heating costs in real-time
- **Smart Recommendations**: Get automated recommendations on which system to use

### Web Interface
- Beautiful, responsive dashboard
- Real-time energy monitoring
- Device management interface
- Heating system comparison view
- Automation control panel

## Installation

1. Add this repository to your Home Assistant Add-on Store
2. Install the "Smart Energy Controller" add-on
3. Configure your sensors (see Configuration section)
4. Start the add-on
5. Access the web interface through Home Assistant

## Configuration

### Basic Configuration

```yaml
solar_sensor: sensor.solar_power
electricity_cost_sensor: sensor.electricity_price
gas_cost_sensor: sensor.gas_price
solar_forecast_sensor: sensor.solar_forecast
electricity_forecast_sensor: sensor.electricity_forecast
free_session_sensors:
  - binary_sensor.octopus_free_session
saving_session_sensors:
  - binary_sensor.octopus_saving_session
cop_coefficient: 3.5
eer_coefficient: 12.0
automation_enabled: true
heating_min_change_interval: 900
publish_ha_entities: true
allow_direct_device_control: true
enable_solar_forecast_optimization: true
enable_cost_forecast_optimization: true
```

### Configuration Options

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `solar_sensor` | No | Entity ID of your solar generation sensor (in Watts) | "" |
| `electricity_cost_sensor` | No | Entity ID of your electricity cost sensor (per kWh) | "" |
| `gas_cost_sensor` | No | Entity ID of your gas cost sensor (per kWh) | "" |
| `solar_forecast_sensor` | No | Entity ID of solar forecast sensor (with forecast attribute) | "" |
| `electricity_forecast_sensor` | No | Entity ID of cost forecast sensor (with forecast attribute) | "" |
| `free_session_sensors` | No | List of sensors indicating free electricity sessions | [] |
| `saving_session_sensors` | No | List of sensors indicating saving sessions | [] |
| `cop_coefficient` | No | Coefficient of Performance for your heat pump | 3.5 |
| `eer_coefficient` | No | Energy Efficiency Ratio for cooling | 12.0 |
| `automation_enabled` | No | Enable automation on startup | true |
| `heating_min_change_interval` | No | Minimum seconds between heating changes (300-3600) | 900 |
| `publish_ha_entities` | No | Publish automation decisions as HA entities | true |
| `allow_direct_device_control` | No | Global setting to allow device control | true |
| `enable_solar_forecast_optimization` | No | Enable solar forecast features | false |
| `enable_cost_forecast_optimization` | No | Enable cost forecast features | false |

## How It Works

### Device Priority System

Devices are controlled based on a priority system (1-10):
- **1-3**: High priority - Always on unless in saving session
- **4-6**: Medium priority - Controlled based on solar/cost
- **7-10**: Low priority - First to turn off during high costs or saving sessions

### Automation Logic

1. **Saving Sessions**: Turn off all devices with priority > 3
2. **Free Sessions**: Turn on all managed devices
3. **Smart Control**:
   - High solar (>1kW): Turn on devices
   - High costs (>0.30/kWh): Turn off low priority devices

### Heat Pump vs Gas Comparison

The system calculates the cost per kWh of heat for both systems:

- **Heat Pump Cost** = Electricity Cost / COP
- **Gas Cost** = Gas Cost (already per kWh)

A recommendation is provided based on which is cheaper.

## Usage

### Adding Devices

1. Navigate to the "Devices" tab
2. Click "Refresh Device List" to see available devices
3. Click "Add" next to a device
4. Set the priority (1-10) and power consumption
5. The device is now managed by the system

### Monitoring Energy

The Dashboard shows:
- Current solar generation
- Electricity and gas costs
- Active sessions (free/saving)
- Number of managed devices

### Heating Comparison

The "Heating Comparison" tab shows:
- Cost per kWh for heat pump
- Cost per kWh for gas heating
- Your heat pump's COP
- Recommendation on which system to use
- Percentage savings

### Automation Control

Toggle automation on/off from the "Automation" tab. When enabled:
- Devices are controlled automatically every 30 seconds
- Device states are logged
- Energy decisions are made based on current conditions
- Automation decisions published to Home Assistant (if enabled)

## New Features in v1.1.0

### Device Scheduling

Configure time windows when devices should NOT be controlled:

```json
{
  "entity_id": "switch.dishwasher",
  "schedule": {
    "start": "08:00",
    "end": "22:00",
    "days": [0, 1, 2, 3, 4]  // Monday-Friday
  },
  "allow_direct_control": true,
  "required_run_duration": 120,  // Minutes
  "auto_start_automation": "automation.start_dishwasher"
}
```

### Solar Forecast Optimization

When `enable_solar_forecast_optimization` is enabled and `solar_forecast_sensor` is configured:
- System analyzes forecast data to find optimal time slots
- Considers device `required_run_duration`
- Returns top 10 slots with highest solar generation
- Accessible via `/api/devices/schedule/{entity_id}`

### Cost Forecast Optimization

When `enable_cost_forecast_optimization` is enabled and `electricity_forecast_sensor` is configured:
- System calculates cheapest time slots
- Factors in device run duration
- Returns top 10 most cost-effective slots
- Helps schedule energy-intensive devices

### Heating Control

Minimum interval between heating system changes:
- Configurable via `heating_min_change_interval` (300-3600 seconds)
- Prevents frequent cycling of heating systems
- Automatically detects heating devices (name contains 'heat' or 'thermostat')
- Tracks last change per device

### Home Assistant Integration

When `publish_ha_entities` is enabled:
- Control decisions published as `sensor.sec_{device}_decision`
- Device configs published as `sensor.sec_{device}_config`
- Includes timestamp, reason, and action details
- View automation activity directly in HA

### Auto-Start Triggers

Trigger Home Assistant automations/scripts when conditions are favorable:
```yaml
# In device config
auto_start_automation: automation.start_washing_machine
# or
auto_start_automation: script.dishwasher_start
```

When device is turned on due to excess solar or cheap rates, the configured automation/script is triggered with context variables.

## API Endpoints

### GET /api/devices
Get all available devices from Home Assistant

### GET /api/devices/managed
Get all devices currently managed by the system

### POST /api/devices/managed
Add a device to energy management
```json
{
  "entity_id": "switch.washing_machine",
  "priority": 5,
  "power_consumption": 2000,
  "schedule": {
    "start": "08:00",
    "end": "22:00",
    "days": [0,1,2,3,4]
  },
  "allow_direct_control": true,
  "required_run_duration": 90,
  "auto_start_automation": "automation.start_washing"
}
```

### PUT /api/devices/managed/{entity_id}
Update device configuration (new in v1.1.0)
```json
{
  "priority": 7,
  "schedule": {...},
  "allow_direct_control": false
}
```

### DELETE /api/devices/managed/{entity_id}
Remove a device from energy management

### GET /api/devices/schedule/{entity_id}
Get optimal schedule for device based on forecasts (new in v1.1.0)

### GET /api/forecast/solar
Get solar generation forecast data (new in v1.1.0)

### GET /api/forecast/cost
Get energy cost forecast data (new in v1.1.0)

### GET /api/energy/status
Get current energy status

### GET /api/heating/comparison
Get heating system cost comparison

### GET /api/automation/status
Get automation status

### POST /api/automation/toggle
Toggle automation on/off
```json
{
  "enabled": true
}
```

## Troubleshooting

### Devices Not Appearing
- Ensure Home Assistant API is accessible
- Check that devices are properly configured in Home Assistant
- Verify the add-on has the correct permissions

### Automation Not Working
- Check that sensors are configured correctly
- Verify sensor entity IDs in configuration
- Check add-on logs for errors
- Ensure automation is enabled

### Cost Comparison Incorrect
- Verify gas and electricity cost sensors
- Check COP coefficient matches your heat pump
- Ensure cost sensors report values in the same units

## Support

For issues and feature requests, please visit:
https://github.com/MattHadfield113/home-assistant-smart-energy

## License

MIT License
