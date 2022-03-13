from enum import Enum, auto, unique, IntEnum, IntFlag
from datetime import datetime


def DateTime():
    return lambda time_in_ms: None if time_in_ms <= 0 \
        else datetime.fromtimestamp(time_in_ms // 1000) \
        .replace(microsecond=(time_in_ms % 1000) * 1000)


class DaysOfWeekFlag(IntFlag):
    MONDAY = 0x01
    TUESDAY = 0x02
    WEDNESDAY = 0x04
    THURSDAY = 0x08
    FRIDAY = 0x10
    SATURDAY = 0x20
    SUNDAY = 0x40


class DaysOfWeekSet(dict):

    def __init__(self, flags: int):
        super().__init__()
        self['monday'] = bool(DaysOfWeekFlag.MONDAY & flags)
        self['tuesday'] = bool(DaysOfWeekFlag.TUESDAY & flags)
        self['wednesday'] = bool(DaysOfWeekFlag.WEDNESDAY & flags)
        self['thursday'] = bool(DaysOfWeekFlag.THURSDAY & flags)
        self['friday'] = bool(DaysOfWeekFlag.FRIDAY & flags)
        self['saturday'] = bool(DaysOfWeekFlag.SATURDAY & flags)
        self['sunday'] = bool(DaysOfWeekFlag.SUNDAY & flags)


class Repeat(object):

    def __init__(self, data):
        super().__init__()
        self.value = RepeatEnum(data['weekRepeat'])
        start_from = -1
        if data['weekRepeat'] == 3:
            self.times = data['nonWeeklyRepeat']
            start_from = data['nonWeeklyFrom']
        else:
            self.times = DaysOfWeekSet(data['days'])
        self.start_from = DateTime()(start_from)

    def to_json(self):
        return {
            'value': self.value.name,
            'times': self.times,
            'start_from': self.start_from,
        }


class RepeatEnum(IntEnum):
    NONE = -1
    WEEKLY = 0
    ODD_WEEK = 1
    EVEN_WEEK = 2
    NON_WEEKLY = 3


class ExtendedConfig:

    def __init__(self, data):
        super().__init__()
        self.volume_increase = VolumeIncrease(data['gradualVolumeIncrease'])
        self.snooze = Snooze(**{key: value for key, value in data.items() if str(key).startswith(
            'snooze')})
        self.delayed_start = DelayedStart(data['soundDelay'])
        self.self_disposable = bool(data['isSelfDisposable'])
        self.terminate_tracking = bool(data['terminatesTracking'])
        self.vibration = Vibrate(data['vibrationStart'])
        self.vibration_wearable = Vibrate(data['vibrationStartSmartWatch'])
        self.last_enabled = DateTime()(data['lastEnableTimestamp'])

    def __str__(self) -> str:
        return super().__str__()


class VolumeIncrease(IntFlag):
    DEFAULT = -2
    DISABLED = -1
    ENABLED = 0

    def __new__(cls, value):
        if value < 0:
            return super().__new__(cls, value)
        else:
            obj = int.__new__(cls, value)
            # obj._value_ = value
            return obj


class Snooze:

    def __init__(self, **snooze_data):
        super().__init__()
        self.after_alarm = SnoozeAfterAlarm(snooze_data['snoozeAfterAlarm'])
        self.duration = SnoozeDuration(snooze_data['snoozeDuration'])
        self.limit = SnoozeLimit(snooze_data['snoozeLimit'])
        self.total_time_limit = SnoozeDuration(snooze_data['snoozeTotalTimeLimit'])


class SnoozeAfterAlarm(IntFlag):
    DEFAULT = -2
    DISABLED = 0
    ENABLED = 1


class SnoozeDuration(IntFlag):
    DEFAULT = -2
    LAST_USED = -1
    DISABLED = 0
    ENABLED = 1

    def __new__(cls, value):
        if value <= 0:
            return super().__new__(cls, value)
        else:
            obj = int.__new__(cls, value)
            # obj._value_ = value
            return obj


class SnoozeLimit(IntFlag):
    DEFAULT = -2
    NO_LIMIT = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class DelayedStart(IntFlag):
    DEFAULT = -2
    FROM_START = -1
    ENABLED = 0

    def __new__(cls, value):
        if value < 0:
            return super().__new__(cls, value)
        else:
            obj = int.__new__(cls, value)
            # obj._value_ = value
            return obj


class Vibrate(IntFlag):
    DEFAULT = -2
    DISABLED = -1
    FROM_START = 0
    ENABLED = 1

    def __new__(cls, value):
        if value <= 0:
            return super().__new__(cls, value)
        else:
            obj = int.__new__(cls, value)
            # obj._value_ = value
            return obj


class TimeToBed(IntFlag):
    DEFAULT = -2
    DISABLED = -1
    ENABLED = 0

    def __new__(cls, value):
        if value < 0:
            return super().__new__(cls, value)
        else:
            obj = int.__new__(cls, value)
            # obj._value_ = value
            return obj


class Captcha(IntFlag):
    DEFAULT = -1
    DISABLED = 0
    SIMPLE_MATH = 1
    TYPED_MATH = 2
    SLEEPING_SHEEP = 3
    QR_BARCODE = 4
    NFC_TAG = 5
    SHAKE_IT = 6
    DREAM_DIARY = 7
    SAY_CHEESE = 8
    LAUGH_OUT_LOUD = 9
