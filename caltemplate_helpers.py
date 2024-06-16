from typing import Tuple, List, Dict, Any
from datetime import datetime, timedelta
from icalendar import Event

kWdayMap = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
kStartHr = 8
kEndHr = 20


def split_title(title: str) -> List[str]:
  out = title.split('\n')
  if len(out) < 2:
    out.append('')
  return out

def time_elts(start_dt: datetime, end_dt: datetime) -> List[Tuple[float, Dict[str, Any]]]:
  """returns the time env elements between start_hr and end_hr, inclusive"""
  scale = 1.0 / (end_dt - start_dt).seconds

  def dt_to_elt_tuple(dt: datetime) -> Tuple[float, Dict[str, str]]:
    frac = (dt - start_dt).seconds * scale

    num = dt.hour % 12
    if num == 0:
      num = 12
    ampm = 'a' if dt.hour < 12 else 'p'

    return (frac, {'time': f'{num}{ampm}'})

  assert start_dt.date() == end_dt.date()
  day_dt = start_dt.replace(minute=0, hour=0, second=0, microsecond=0)
  return [dt_to_elt_tuple(day_dt + timedelta(hours=hr))
          for hr in range(start_dt.hour, end_dt.hour + 1)]  # assumes dt on hour boundary

def events_elts(events: List[Event], current_events: List[Event], start_dt: datetime, end_dt: datetime) -> List[Tuple[float, Dict[str, Any]]]:
  """returns the event elements between start_hr and end_hr, inclusive"""
  elts = []
  scale = 1.0 / (end_dt - start_dt).seconds
  for event in events:
    ev_start: datetime = event.get('DTSTART').dt
    ev_end: datetime = event.get('DTEND').dt
    if ev_end < start_dt or ev_start > end_dt:  # drop events out-of-range
      continue
    if ev_start < start_dt:  # clamp events to range
      ev_start = start_dt
    if ev_end > end_dt:
      ev_end = end_dt

    elts.append(((ev_start - start_dt).seconds * scale, {
      'title': event.get('SUMMARY'),
      'size_frac': (ev_end - ev_start).seconds * scale,
      'fill': '#ff0000' if event in current_events else '#000000',
    }))

  return elts

def duck_image(currenttime: datetime) -> str:
  # easter egg logic
  if currenttime.weekday() >= 4:  # happy duck on Fri / weekend
    return 'ext_art/sub_duck.svg'
  else:
    return 'ext_art/sub_duck_serious.svg'
