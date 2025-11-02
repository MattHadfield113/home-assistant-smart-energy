# Feature Documentation

## Overview

Smart Energy Controller provides intelligent automation for home energy management with a focus on cost optimization and renewable energy utilization.

## Core Features

### 1. Device Management

#### Import Home Assistant Devices
- Automatically discover switches, lights, and buttons from Home Assistant
- Filter for controllable devices only
- Real-time state synchronization

#### Priority System
Devices are assigned priorities (1-10) for intelligent control:
- **Priority 1-3 (Essential)**: Critical devices that should remain on unless in saving sessions
  - Examples: Refrigerator, security systems, essential lighting
- **Priority 4-6 (Normal)**: Regular devices controlled based on conditions
  - Examples: Washing machine, dishwasher, entertainment systems
- **Priority 7-10 (Optional)**: Low priority devices, first to turn off
  - Examples: Pool pumps, decorative lighting, non-essential equipment

#### Power Consumption Tracking
- Configure estimated power consumption per device
- Used for energy budgeting and cost calculations
- Helps prioritize which devices to control

### 2. Solar Generation Optimization

#### Automatic Device Control
When solar generation exceeds threshold (1kW):
- Turn on managed devices to use excess solar power
- Prioritize high-consumption devices when more power available
- Maximize self-consumption of solar energy

#### Benefits
- Reduce grid electricity purchases
- Use free solar energy effectively
- Lower electricity bills
- Reduce carbon footprint

### 3. Cost-Based Control

#### Dynamic Pricing Response
- Monitor real-time electricity costs
- Turn off low-priority devices when prices high (>0.30/kWh)
- Enable devices when prices are low
- Optimize running costs automatically

#### Cost Threshold Management
Configurable thresholds for:
- High cost device shutoff
- Low cost device activation
- Free session utilization

### 4. Free Electric Sessions

#### Octopus Energy Integration
Support for free electricity periods:
- Detect free session activation
- Turn on ALL managed devices
- Maximize usage of free electricity
- Automatically restore normal operation when session ends

#### Supported Integrations
- Octopus Energy Saving Sessions
- Custom binary sensors
- Time-based templates
- Third-party tariff integrations

### 5. Saving Sessions (Demand Response)

#### Grid Demand Management
During high demand periods:
- Turn off non-essential devices (priority > 3)
- Reduce household electricity consumption
- Support grid stability
- Earn rewards from energy providers

#### Smart Turn-Off Logic
- Preserve essential device operation
- Gracefully handle device states
- Automatic restoration after session

### 6. Heat Pump vs Gas Comparison

#### COP Calculation
Coefficient of Performance (COP) calculation:
```
COP = Heat Output (kWh) / Electrical Input (kWh)
```

Typical values:
- Modern heat pumps: 3.0-4.5
- Older heat pumps: 2.5-3.5
- Higher COP = more efficient

#### Cost Comparison
Real-time cost comparison:
```
Heat Pump Cost/kWh = Electricity Cost / COP
Gas Cost/kWh = Gas Price
```

#### Smart Recommendations
- Automatic recommendation based on current costs
- Percentage savings calculation
- Consider both energy and efficiency

### 7. EER Calculation

Energy Efficiency Ratio for cooling:
```
EER = Cooling Output (BTU/h) / Electrical Input (Wh)
```

Typical values:
- High efficiency: 12-15+ BTU/Wh
- Standard efficiency: 8-11 BTU/Wh
- Used for air conditioning cost analysis

### 8. Web Dashboard

#### Real-Time Monitoring
- Solar generation display
- Current electricity and gas costs
- Active session indicators
- Managed device count
- Auto-refresh every 30 seconds

#### Device Management Interface
- Add/remove devices
- Configure priorities
- Set power consumption
- View current states

#### Heating Comparison View
- Side-by-side cost comparison
- COP display
- Savings percentage
- Clear recommendations

#### Automation Control
- Enable/disable automation
- View automation status
- See how automation works

### 9. REST API

Full API for custom integrations:

#### Device Endpoints
- `GET /api/devices` - Get all HA devices
- `GET /api/devices/managed` - Get managed devices
- `POST /api/devices/managed` - Add device
- `DELETE /api/devices/managed/{id}` - Remove device

#### Energy Endpoints
- `GET /api/energy/status` - Current status
- `GET /api/heating/comparison` - Heating comparison

#### Automation Endpoints
- `GET /api/automation/status` - Automation status
- `POST /api/automation/toggle` - Toggle automation

### 10. Persistent Storage

#### Device Configuration
- Managed devices saved to disk
- Survives addon restarts
- JSON-based storage in `/data/`

#### Configuration Preservation
- Settings maintained across updates
- Easy backup and restore

## Automation Logic

### Decision Flow

1. **Check if automation enabled** → If no, skip
2. **Check for saving session** → If yes, turn off non-essential
3. **Check for free session** → If yes, turn on all devices
4. **Check solar generation** → If high, turn on devices
5. **Check electricity cost** → If high, turn off low-priority
6. **Wait 30 seconds** → Repeat

### Priority-Based Control

Devices controlled based on priority and conditions:

| Condition | Priority 1-3 | Priority 4-6 | Priority 7-10 |
|-----------|--------------|--------------|---------------|
| Normal | On | On | On |
| High Solar | On | On | On |
| High Cost | On | Conditional | Off |
| Saving Session | On | Off | Off |
| Free Session | On | On | On |

## Configuration Examples

### Typical UK Setup (Octopus Energy)
```yaml
solar_sensor: sensor.solaredge_current_power
electricity_cost_sensor: sensor.octopus_energy_electricity_current_rate
gas_cost_sensor: sensor.octopus_energy_gas_current_rate
free_session_sensors:
  - binary_sensor.octopus_saving_session_active
saving_session_sensors:
  - binary_sensor.octopus_saving_session_active
cop_coefficient: 3.5
automation_enabled: true
```

### Solar-Only Setup
```yaml
solar_sensor: sensor.solar_power
electricity_cost_sensor: ""
gas_cost_sensor: ""
free_session_sensors: []
saving_session_sensors: []
automation_enabled: true
```

### Heat Pump Comparison Setup
```yaml
electricity_cost_sensor: sensor.electricity_price
gas_cost_sensor: sensor.gas_price
cop_coefficient: 4.0
eer_coefficient: 12.0
automation_enabled: false
```

## Best Practices

### Device Selection
- Start with high-consumption, flexible devices
- Avoid devices requiring manual intervention
- Don't automate critical systems initially

### Priority Assignment
- Essential services: 1-3
- Flexible loads: 4-6
- Deferrable loads: 7-10

### Power Consumption
- Use manufacturer specifications
- Measure with smart plugs for accuracy
- Update periodically

### Testing
- Start with automation disabled
- Test individual devices
- Monitor for unexpected behavior
- Gradually enable automation

### Monitoring
- Check dashboard regularly
- Review device control patterns
- Adjust priorities as needed
- Monitor cost savings

## Limitations

- Requires configured sensors for full functionality
- 30-second automation cycle (not real-time)
- Cannot predict future prices (reacts to current)
- Depends on Home Assistant API availability
- Manual device power consumption configuration

## Future Enhancements

Potential features for future versions:
- Machine learning for optimal control
- Weather-based predictions
- Battery storage integration
- EV charging optimization
- Historical cost analysis
- Mobile app notifications
- Schedule-based overrides
- Multi-zone control
