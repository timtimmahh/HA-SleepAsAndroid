import json
import logging
from turtle import st
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Any, Tuple, Union

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_registry import async_entries_for_config_entry
from homeassistant.helpers.restore_state import RestoreEntity

import voluptuous as vol

from .sleep_as_ha import SleepAsHAInstance
from .schema_mappings import Repeat, DateTime, ExtendedConfig, Captcha
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
ALARM_SCHEMA = vol.Schema({
    vol.Required("id", default=-1): vol.Number(),
    vol.Required("hour"): vol.All(vol.Number(), vol.Range(min=0, max=23)),
    vol.Required("minutes"): vol.All(vol.Number(), vol.Range(min=0, max=59)),
    vol.Required("daysOfWeek"): (lambda days_of_week: Repeat(days_of_week)),
    vol.Optional("label"): vol.Title,
    vol.Optional("enabled", default=True): vol.Boolean(),
    vol.Optional("silent", default=False): vol.Boolean(),
    vol.Optional("legacyVibrate", default=True): vol.Boolean(),
    vol.Optional("captcha"): (lambda captcha: Captcha(captcha)),
    vol.Optional("alert"): str,
    vol.Optional("extendedConfig"): (lambda ext: ExtendedConfig(ext)),
    vol.Optional("suspendTime", default=-1): DateTime(),
    vol.Optional("time"): DateTime()
}, extra=True)

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up the sensor entry."""

    async def add_configured_entities():
        """Scan entity registry and add previously created entities to Home Assistant."""

        entities = async_entries_for_config_entry(
            instance.entity_registry, config_entry.entry_id
        )
        sensors: list[SleepAlarmSensor] = []
        for entity in entities:

            device_name = instance.device_name_from_entity_id(entity.unique_id)
            _LOGGER.debug(
                f"add_configured_entities: creating sensor with name {device_name}"
            )
            (sensor, _) = instance.get_alarm_sensor(device_name)
            sensors.append(sensor)

        async_add_entities(sensors)

    instance: SleepAsHAInstance = hass.data[DOMAIN][config_entry.entry_id]
    await add_configured_entities()
    _LOGGER.debug("async_setup_entry: adding configured entities is finished.")
    _LOGGER.debug("Going to subscribe to root topic.")
    await instance.subscribe_root_topic(async_add_entities)
    _LOGGER.debug("async_setup_entry is finished")
    return True


class AlarmData:

    def __init__(self, data: Dict[str, Any]) -> None:
        super().__init__()
        _schema = ALARM_SCHEMA(data)
        self.id: int = _schema['id']
        self.hour: int = _schema['hour']
        self.minutes: int = _schema['minutes']
        self.daysOfWeek: Repeat = _schema['daysOfWeek']
        self.label: str = _schema['label']
        self.enabled: bool = _schema['enabled']
        self.silent: bool = _schema['silent']
        self.vibrate: bool = _schema['legacyVibrate']
        self.captcha: Captcha = _schema['captcha']
        self.alert: str = _schema['alert']
        self.extendedConfig: ExtendedConfig = _schema['extendedConfig']
        self.suspendTime: datetime = _schema['suspendTime']
        self.time: datetime = _schema['time']


class SleepAlarmSensor(BinarySensorEntity, RestoreEntity):

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, name: str, alarm_data:
    AlarmData):
        """Initialize entry."""
        self._instance: SleepAsHAInstance = hass.data[DOMAIN][
            config_entry.entry_id
        ]

        self.hass: HomeAssistant = hass

        self._name = name
        self._alarm_data: AlarmData = alarm_data
        self._device_id: str = "unknown"
        self._attr_extra_state_attributes = {}
        self._set_attributes(
            {}
        )  # initiate _attr_extra_state_attributes with empty values
        _LOGGER.debug(f"Creating sensor with name {alarm_data.id}")

    async def async_added_to_hass(self):
        """When sensor added to Home Assistant.

        Should create device for sensor here
        """
        await super().async_added_to_hass()
        device_registry = await dr.async_get_registry(self.hass)
        device = device_registry.async_get_device(
            identifiers=self.device_info["identifiers"], connections=set()
        )
        _LOGGER.debug("My device id is %s", device.id)
        self._device_id = device.id

        if (old_state := await self.async_get_last_state()) is not None:
            self._alarm_data.enabled = old_state.state
            _LOGGER.debug(
                f"async_added_to_hass: restored previous state for {self.name}: {self.state}"
            )
        else:
            # No previous state. It is fine, but it would be nice to report
            _LOGGER.debug(
                f"async_added_to_hass: no previously saved state for {self.name}"
            )

        self.async_write_ha_state()

    async def async_will_remove_from_hass(self):
        """When sensor is removed from Home Assistant.

        Should remove device here
        """
        # ToDo: should we remove device?
        pass

    @property
    def name(self):
        """Return the name of the sensor."""
        return f'{self._instance.create_entity_id(self._name)}{self._alarm_data.id}'

    @property
    def is_on(self) -> Union[bool, None]:
        return self._alarm_data.enabled

    def turn_on(self, **kwargs: Any) -> None:
        self._alarm_data.enabled = True
        self._update_alarm_state()

    def turn_off(self, **kwargs: Any) -> None:
        self._alarm_data.enabled = False
        self._update_alarm_state()

    def _update_alarm_state(self):
        self.async_write_ha_state()

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._instance.create_entity_id(self._name)

    @property
    def available(self) -> bool:
        """Is sensor available or not."""
        return self.state != STATE_OFF and self.state != STATE_UNKNOWN

    @property
    def device_id(self) -> str:
        """Device identification for sensor."""
        return self._device_id

    @property
    def device_info(self):
        """Device info for sensor."""
        _LOGGER.debug("My identifiers is %s", {(DOMAIN, self.unique_id)})
        info = {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "SleepAsHA",
            "type": None,
            "model": "MQTT",
        }
        return info

    def process_message(self, msg: AlarmData):
        """Process new MQTT messages.

        Set sensor state, attributes and fire events.

        :param msg: MQTT message
        :param triggers: event triggers
        """
        _LOGGER.debug(f"Processing message {msg}")
        try:
            new_state = self.state
            try:
                new_state = msg.enabled
            except KeyError:
                _LOGGER.warning("Got unexpected payload: '%s'", msg)

            self._set_attributes(msg.__dict__)
            if new_state:
                self.turn_on()
            else:
                self.turn_off()
            self._fire_event(self.state)
            # if triggers is not None:
            # self._fire_trigger(self.state, triggers)

        except json.decoder.JSONDecodeError:
            _LOGGER.warning("expected JSON payload. got '%s' instead", msg.payload)

    def _fire_event(self, event_payload: str):
        """Fire event with payload {'event': event_payload}.

        :param event_payload: payload for event
        """
        payload = {"event": event_payload}
        _LOGGER.debug("Firing '%s' with payload: '%s'", self.name, payload)
        self.hass.bus.fire(self.name, payload)

    def _fire_trigger(self, new_state: str, triggers: list[str]):
        """Fire trigger based on new state.

        :param new_state: type of trigger to fire
        """
        if new_state in triggers:
            self.hass.bus.async_fire(
                DOMAIN + "_event", {"device_id": self.device_id, "type": new_state}
            )
        else:
            _LOGGER.warning(
                "Got %s event, but it is not in TRIGGERS list: will not fire this event for "
                "trigger!",
                new_state,
            )

    def _set_attributes(self, payload: dict):
        new_attributes = {}
        for k, v in self.__additional_attributes.items():
            new_attributes[v] = payload.get(k, STATE_UNAVAILABLE)
        _LOGGER.debug(f"New attributes is {new_attributes}")
        return self._attr_extra_state_attributes.update(new_attributes)

    @property
    def __additional_attributes(self) -> Dict[str, Any]:
        return {key: value for key, value in self._alarm_data.__dict__.items() if
                key not in ('id', 'enabled')}
