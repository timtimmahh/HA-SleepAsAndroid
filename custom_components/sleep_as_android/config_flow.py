"""Configuration via UI for the integration."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any

from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DEFAULT_NAME, DEFAULT_QOS, DEFAULT_TOPIC_TEMPLATE, DOMAIN, CONF_ALARMS, \
    DEFAULT_ALARM_LABEL, CONF_ALARM_TIME_FMT, CONF_ALARM_DATE_FMT, CONF_ALARM_LABEL, \
    CONF_ALARM_TIME, CONF_ALARM_DATE, CONF_ALARM_REPEAT, CONF_ALARM_ADD_ANOTHER


def get_value(config_entry: config_entries | None, param: str, default=None):
    """Get current value for configuration parameter.
    :param config_entry: config_entries|None: config entry from Flow
    :param param: str: parameter name for getting value
    :param default: default value for parameter, defaults to None
    :returns: parameter value, or default value or None
    """
    if config_entry is not None:
        return config_entry.options.get(param, config_entry.data.get(param, default))
    else:
        return default


def create_schema(
        config_entry: config_entries | None, step: str = "user"
) -> vol.Schema:
    """Generate configuration schema.
    :param config_entry: config_entries|None: config entry from Flow
    :param step: stem name
    """
    schema = vol.Schema({})
    if step == "user":
        schema = schema.extend(
            {
                vol.Required(
                    "name",
                    default=get_value(
                        config_entry=config_entry, param="name", default=DEFAULT_NAME
                    ),
                ): cv.string,
            }
        )

    if step != "alarm":
        schema = schema.extend(
            {
                vol.Required(
                    "topic_template",
                    default=get_value(
                        config_entry=config_entry,
                        param="topic_template",
                        default=DEFAULT_TOPIC_TEMPLATE,
                    ),
                ): cv.string,
                vol.Optional(
                    "qos",
                    default=get_value(
                        config_entry=config_entry, param="qos", default=DEFAULT_QOS
                    ),
                ): int,
            }
        )
    else:
        schema = schema.extend(
            {
                vol.Optional(CONF_ALARM_LABEL, default=""): cv.string,
                vol.Required(CONF_ALARM_TIME, default=datetime.now().strftime(CONF_ALARM_TIME_FMT)):
                    cv.time,
                vol.Required(CONF_ALARM_DATE, default=datetime.now().strftime(CONF_ALARM_DATE_FMT)):
                    cv.date,
                vol.Required(CONF_ALARM_REPEAT, default=["Sunday"]): cv.multi_select({
                    "Sunday": False,
                    "Monday": False,
                    "Tuesday": False,
                    "Wednesday": False,
                    "Thursday": False,
                    "Friday": False,
                    "Saturday": False,
                }),
                vol.Optional(CONF_ALARM_ADD_ANOTHER, default=False): cv.boolean
            }
        )
    return schema


class SleepAsAndroidConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """First time set up flow."""

    def __init__(self) -> None:
        self._config_entry: config_entries | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SleepAsAndroidOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            # self.data = user_input
            # self.data[CONF_ALARMS] = []
            # return await self.async_step_alarm()
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=create_schema(None, step="user")
        )


class SleepAsAndroidOptionsFlow(config_entries.OptionsFlow):
    """Changing options flow."""

    data: Dict[str, Any]

    def __init__(self, config_entry):
        """Initialize options flow."""
        super().__init__()
        self._config_entry = config_entry
        self._entry_id = config_entry.entry_id

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        if user_input is not None:
            self.data = user_input
            self.data[CONF_ALARMS] = []
            return await self.async_step_alarm()
            #self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=create_schema(self._config_entry, step="init"),
            errors=errors,
        )

    async def async_step_alarm(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to add alarms."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                self.data[CONF_ALARMS].append({
                    "label": user_input.get(CONF_ALARM_LABEL, ""),
                    "time": user_input[CONF_ALARM_TIME],
                    "date": user_input[CONF_ALARM_DATE],
                    "repeat": user_input.get(CONF_ALARM_REPEAT, []),
                })
            except Exception as err:
                print(err)

            if user_input.get(CONF_ALARM_ADD_ANOTHER, False):
                return await self.async_step_alarm()

            return self.async_create_entry(title="",
                                           data=self.data)

        return self.async_show_form(step_id="alarm", data_schema=create_schema(self._config_entry,
                                                                               step="alarm"),
                                    errors=errors)
