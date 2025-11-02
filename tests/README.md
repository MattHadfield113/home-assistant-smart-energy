# Tests

Unit tests for the Smart Energy Controller addon.

## Running Tests

To run the tests:

```bash
python3 -m unittest discover tests -v
```

## Test Coverage

### test_energy_manager.py
Tests for the EnergyManager class:
- Device management (add/remove)
- COP/EER calculations
- Heating cost comparison
- Solar generation and cost monitoring
- Automation control
- Status reporting

### test_ha_client.py
Tests for the HomeAssistantClient class:
- API initialization
- Device retrieval
- State management
- Service calls (turn_on/turn_off)
- Sensor value reading

## Test Results

All tests passing (18/18) ✓
