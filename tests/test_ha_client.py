"""Unit tests for ha_client module."""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from ha_client import HomeAssistantClient  # noqa: E402


class TestHomeAssistantClient(unittest.TestCase):
    """Test cases for HomeAssistantClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = HomeAssistantClient("test_token")

    def test_initialization(self):
        """Test client initialization."""
        self.assertEqual(self.client.token, "test_token")
        self.assertEqual(self.client.base_url, "http://supervisor/core/api")
        self.assertIn("Authorization", self.client.headers)

    @patch("ha_client.requests.get")
    def test_get_states(self, mock_get):
        """Test getting states."""
        mock_response = Mock()
        mock_response.json.return_value = [{"entity_id": "switch.test", "state": "on"}]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        states = self.client.get_states()
        self.assertEqual(len(states), 1)
        self.assertEqual(states[0]["entity_id"], "switch.test")

    @patch("ha_client.requests.get")
    def test_get_state(self, mock_get):
        """Test getting single state."""
        mock_response = Mock()
        mock_response.json.return_value = {"entity_id": "switch.test", "state": "on"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        state = self.client.get_state("switch.test")
        self.assertEqual(state["entity_id"], "switch.test")
        self.assertEqual(state["state"], "on")

    @patch("ha_client.requests.get")
    def test_get_devices(self, mock_get):
        """Test getting devices."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"entity_id": "switch.test", "state": "on", "attributes": {"friendly_name": "Test Switch"}},
            {"entity_id": "sensor.temperature", "state": "20", "attributes": {}},
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        devices = self.client.get_devices()
        # Should only return controllable devices (switch, light, button)
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0]["entity_id"], "switch.test")

    @patch("ha_client.requests.post")
    def test_call_service(self, mock_post):
        """Test calling a service."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client.call_service("switch", "turn_on", "switch.test")
        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch("ha_client.requests.post")
    def test_turn_on(self, mock_post):
        """Test turning on a device."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client.turn_on("switch.test")
        self.assertTrue(result)

    @patch("ha_client.requests.post")
    def test_turn_off(self, mock_post):
        """Test turning off a device."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client.turn_off("switch.test")
        self.assertTrue(result)

    @patch("ha_client.requests.get")
    def test_get_sensor_value(self, mock_get):
        """Test getting sensor value."""
        mock_response = Mock()
        mock_response.json.return_value = {"state": "42.5"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        value = self.client.get_sensor_value("sensor.test")
        self.assertEqual(value, 42.5)


if __name__ == "__main__":
    unittest.main()
