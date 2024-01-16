from typing import Tuple, List, Dict, Any
import datetime
from math import ceil, floor
import os.path
from urllib.request import urlopen
from icalendar import Calendar
import recurring_ical_events

WDAY_MAP = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}

ICAL_URL = "https://calendar.google.com/calendar/ical/gv8rblqs5t8hm6br9muf9uo2f0%40group.calendar.google.com/public/basic.ics"
CACHE_FILE = "cache.ics"

def get_calender():
  if not os.path.isfile(CACHE_FILE):  # fetch if needed
    print(f"fetching from {ICAL_URL}")
    data = urlopen(ICAL_URL).read()
    with open(CACHE_FILE, 'wb') as f:
      f.write(data)

  with open(CACHE_FILE, 'rb') as f:
    data = f.read()

  return Calendar.from_ical(data)


def time_elts(start_hr: float, end_hr: float) -> List[Tuple[float, Dict[str, Any]]]:
  """returns the time env elements between start_hr and end_hr, inclusive"""
  def hr_to_str(hr: float) -> str:
    num = hr % 12
    if num == 0:
      num = 12
    return f"{num}{'a' if hr < 12 else 'p'}"

  scale = 1.0 / (end_hr - start_hr)
  return [((hr - start_hr) * scale, {'time': hr_to_str(hr)})
          for hr in range(ceil(start_hr), floor(end_hr) + 1)]

def events_elts(day: datetime.datetime, start_hr: float, end_hr: float) -> List[Tuple[float, Dict[str, Any]]]:
  """returns the event elements between start_hr and end_hr, inclusive"""
  events = recurring_ical_events.of(get_calender()).between(day, day + datetime.timedelta(days=1))
  start_dt = day + datetime.timedelta(hours=start_hr)
  end_dt = day + datetime.timedelta(hours=end_hr)

  elts = []
  scale = 1.0 / (end_hr - start_hr)
  for event in events:
    ev_start: datetime.datetime = event.get('DTSTART').dt
    ev_end: datetime.datetime = event.get('DTEND').dt
    if ev_end < start_dt or ev_start > end_dt:  # drop events out-of-range
      continue
    if ev_start < start_dt:  # clamp events to range
      ev_start = start_dt
    if ev_end > end_dt:
      ev_end = end_dt

    hours = (ev_end - ev_start).seconds / 3600
    elts.append(((ev_start.hour - start_hr) * scale, {
      'title': event.get('SUMMARY'),
      'size_frac': hours / (end_hr - start_hr),
    }))

  return elts
