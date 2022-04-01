"""Consts for the integration."""

DOMAIN = "sleep_as_android"
DEVICE_MACRO: str = "%%%device%%%"

DEFAULT_NAME = "SleepAsAndroid"
DEFAULT_TOPIC_TEMPLATE = "SleepAsAndroid/%s" % DEVICE_MACRO
DEFAULT_QOS = 0
DEFAULT_ALARM_LABEL = ""

CONF_ALARMS = "alarms"
CONF_ALARM_TIME_FMT = "%H:%M"
CONF_ALARM_DATE_FMT = "%Y-%m-%d"
CONF_ALARM_LABEL = "label"
CONF_ALARM_TIME = "time"
CONF_ALARM_DATE = "date"
CONF_ALARM_REPEAT = "repeat"
CONF_ALARM_ADD_ANOTHER = "add_another"
