from itertools import chain
from typing import Tuple
from datetime import datetime, timedelta
import recurring_ical_events
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image
import io

# because pysvglabel isn't structured as a package, we hack around it by adding it to PYTHONPATH
# TODO clean this up by a lot
import sys

import caltemplate_helpers

sys.path.append("pysvglabel")
from labelcore import SvgTemplate

kFudgeAdvanceTime = timedelta(minutes=5)  # add this for the "current" time to account for clock drift and whatnot


def render(template_filename: str, calendar: list, title: str, currenttime: datetime) -> bytes:
  """Renders the calendar to a PNG, given the ical url and title, returning the PNG data"""
  template = SvgTemplate(template_filename)
  label = template._create_instance()

  currenttime = currenttime + kFudgeAdvanceTime
  day_start = currenttime.replace(hour=0, minute=0, second=0, microsecond=0)
  events = recurring_ical_events.of(calendar).between(day_start, day_start + timedelta(days=1))

  # don't highlight current events past the end cutoff
  if currenttime.hour < caltemplate_helpers.kEndHr:
    current_events = recurring_ical_events.of(calendar).between(currenttime, currenttime)
  else:
    current_events = []

  instance = template.apply_instance({
    'title': title,
    'current_events': current_events,
    'events': events,
    'day': day_start},
    [], 0)
  label.append(instance)
  root = ET.ElementTree(label).getroot()

  png_data = cairosvg.svg2png(bytestring=ET.tostring(root, 'utf-8'))

  image = Image.open(io.BytesIO(png_data))
  image = image.convert(mode='P')  # palette conversion for additional compression
  img_byte_arr = io.BytesIO()
  image.save(img_byte_arr, format='PNG', optimize=True)
  png_data = img_byte_arr.getvalue()

  return png_data


def next_update(calendar: list, currenttime: datetime) -> datetime:
  """Returns the next update time for some calendar"""
  currenttime = currenttime + kFudgeAdvanceTime
  day_start = currenttime.replace(hour=0, minute=0, second=0, microsecond=0)
  events = recurring_ical_events.of(calendar).between(day_start, day_start + timedelta(days=1))

  # compute the next update time
  endtime = day_start.replace(hour=caltemplate_helpers.kEndHr)
  event_times = list(chain.from_iterable([[event.get('DTSTART').dt, event.get('DTEND').dt] for event in events]))
  past_end_events = [time for time in event_times if time > endtime]
  event_times = [time for time in event_times if time <= endtime]  # prune out events past the end
  if past_end_events:  # if there were events past the end, replace it with one at the end
    event_times.append(endtime)
  event_times.extend([  # refresh a couple times a day
    day_start.replace(hour=1),
    day_start.replace(hour=caltemplate_helpers.kStartHr),
    day_start.replace(hour=12),
    day_start.replace(hour=16),
    day_start.replace(hour=1) + timedelta(days=1)  # next day
  ])
  event_times = [time for time in event_times if time > currenttime]
  nexttime = sorted(event_times)[0]

  return nexttime
