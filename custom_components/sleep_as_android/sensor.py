"""Sensor for Sleep as android states."""

import abc
import enum
import json
import logging
from typing import TYPE_CHECKING, Any, Dict

from homeassistant.components import mqtt 
from homeassistant.components.sensor import RestoreSensor, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry, entity_platform, device_registry
from .const import DOMAIN, SleepTrackingEvent

if TYPE_CHECKING:
    from . import SleepAsAndroidInstance

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: entity_platform.AddEntitiesCallback):
    instance: SleepAsAndroidInstance = hass.data[DOMAIN][config_entry.entry_id]
    entities = entity_registry.async_entries_for_config_entry(
        instance.entity_registry, config_entry.entry_id
    )

    dr = device_registry.async_get(hass)
    sensors = []
    for entity in entities:
        device_name = dr.async_get(entity.device_id)
        s, is_new = instance.get_sensors(device_name)
        if is_new:
            sensors.extend(s)
    async_add_entities(sensors)
    platform = entity_platform.async_get_current_platform()
    await instance.subscribe_root_topic(platform)
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
        if event == 'Unknown':
            _LOGGER.warning("Successfuly got testing message: '%s'", msg.payload)
        else:
            self._process_message(SleepTrackingEvent(event), payload)

    @abc.abstractmethod
    def _process_message(self, event: SleepTrackingEvent, values: Dict[str, str]):
        """Process new MQTT messages."""
        pass

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._device}_{self._name}"

    @property
    def device_info(self):
        """Device info for sensor."""
        return {
            "identifiers": {(DOMAIN, self._device)},
            "connections": set(),
            "name": self._device
            }


class SleepAsAndroidState(SleepAsAndroidSensor):
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(self, device: str, name: str, icon: str, mapping: Dict[SleepTrackingEvent, str]):
        super().__init__(device, name)
        self._attr_native_value: str = STATE_UNKNOWN
        self._attr_icon = icon
        self._attr_options = [
            STATE_UNKNOWN,
            *mapping.values()
        ]
        self._mapping = mapping

    def _process_message(self, event: SleepTrackingEvent, _values):
        if event in self._mapping:
            self._attr_native_value = self._mapping[event]
            self.async_write_ha_state()


class SleepAsAndroidLastEvent(SleepAsAndroidState):
    """Last event received from Sleep as Android."""
    def __init__(self, device: str):
        mapping = {e: e.value for e in SleepTrackingEvent}
        super().__init__(device, "last_event", "mdi:arrow-right-thick", mapping)

    def _process_message(self, event: SleepTrackingEvent, values: Dict[str, str]):
        self._attr_extra_state_attributes = values
        super()._process_message(event, values)


class SleepAsAndroidIsAsleep(SleepAsAndroidState):
    def __init__(self, device: str):
        mapping = {
            SleepTrackingEvent.AWAKE: 'awake',
            SleepTrackingEvent.NOT_AWAKE: 'sleeping',
            SleepTrackingEvent.SLEEP_TRACKING_STOPPED: STATE_UNKNOWN,
            SleepTrackingEvent.SLEEP_TRACKING_PAUSED: STATE_UNKNOWN,
        }
        super().__init__(device, "is_asleep", "mdi:sleep", mapping)