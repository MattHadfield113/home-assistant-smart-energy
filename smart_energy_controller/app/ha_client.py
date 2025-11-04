"""Home Assistant API client."""

import logging

import requests

logger = logging.getLogger(__name__)


class HomeAssistantClient:
    """Client for communicating with Home Assistant API."""

    def __init__(self, token):
        """Initialize the client."""
        self.token = token
        self.base_url = "http://supervisor/core/api"
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def get_states(self):
        """Get all states from Home Assistant."""
        try:
            response = requests.get(f"{self.base_url}/states", headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting states: {e}")
            return []

    def get_state(self, entity_id):
        """Get state of a specific entity."""
        try:
            response = requests.get(f"{self.base_url}/states/{entity_id}", headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting state for {entity_id}: {e}")
            return None

    def get_devices(self):
        """Get all controllable devices (switches, lights, buttons)."""
        states = self.get_states()
        devices = []

        for state in states:
            entity_id = state.get("entity_id", "")
            domain = entity_id.split(".")[0] if "." in entity_id else ""

            # Filter for controllable devices
            if domain in ["switch", "light", "button", "input_boolean"]:
                devices.append(
                    {
                        "entity_id": entity_id,
                        "name": state.get("attributes", {}).get("friendly_name", entity_id),
                        "state": state.get("state"),
                        "domain": domain,
                        "attributes": state.get("attributes", {}),
                    }
                )

        return devices

    def call_service(self, domain, service, entity_id=None, service_data=None):
        """Call a Home Assistant service."""
        try:
            data = service_data or {}
            if entity_id:
                data["entity_id"] = entity_id

            response = requests.post(
                f"{self.base_url}/services/{domain}/{service}", headers=self.headers, json=data, timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error calling service {domain}.{service}: {e}")
            return False

    def turn_on(self, entity_id):
        """Turn on a device."""
        domain = entity_id.split(".")[0]
        return self.call_service(domain, "turn_on", entity_id)

    def turn_off(self, entity_id):
        """Turn off a device."""
        domain = entity_id.split(".")[0]
        return self.call_service(domain, "turn_off", entity_id)

    def get_sensor_value(self, entity_id):
        """Get numeric value from a sensor."""
        state = self.get_state(entity_id)
        if state:
            try:
                return float(state.get("state", 0))
            except (ValueError, TypeError):
                logger.warning(f"Could not convert sensor value to float: {entity_id}")
                return 0.0
        return 0.0

    def set_state(self, entity_id, state_data):
        """Set state of an entity (for publishing sensors)."""
        try:
            response = requests.post(
                f"{self.base_url}/states/{entity_id}", headers=self.headers, json=state_data, timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error setting state for {entity_id}: {e}")
            return False
