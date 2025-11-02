# Changelog

All notable changes to the Smart Energy Controller add-on will be documented in this file.

## [1.1.0] - 2024-11-04

### Added
- Heating control with minimum time between changes (configurable interval)
- Device scheduling system to prevent control during specific times
- Home Assistant integration publishing automation decisions as entities
- Device control allowance settings (allow/disallow direct control per device)
- Smart solar timing based on solar forecast data
- Auto-start device triggers (HA automation/script on excess solar or cheap rates)
- Energy cost forecast integration for calculating cheapest slots
- Configuration options for forecast optimization
- Comprehensive test coverage for all new calculations (11 new tests)
- New API endpoints for device scheduling and forecast data
- Enhanced web UI with Scheduling tab for forecast visualization
- Modal dialogs for device schedule configuration

### Changed
- Enhanced device management with additional configuration options
- Improved automation logic with schedule-aware control
- Updated API to support device configuration updates
- Expanded test suite from 18 to 29 tests

### Technical Details
- Added `required_run_duration` for devices (minutes needed to run)
- Added `schedule` configuration (start time, end time, active days)
- Added `allow_direct_control` flag per device
- Added `auto_start_automation` to trigger HA automations/scripts
- Added `heating_min_change_interval` global setting (300-3600 seconds)
- Added `publish_ha_entities` to control HA entity publication
- Added `enable_solar_forecast_optimization` feature flag
- Added `enable_cost_forecast_optimization` feature flag
- New forecast calculation methods for optimal scheduling
- Device control decisions published as sensors in Home Assistant

## [1.0.0] - 2024-11-02

### Added
- Initial release of Smart Energy Controller add-on
- Device management system for switches, lights, and buttons
- Automation based on solar generation
- Automation based on electricity pricing
- Support for free electric sessions
- Support for saving sessions (demand response)
- Heat pump vs gas heating cost comparison
- COP (Coefficient of Performance) calculation
- EER (Energy Efficiency Ratio) calculation
- Web-based frontend with dashboard
- Real-time energy monitoring
- Device priority system for intelligent control
- RESTful API for device and automation management
- Responsive web design for mobile and desktop
- Auto-refresh dashboard every 30 seconds
- Persistent device storage
- Configurable automation settings
