"""Sensor for Sleep as android states."""

import abc
import json
import logging
from typing import TYPE_CHECKING, Any, Dict

from homeassistant.components import mqtt 
from homeassistant.components.sensor import RestoreSensor, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_entries_for_config_entry

from .const import DOMAIN, sleep_tracking_events
from .device_trigger import TRIGGERS

if TYPE_CHECKING:
    from . import SleepAsAndroidInstance

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    instance: SleepAsAndroidInstance = hass.data[DOMAIN][config_entry.entry_id]
    await instance.subscribe_root_topic(async_add_entities)
    return True


class SleepAsAndroidSensor(abc.ABC, RestoreSensor):
    """Sensor for the integration."""
    _attr_should_poll = False
    _attr_has_entity_name = True
    

    def __init__(self, device: str, name: str):
        self._device = device
        self._name: str = name
        self._attr_name = name

    async def async_added_to_hass(self):
        """Restore any data that already exists """
        await super().async_added_to_hass()
        if (old_state := await self.async_get_last_sensor_data()) is not None:
            self._attr_native_value = old_state.native_value
            self.async_write_ha_state()

    def process_message(self, msg: mqtt.models.ReceiveMessage):
        """Process new MQTT messages."""
        _LOGGER.debug(f"Processing message {msg}")
        try:
            payload = json.loads(msg.payload)
        except json.decoder.JSONDecodeError:
            _LOGGER.warning("expected JSON payload. got '%s' instead", msg.payload)
            return
        # See https://docs.sleep.urbandroid.org/services/mqtt.html#format-of-the-post-request
        if 'event' not in payload:
            _LOGGER.warning("Got unexpected payload: '%s'", payload)
            return
        event = payload.pop('event')
        self._process_message(event, payload)

    @abc.abstractmethod
    def _process_message(self, event: str, values: Dict[str, str]):
        """Process new MQTT messages."""
        pass

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._device}_{self._name}"

    @property
    def device_info(self):
        """Device info for sensor."""
        return {"identifiers": {(DOMAIN, self._device)}}

class SleepAsAndroidLastEvent(SleepAsAndroidSensor):
    """Last event received from Sleep as Android.
    """
    _attr_icon = "mdi:arrow-right-thick"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [
        STATE_UNKNOWN,
        *sleep_tracking_events,
    ]

    def __init__(self, device: str):
        super().__init__(device, "last_event")
        self._attr_native_value: str = STATE_UNKNOWN
        self._attr_extra_state_attributes = {}

    def _process_message(self, event: str, values: Dict[str, str]):
        self._attr_extra_state_attributes = values
        _LOGGER.warning("_attr_options '%s' ", self._attr_options)
        if self.state != event:
            self._attr_native_value = event
            self.async_write_ha_state()