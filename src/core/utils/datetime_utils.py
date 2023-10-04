import typing
from datetime import datetime, tzinfo, timedelta

from dateutil import tz


REFRESH_THRESHOLD = timedelta(seconds=20)


DATE_FORMAT = r"%d.%m.%y"
DATE_FORMAT_USER = "dd.mm.yy"

TIME_FORMAT = r"%H:%M"
TIME_FORMAT_USER = "hh:mm"

DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"
DATETIME_FORMAT_USER = f"{DATE_FORMAT_USER} {TIME_FORMAT_USER}"

LOCATION = "Europe/Moscow"


def get_tz(location: str) -> tzinfo:
    result = tz.gettz(location)
    assert result is not None
    return result


tz_game = get_tz(LOCATION)
tz_utc = get_tz("UTC")
tz_local = typing.cast(tzinfo, tz.gettz())


def add_timezone(dt: datetime, timezone: tzinfo = tz_game) -> datetime:
    return datetime.combine(dt.date(), dt.time(), timezone)


def trim_tz(dt: datetime) -> datetime:
    internal = dt.astimezone(tz=tz_game)
    return datetime.combine(date=internal.date(), time=internal.time())
