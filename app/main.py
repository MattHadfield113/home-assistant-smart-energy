"""Main application for Smart Energy Controller addon."""

import asyncio
import json
import logging
import os
import threading
import time

from energy_manager import EnergyManager
from flask import Flask, jsonify, render_template, request
from ha_client import HomeAssistantClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", template_folder="templates")

# Initialize components
ha_client = None
energy_manager = None
automation_task = None


def load_config():
    """Load addon configuration."""
    config_path = "/data/options.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {}


@app.route("/")
def index():
    """Render main page."""
    return render_template("index.html")


@app.route("/api/devices")
def get_devices():
    """Get all available devices from Home Assistant."""
    try:
        devices = ha_client.get_devices()
        return jsonify({"success": True, "devices": devices})
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve devices"}), 500


@app.route("/api/devices/managed")
def get_managed_devices():
    """Get devices managed by energy controller."""
    try:
        devices = energy_manager.get_managed_devices()
        return jsonify({"success": True, "devices": devices})
    except Exception as e:
        logger.error(f"Error getting managed devices: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve managed devices"}), 500


@app.route("/api/devices/managed", methods=["POST"])
def add_managed_device():
    """Add a device to energy management."""
    try:
        data = request.json
        energy_manager.add_device(data["entity_id"], data.get("priority", 5), data.get("power_consumption", 0))
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error adding device: {e}")
        return jsonify({"success": False, "error": "Failed to add device"}), 500


@app.route("/api/devices/managed/<entity_id>", methods=["DELETE"])
def remove_managed_device(entity_id):
    """Remove a device from energy management."""
    try:
        energy_manager.remove_device(entity_id)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error removing device: {e}")
        return jsonify({"success": False, "error": "Failed to remove device"}), 500


@app.route("/api/energy/status")
def get_energy_status():
    """Get current energy status."""
    try:
        status = energy_manager.get_status()
        return jsonify({"success": True, "status": status})
    except Exception as e:
        logger.error(f"Error getting energy status: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve energy status"}), 500


@app.route("/api/heating/comparison")
def get_heating_comparison():
    """Get heating system cost comparison."""
    try:
        comparison = energy_manager.calculate_heating_comparison()
        return jsonify({"success": True, "comparison": comparison})
    except Exception as e:
        logger.error(f"Error calculating heating comparison: {e}")
        return jsonify({"success": False, "error": "Failed to calculate heating comparison"}), 500


@app.route("/api/automation/status")
def get_automation_status():
    """Get automation status."""
    try:
        status = energy_manager.get_automation_status()
        return jsonify({"success": True, "status": status})
    except Exception as e:
        logger.error(f"Error getting automation status: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve automation status"}), 500


@app.route("/api/automation/toggle", methods=["POST"])
def toggle_automation():
    """Toggle automation on/off."""
    try:
        data = request.json
        enabled = data.get("enabled", True)
        energy_manager.set_automation_enabled(enabled)
        return jsonify({"success": True, "enabled": enabled})
    except Exception as e:
        logger.error(f"Error toggling automation: {e}")
        return jsonify({"success": False, "error": "Failed to toggle automation"}), 500


@app.route("/api/config")
def get_config():
    """Get current configuration."""
    try:
        config = load_config()
        return jsonify({"success": True, "config": config})
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve configuration"}), 500


@app.route("/api/devices/schedule/<entity_id>")
def get_device_schedule(entity_id):
    """Get optimal schedule for a device based on forecasts."""
    try:
        schedule = energy_manager.get_device_optimal_schedule(entity_id)
        if schedule:
            return jsonify({"success": True, "schedule": schedule})
        else:
            return jsonify({"success": False, "error": "Device not found or no schedule available"}), 404
    except Exception as e:
        logger.error(f"Error getting device schedule: {e}")
        return jsonify({"success": False, "error": "Failed to calculate schedule"}), 500


@app.route("/api/devices/managed/<entity_id>", methods=["PUT"])
def update_managed_device(entity_id):
    """Update a managed device configuration."""
    try:
        data = request.json
        device_info = energy_manager.managed_devices.get(entity_id)
        if not device_info:
            return jsonify({"success": False, "error": "Device not found"}), 404

        # Update device settings
        if "priority" in data:
            device_info["priority"] = data["priority"]
        if "power_consumption" in data:
            device_info["power_consumption"] = data["power_consumption"]
        if "schedule" in data:
            device_info["schedule"] = data["schedule"]
        if "allow_direct_control" in data:
            device_info["allow_direct_control"] = data["allow_direct_control"]
        if "auto_start_automation" in data:
            device_info["auto_start_automation"] = data["auto_start_automation"]
        if "required_run_duration" in data:
            device_info["required_run_duration"] = data["required_run_duration"]

        energy_manager.save_managed_devices()
        energy_manager._publish_device_entity(entity_id)

        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error updating device: {e}")
        return jsonify({"success": False, "error": "Failed to update device"}), 500


@app.route("/api/forecast/solar")
def get_solar_forecast():
    """Get solar generation forecast."""
    try:
        forecast = energy_manager.get_solar_forecast()
        return jsonify({"success": True, "forecast": forecast})
    except Exception as e:
        logger.error(f"Error getting solar forecast: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve solar forecast"}), 500


@app.route("/api/forecast/cost")
def get_cost_forecast():
    """Get energy cost forecast."""
    try:
        forecast = energy_manager.get_cost_forecast()
        return jsonify({"success": True, "forecast": forecast})
    except Exception as e:
        logger.error(f"Error getting cost forecast: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve cost forecast"}), 500


def automation_loop_sync():
    """Main automation loop (synchronous wrapper)."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            if energy_manager and energy_manager.is_automation_enabled():
                loop.run_until_complete(energy_manager.update_and_control())
        except Exception as e:
            logger.error(f"Error in automation loop: {e}")
        time.sleep(30)  # Run every 30 seconds


def run_automation_background():
    """Run automation loop in background thread."""
    automation_thread = threading.Thread(target=automation_loop_sync, daemon=True)
    automation_thread.start()
    logger.info("Automation loop started in background")


def main():
    """Main entry point."""
    global ha_client, energy_manager

    logger.info("Starting Smart Energy Controller...")

    # Load configuration
    config = load_config()
    logger.info(f"Loaded configuration: {config}")

    # Initialize Home Assistant client
    supervisor_token = os.environ.get("SUPERVISOR_TOKEN")
    ha_client = HomeAssistantClient(supervisor_token)

    # Initialize Energy Manager
    energy_manager = EnergyManager(ha_client, config)

    # Start automation loop in background
    run_automation_background()

    # Run Flask app
    logger.info("Starting web server on port 8099...")
    app.run(host="0.0.0.0", port=8099, debug=False)


if __name__ == "__main__":
    main()
