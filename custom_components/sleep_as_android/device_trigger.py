"""Triggers for Sleep As Android."""
import logging

from homeassistant.components.device_automation import (
    DEVICE_TRIGGER_BASE_SCHEMA as HA_TRIGGER_BASE_SCHEMA,
)
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_PLATFORM,
    CONF_TYPE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
import voluptuous as vol

from .const import DOMAIN, sleep_tracking_events

_LOGGER = logging.getLogger(__name__)

TRIGGERS = sleep_tracking_events + [STATE_UNKNOWN]

TRIGGER_SCHEMA = HA_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(TRIGGERS),
    }
)


async def async_get_triggers(hass, device_id):
    """Return a list of triggers."""

    triggers = []

    for t in TRIGGERS:
        triggers.append(
            {
                # Required fields of TRIGGER_BASE_SCHEMA
                CONF_PLATFORM: "device",
                CONF_DOMAIN: DOMAIN,
                CONF_DEVICE_ID: device_id,
                # Required fields of TRIGGER_SCHEMA
                CONF_TYPE: t,
            }
        )

    return triggers


async def async_attach_trigger(hass: HomeAssistant, config, action, automation_info):
    """Attach a trigger."""
    config = TRIGGER_SCHEMA(config)
    _LOGGER.debug("Got subscription to trigger: %s", config)
    event_config = event_trigger.TRIGGER_SCHEMA(
        {
            event_trigger.CONF_PLATFORM: "event",
            event_trigger.CONF_EVENT_TYPE: DOMAIN + "_event",
            event_trigger.CONF_EVENT_DATA: {
                CONF_DEVICE_ID: config[CONF_DEVICE_ID],
                CONF_TYPE: config[CONF_TYPE],
            },
        }
    )

    return await event_trigger.async_attach_trigger(
        hass, event_config, action, automation_info, platform_type="device"
    )
