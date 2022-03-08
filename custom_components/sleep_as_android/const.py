"""Consts for the integration."""

from .sensor import SleepAsAndroidSensor
from .alarm_sensor import SleepAsAndroidAlarmSensor

DOMAIN = "sleep_as_android"
DEVICE_MACRO: str = "%%%device%%%"

DEFAULT_NAME = "SleepAsAndroid"
DEFAULT_TOPIC_TEMPLATE = "SleepAsAndroid/%s" % DEVICE_MACRO
DEFAULT_ALARM_TOPIC_TEMPLATE = "%s/alarms" % DEFAULT_TOPIC_TEMPLATE
DEFAULT_QOS = 0


STATE_SENSOR = SleepAsAndroidSensor
ALARMS_SENSOR = SleepAsAndroidAlarmSensor