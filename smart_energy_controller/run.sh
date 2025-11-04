#!/usr/bin/env bash
set -e

CONFIG_PATH=/data/options.json

# Create data directory if it doesn't exist
mkdir -p /data

# Create default config if none exists
if [ ! -f "$CONFIG_PATH" ]; then
    echo "Creating default configuration..."
    cat > "$CONFIG_PATH" << EOF
{
  "solar_sensor": "",
  "electricity_cost_sensor": "",
  "gas_cost_sensor": "",
  "free_session_sensors": [],
  "saving_session_sensors": [],
  "cop_coefficient": 3.5,
  "eer_coefficient": 12.0,
  "automation_enabled": true
}
EOF
fi

echo "Starting Smart Energy Controller..."
cd /app
exec python3 main.py
