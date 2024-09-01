from itertools import chain
from datetime import datetime, timedelta, date
from typing import List, Tuple

import recurring_ical_events  # type: ignore
import xml.etree.ElementTree as ET
import cairosvg  # type: ignore
from PIL import Image
import icalendar
import io

# because pysvglabel isn't structured as a package, we hack around it by adding it to PYTHONPATH
# TODO clean this up by a lot
import sys

import caltemplate_helpers

sys.path.append("pysvglabel")
from labelcore import SvgTemplate

kFudgeAdvanceTime = timedelta(minutes=5)  # add this for the "current" time to account for clock drift and whatnot


def eastereggs(title: str, currenttime: datetime) -> List[Tuple[datetime, datetime, str]]:
  """Returns a list of easter eggs for the duck image. as (start, end, image) tuples."""
  day_start = currenttime.replace(hour=0, minute=0, second=0, microsecond=0)
  eggs: List[Tuple[datetime, datetime, str]] = []
  if day_start.weekday() >= 4:  # happy duck on Fri / weekend
    eggs.append((day_start, day_start+timedelta(hours=25), 'ext_art/sub_duck.svg'))
  if day_start.weekday() == 2 and title.lower().startswith('TESLA ROOM'.lower()):  # board games night
    eggs.append((day_start + timedelta(hours=18, minutes=30),
                 day_start+timedelta(hours=25), 'ext_art/sub_duck_boardgames.svg'))
  return eggs


def render(template_filename: str, calendars: List[icalendar.Calendar], events: List[icalendar.Event], title: str, currenttime: datetime) -> bytes:
  """Renders the calendar to a PNG, given the ical url and title, returning the PNG data"""
  template = SvgTemplate(template_filename)
  label = template._create_instance()

  currenttime = currenttime + kFudgeAdvanceTime
  day_start = currenttime.replace(hour=0, minute=0, second=0, microsecond=0)

  all_events = list(chain.from_iterable([recurring_ical_events.of(cal).between(day_start, day_start + timedelta(days=2))
                                         for cal in calendars] + [events]))
  events = [event for event in all_events if isinstance(event.get('DTSTART').dt, datetime)]  # filter all-day events
  day_events = [event for event in all_events if isinstance(event.get('DTSTART').dt, date) and
                event.get('DTSTART').dt == currenttime.date() and
                'first day of' not in event.get('SUMMARY').lower()]  # a bit of a hack to clean up holiday display
  current_events = [event for event in events
                    if event.get('DTSTART').dt <= currenttime and event.get('DTEND').dt > currenttime]

  duck_image = 'ext_art/sub_duck_serious.svg'  # default
  eggs = eastereggs(title, currenttime)
  for egg in eggs:
    if currenttime >= egg[0] and currenttime < egg[1]:
      duck_image = egg[2]

  instance = template.apply_instance({
    'title': title,
    'current_events': current_events,  # type: ignore
    'events': events,  # type: ignore
    'day_events': day_events,  # type: ignore
    'day': day_start,  # type: ignore
    'currenttime': currenttime,  # type: ignore
    'duck_image': duck_image,
  }, [], 0)
  label.append(instance)
  root = ET.ElementTree(label).getroot()

  png_data = cairosvg.svg2png(bytestring=ET.tostring(root, 'utf-8'))

  image = Image.open(io.BytesIO(png_data))
  image = image.convert(mode='P')  # palette conversion for additional compression
  img_byte_arr = io.BytesIO()
  image.save(img_byte_arr, format='PNG', optimize=True)
  png_data = img_byte_arr.getvalue()

  return png_data


def next_update(calendar: icalendar.Calendar, title: str, currenttime: datetime) -> datetime:
  """Returns the next update time for some calendar"""
  currenttime = currenttime + kFudgeAdvanceTime
  day_start = currenttime.replace(hour=0, minute=0, second=0, microsecond=0)
  events = recurring_ical_events.of(calendar).between(day_start + timedelta(hours=caltemplate_helpers.kStartHr),
                                                      day_start + timedelta(hours=caltemplate_helpers.kEndHr))
  eggs = eastereggs(title, currenttime)

  # compute the next update time
  event_times = list(chain.from_iterable([[event.get('DTSTART').dt, event.get('DTEND').dt] for event in events]))
  event_times.extend([  # refresh hourly
    day_start + timedelta(hours=1),
    day_start + timedelta(hours=25)  # next day
  ])
  if day_start.weekday() < 5:  # weekdays only
    event_times.extend(map(lambda hour: day_start + timedelta(hours=hour),
                           range(caltemplate_helpers.kStartHr, caltemplate_helpers.kEndHr + 1)))  # refresh on end hour
  event_times += [egg[0] for egg in eggs] + [egg[1] for egg in eggs]  # add easter eggs
  event_times = [time for time in event_times if time > currenttime]
  nexttime = sorted(event_times)[0]

  return nexttime
