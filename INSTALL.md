# Installation Guide

## Prerequisites

- Home Assistant OS, Supervised, or Container installation
- Access to the Add-on Store
- Sensors configured for:
  - Solar generation (optional)
  - Electricity pricing (optional)
  - Gas pricing (optional)
  - Free/Saving session indicators (optional)

## Installation Steps

### 1. Add the Repository

1. Open Home Assistant
2. Navigate to **Settings** → **Add-ons** → **Add-on Store**
3. Click the **⋮** menu (top right) → **Repositories**
4. Add this repository URL:
   ```
   https://github.com/MattHadfield113/home-assistant-smart-energy
   ```
5. Click **Add**

### 2. Install the Add-on

1. Refresh the Add-on Store
2. Find "Smart Energy Controller" in the list
3. Click on it and press **Install**
4. Wait for the installation to complete

### 3. Configure the Add-on

1. Go to the **Configuration** tab
2. Configure your sensors (see Configuration section below)
3. Click **Save**

### 4. Start the Add-on

1. Go to the **Info** tab
2. Enable **Start on boot** (recommended)
3. Enable **Watchdog** (recommended)
4. Click **Start**

### 5. Access the Interface

- Click **Open Web UI** or
- Access through the Home Assistant sidebar (after enabling ingress)
- URL format: `http://homeassistant.local:8099`

## Configuration

### Minimal Configuration

```yaml
automation_enabled: true
```

### Full Configuration Example

```yaml
solar_sensor: sensor.solar_power_generation
electricity_cost_sensor: sensor.electricity_price_per_kwh
gas_cost_sensor: sensor.gas_price_per_kwh
free_session_sensors:
  - binary_sensor.octopus_free_session
  - binary_sensor.solar_excess_threshold
saving_session_sensors:
  - binary_sensor.octopus_saving_session
  - binary_sensor.grid_demand_high
cop_coefficient: 3.5
eer_coefficient: 12.0
automation_enabled: true
```

### Configuration Options Explained

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `solar_sensor` | string | Entity ID of solar power sensor (in Watts) | `""` |
| `electricity_cost_sensor` | string | Entity ID of electricity cost sensor (per kWh) | `""` |
| `gas_cost_sensor` | string | Entity ID of gas cost sensor (per kWh) | `""` |
| `free_session_sensors` | list | Binary sensors indicating free electricity | `[]` |
| `saving_session_sensors` | list | Binary sensors indicating saving sessions | `[]` |
| `cop_coefficient` | float | Heat pump Coefficient of Performance | `3.5` |
| `eer_coefficient` | float | Energy Efficiency Ratio | `12.0` |
| `automation_enabled` | bool | Enable automation on startup | `true` |

## Finding Your Sensors

### Solar Generation Sensor
- Usually created by solar inverter integrations
- Common names:
  - `sensor.solar_power`
  - `sensor.inverter_power`
  - `sensor.solar_production`

### Electricity Cost Sensor
- Created by energy tariff integrations (Octopus Energy, etc.)
- Common names:
  - `sensor.electricity_price`
  - `sensor.octopus_energy_current_rate`
  - `sensor.energy_cost`

### Gas Cost Sensor
- Created by energy provider integrations
- Common names:
  - `sensor.gas_price`
  - `sensor.gas_rate`

### Session Sensors
- Binary sensors that are "on" during specific periods
- Can be created with template sensors or integrations
- Example: Octopus Energy Saving Sessions

## Troubleshooting

### Add-on Won't Start
1. Check the logs in the **Log** tab
2. Verify all sensor entity IDs are correct
3. Ensure Home Assistant API is accessible

### Can't Access Web Interface
1. Verify the add-on is running
2. Check port 8099 is not blocked
3. Try accessing via ingress instead

### Devices Not Appearing
1. Ensure devices exist in Home Assistant
2. Check device domains (must be switch, light, or button)
3. Refresh the device list in the interface

### Automation Not Working
1. Verify automation is enabled
2. Check sensor configurations
3. Review logs for errors
4. Ensure devices are added to management

## Next Steps

After installation:
1. Add devices to energy management
2. Set device priorities
3. Configure power consumption estimates
4. Monitor the dashboard
5. Adjust automation as needed

## Uninstallation

1. Stop the add-on
2. Click **Uninstall**
3. Data in `/data/` will be preserved unless you delete the add-on completely
