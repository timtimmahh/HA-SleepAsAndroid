from enum import IntEnum, auto
from .sleep import SleepTrackerSensor
from .alarm import SleepAlarmSensor

DOMAIN = "sleep_as_ha"
DEVICE_MACRO: str = "%%%device%%%"

DEFAULT_NAME = "SleepAsHA"
DEFAULT_TOPIC_TEMPLATE = "SleepAsHA/%s" % DEVICE_MACRO
DEFAULT_ALARM_TOPIC_TEMPLATE = "%s/alarms" % DEFAULT_TOPIC_TEMPLATE
DEFAULT_QOS = 0
