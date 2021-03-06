import re
import logging
import datetime
import pytz

def logline_to_dict(logline: str) -> dict:
    data = {}
    pairs = re.split('(?<!:):(?!:)', logline.strip())
    for p in pairs:
        p = p.replace('::',':')
        keyval = p.split('=')
        try:
            data[keyval[0]] = keyval[1]
        except IndexError as e:
            logging.error('error "{}" in keyval "{}", logline "{}"'.format(e,keyval,logline))
    return data

def crawl_date_to_datetime(d: str) -> datetime.datetime:
    """Converts a crawl date string to a datetime object.
    Note: crawl dates use a 0-indexed month... I think you can blame struct_tm
    for this.
    """
    # Increment the month by one
    d = d[:4] + '%02d' % (int(d[4:6]) + 1) + d[6:]
    return datetime.datetime(
        year=int(d[:4]),
        month=int(d[4:6]),
        day=int(d[6:8]),
        hour=int(d[8:10]),
        minute=int(d[10:12]),
        second=int(d[12:14]),
        tzinfo=pytz.utc)
