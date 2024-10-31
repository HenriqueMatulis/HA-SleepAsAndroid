"""Consts for the integration."""
import enum

DOMAIN = "sleep_as_android"
DEVICE_MACRO: str = "%%%device%%%"

DEFAULT_NAME = "SleepAsAndroid"
DEFAULT_TOPIC_TEMPLATE = "SleepAsAndroid/%s" % DEVICE_MACRO
DEFAULT_QOS = 0

# available at https://docs.sleep.urbandroid.org/services/automation.html#events
class SleepTrackingEvent(enum.Enum):
    SLEEP_TRACKING_STARTED = "sleep_tracking_started"
    SLEEP_TRACKING_STOPPED = "sleep_tracking_stopped"
    SLEEP_TRACKING_PAUSED = "sleep_tracking_paused"
    SLEEP_TRACKING_RESUMED = "sleep_tracking_resumed"
    ALARM_SNOOZE_CLICKED = "alarm_snooze_clicked"
    ALARM_SNOOZE_CANCELED = "alarm_snooze_canceled"
    TIME_TO_BED_ALARM_ALERT = "time_to_bed_alarm_alert"
    ALARM_ALERT_START = "alarm_alert_start"
    ALARM_ALERT_DISMISS = "alarm_alert_dismiss"
    ALARM_SKIP_NEXT = "alarm_skip_next"
    SHOW_SKIP_NEXT_ALARM = "show_skip_next_alarm"
    REM = "rem"
    SMART_PERIOD = "smart_period"
    BEFORE_SMART_PERIOD = "before_smart_period"
    LULLABY_START = "lullaby_start"
    LULLABY_STOP = "lullaby_stop"
    LULLABY_VOLUME_DOWN = "lullaby_volume_down"
    DEEP_SLEEP = "deep_sleep"
    LIGHT_SLEEP = "light_sleep"
    AWAKE = "awake"
    NOT_AWAKE = "not_awake"
    APNEA_ALARM = "apnea_alarm"
    ANTISNORING = "antisnoring"
    SOUND_EVENT_SNORE = "sound_event_snore"
    SOUND_EVENT_TALK = "sound_event_talk"
    SOUND_EVENT_COUGH = "sound_event_cough"
    SOUND_EVENT_BABY = "sound_event_baby"
    SOUND_EVENT_LAUGH = "sound_event_laugh"
    BEFORE_ALARM = "before_alarm"
    ALARM_RESCHEDULED = "alarm_rescheduled"


sleep_tracking_events = [e.value for e in SleepTrackingEvent]
