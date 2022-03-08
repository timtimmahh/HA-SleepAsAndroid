"""Sensor for Sleep as Android alarms."""

import json
import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_registry import async_entries_for_config_entry
from homeassistant.helpers.restore_state import RestoreEntity

from .sensor import SleepAsAndroidSensor
from .const import DOMAIN
from .device_trigger import TRIGGERS


if TYPE_CHECKING:
    from . import SleepAsAndroidInstance

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up the sensor entry."""

    async def add_configured_entities():
        """Scan entity registry and add previously created entities to Home Assistant."""

        entities = async_entries_for_config_entry(
            instance.entity_registry, config_entry.entry_id
        )
        sensors: list[SleepAsAndroidAlarmSensor] = []
        for entity in entities:

            device_name = instance.device_name_from_entity_id(entity.unique_id)
            _LOGGER.debug(
                f"add_configured_entities: creating sensor with name {device_name}"
            )
            (sensor, _) = instance.get_sensor(device_name)
            sensors.append(sensor)

        async_add_entities(sensors)

    instance: SleepAsAndroidInstance = hass.data[DOMAIN][config_entry.entry_id]
    await add_configured_entities()
    _LOGGER.debug("async_setup_entry: adding configured entities is finished.")
    _LOGGER.debug("Going to subscribe to root topic.")
    await instance.subscribe_root_topic(async_add_entities)
    _LOGGER.debug("async_setup_entry is finished")
    return True


class SleepAsAndroidAlarmSensor:
    """Sensor for alarm integration."""

    """Mapping for value*.

  It is comfortable to have human readable names.
  Keys is field names from SleepAsAndroid event https://docs.sleep.urbandroid.org/services/automation.html#events
  Values is sensor attributes.
  """
    _attr_icon = "mdi:alarm"
    _attr_should_poll = False
    _attr_device_class = f"{DOMAIN}__status"

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, name: str):
        """Initialize entry."""
        super().__init__(hass, config_entry, name)

    @property
    def __additional_attributes(self) -> dict[str, str]:
        return {
            attr: attr
            for attr in (
                "hour",  #: Int,
                "minutes",  #: Int,
                "daysOfWeek",  #: Int,
                "alarmTime",  #: Int,
                "enabled",  #: Int,
                "vibrate",  #: Int,
                "message",  #: String,
                "alert",  #: String,
                "suspendTime",  #: Int,
                "nonDeepSleepWakeupWindow",  #: Int,
            )
        }

    def process_message(self, msg):
      """Process new MQTT messages for alarms.

      Set sensor state, attributes and fire events.

      :param msg: MQTT message
      """
      _LOGGER.debug('Processing message %s', msg)
      try:
        new_state = STATE_UNKNOWN
        payload = json.loads(msg.payload)
        try:
          new_state = payload[""]
      except json.decoder.JSONDecodeError:
        _LOGGER.warning("expected JSON payload. got '%s' instead", msg.payload)
