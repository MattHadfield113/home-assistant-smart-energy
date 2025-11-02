# Smart Energy Controller Add-on for Home Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Intelligent energy management for Home Assistant with solar, pricing, heat pump optimization, and battery storage.

## Overview

The Smart Energy Controller is a comprehensive Home Assistant add-on that provides intelligent automation for your home's energy consumption. It automatically controls devices based on solar generation, electricity pricing, free electric sessions, and saving sessions. Additionally, it provides cost comparison between heat pump and gas heating systems, and can integrate with battery storage for optimized energy management.

## Key Features

- 🔌 **Device Management**: Import and manage switches, lights, and buttons from Home Assistant
- ☀️ **Solar Optimization**: Automatically turn on devices when excess solar power is available
- 💰 **Cost-Based Control**: Control devices based on real-time electricity pricing
- 🎁 **Free Session Support**: Enable all devices during free electricity periods
- 💾 **Saving Sessions**: Turn off non-essential devices during demand response events
- 🔥 **Heating Comparison**: Compare heat pump vs. gas heating costs with COP/EER calculations
- 🔋 **Battery Integration**: Monitor and optimize around battery storage systems
- 📊 **Web Dashboard**: Beautiful, responsive interface for monitoring and control
- 🤖 **Intelligent Automation**: Priority-based device control system
- 📅 **Smart Scheduling**: Device schedules with time windows and day restrictions
- 🔮 **Forecast Optimization**: Solar and cost forecast integration for optimal timing
- 🏡 **HA Integration**: Publishes automation decisions and system sensors to Home Assistant
- ⚡ **Auto-Start Triggers**: Launch automations/scripts on favorable conditions

## What's New in v1.2.0

- **Battery Storage Support**: Integrate with home battery systems for smarter energy management
- **System Sensor Publishing**: All key metrics published as Home Assistant sensors
- **Battery-Aware Automation**: Smarter decisions when battery storage is available
- **Enhanced Dashboard**: Battery status display when enabled

## What's New in v1.1.0

- **Heating Control**: Configurable minimum time between heating system changes
- **Device Scheduling**: Set time windows when devices should not be controlled
- **Forecast Integration**: Solar and cost forecast optimization for smart scheduling
- **Auto-Start Actions**: Trigger HA automations when conditions are favorable
- **Enhanced Control**: Per-device settings for direct control and run duration
- **HA Entity Publishing**: View automation decisions directly in Home Assistant

## Quick Start

1. Add this repository to your Home Assistant Add-on Store
2. Install the "Smart Energy Controller" add-on
3. Configure your energy sensors in the add-on configuration
4. Start the add-on
5. Access the web interface through the Home Assistant sidebar

## Documentation

For detailed documentation, see [DOCS.md](DOCS.md)

## Configuration Example

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

## Screenshots

### Dashboard
Real-time monitoring of solar generation, energy costs, and session status.

### Device Management
Add and manage devices with priority levels and power consumption settings.

### Heating Comparison
Compare heat pump and gas heating costs with intelligent recommendations.

## How It Works

The add-on continuously monitors your energy conditions and automatically controls managed devices:

- **During high solar generation**: Turn on devices to use excess power
- **During high electricity costs**: Turn off low-priority devices
- **During free sessions**: Enable all devices to maximize free electricity
- **During saving sessions**: Disable non-essential devices to reduce demand

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/MattHadfield113/home-assistant-smart-energy)
