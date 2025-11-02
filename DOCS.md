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
free_session_sensors:
  - binary_sensor.octopus_free_session
saving_session_sensors:
  - binary_sensor.octopus_saving_session
cop_coefficient: 3.5
eer_coefficient: 12.0
automation_enabled: true
```

### Configuration Options

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `solar_sensor` | No | Entity ID of your solar generation sensor (in Watts) | "" |
| `electricity_cost_sensor` | No | Entity ID of your electricity cost sensor (per kWh) | "" |
| `gas_cost_sensor` | No | Entity ID of your gas cost sensor (per kWh) | "" |
| `free_session_sensors` | No | List of sensors indicating free electricity sessions | [] |
| `saving_session_sensors` | No | List of sensors indicating saving sessions | [] |
| `cop_coefficient` | No | Coefficient of Performance for your heat pump | 3.5 |
| `eer_coefficient` | No | Energy Efficiency Ratio for cooling | 12.0 |
| `automation_enabled` | No | Enable automation on startup | true |

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
  "power_consumption": 2000
}
```

### DELETE /api/devices/managed/{entity_id}
Remove a device from energy management

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
