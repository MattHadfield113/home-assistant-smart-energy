"""Main application for Smart Energy Controller addon."""
import os
import json
import asyncio
import logging
from flask import Flask, render_template, jsonify, request
from energy_manager import EnergyManager
from ha_client import HomeAssistantClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')

# Initialize components
ha_client = None
energy_manager = None


def load_config():
    """Load addon configuration."""
    config_path = '/data/options.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route('/api/devices')
def get_devices():
    """Get all available devices from Home Assistant."""
    try:
        devices = ha_client.get_devices()
        return jsonify({'success': True, 'devices': devices})
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/managed')
def get_managed_devices():
    """Get devices managed by energy controller."""
    try:
        devices = energy_manager.get_managed_devices()
        return jsonify({'success': True, 'devices': devices})
    except Exception as e:
        logger.error(f"Error getting managed devices: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/managed', methods=['POST'])
def add_managed_device():
    """Add a device to energy management."""
    try:
        data = request.json
        energy_manager.add_device(
            data['entity_id'],
            data.get('priority', 5),
            data.get('power_consumption', 0)
        )
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error adding device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/managed/<entity_id>', methods=['DELETE'])
def remove_managed_device(entity_id):
    """Remove a device from energy management."""
    try:
        energy_manager.remove_device(entity_id)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error removing device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/energy/status')
def get_energy_status():
    """Get current energy status."""
    try:
        status = energy_manager.get_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logger.error(f"Error getting energy status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/heating/comparison')
def get_heating_comparison():
    """Get heating system cost comparison."""
    try:
        comparison = energy_manager.calculate_heating_comparison()
        return jsonify({'success': True, 'comparison': comparison})
    except Exception as e:
        logger.error(f"Error calculating heating comparison: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/automation/status')
def get_automation_status():
    """Get automation status."""
    try:
        status = energy_manager.get_automation_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logger.error(f"Error getting automation status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/automation/toggle', methods=['POST'])
def toggle_automation():
    """Toggle automation on/off."""
    try:
        data = request.json
        enabled = data.get('enabled', True)
        energy_manager.set_automation_enabled(enabled)
        return jsonify({'success': True, 'enabled': enabled})
    except Exception as e:
        logger.error(f"Error toggling automation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config')
def get_config():
    """Get current configuration."""
    try:
        config = load_config()
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


async def automation_loop():
    """Main automation loop."""
    while True:
        try:
            if energy_manager.is_automation_enabled():
                await energy_manager.update_and_control()
        except Exception as e:
            logger.error(f"Error in automation loop: {e}")
        await asyncio.sleep(30)  # Run every 30 seconds


def run_flask():
    """Run Flask app."""
    app.run(host='0.0.0.0', port=8099, debug=False)


async def main():
    """Main entry point."""
    global ha_client, energy_manager
    
    logger.info("Starting Smart Energy Controller...")
    
    # Load configuration
    config = load_config()
    logger.info(f"Loaded configuration: {config}")
    
    # Initialize Home Assistant client
    supervisor_token = os.environ.get('SUPERVISOR_TOKEN')
    ha_client = HomeAssistantClient(supervisor_token)
    
    # Initialize Energy Manager
    energy_manager = EnergyManager(ha_client, config)
    
    # Start automation loop in background
    asyncio.create_task(automation_loop())
    
    # Run Flask app
    logger.info("Starting web server on port 8099...")
    run_flask()


if __name__ == '__main__':
    asyncio.run(main())
