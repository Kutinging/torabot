import pytz
from datetime import datetime


def tokyo_to_utc(dt):
    local = pytz.timezone('Asia/Tokyo')
    local_dt = local.localize(dt, is_dst=None)
    return local_dt.astimezone(pytz.utc)


def utc_to_tokyo(dt):
    return dt.astimezone(pytz.timezone('Asia/Tokyo'))


def _utcnow():
    return datetime.now(pytz.utc)


def utcnow():
    return _utcnow()
