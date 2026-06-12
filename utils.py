from datetime import datetime, date, time
from streamlit_js_eval import streamlit_js_eval
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from config import ET, UTC, DEFAULT_TZ, DEFAULT_TZ_NAME, FLAGS

def now_utc():
    return datetime.now(UTC)


def now_user(user_tz):
    return datetime.now(user_tz)

def et_to_utc(year, month, day, hour, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=ET).astimezone(UTC).isoformat()

def parse_dt(dt_value, user_tz):
    if isinstance(dt_value, datetime):
        return dt_value.astimezone(user_tz)

    return datetime.fromisoformat(str(dt_value)).astimezone(user_tz)


def can_predict(match_datetime_value):
    if isinstance(match_datetime_value, datetime):
        match_dt_utc = match_datetime_value.astimezone(UTC)
    else:
        match_dt_utc = datetime.fromisoformat(str(match_datetime_value)).astimezone(UTC)

    return now_utc() < match_dt_utc


def get_browser_timezone():
    tz_name = streamlit_js_eval(
        js_expressions="Intl.DateTimeFormat().resolvedOptions().timeZone",
        key="browser_timezone",
    )

    if tz_name:
        try:
            return ZoneInfo(tz_name), tz_name
        except ZoneInfoNotFoundError:
            pass
        except Exception:
            pass

    return DEFAULT_TZ, DEFAULT_TZ_NAME

def flag(team):
    return FLAGS.get(team, "🏳️")