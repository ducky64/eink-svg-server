from itertools import chain
from typing import Tuple, List, Optional
from urllib.request import urlopen
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import recurring_ical_events
import xml.etree.ElementTree as ET
import cairosvg

# because pysvglabel isn't structured as a package, we hack around it by adding it to PYTHONPATH
# TODO clean this up by a lot
import sys

import caltemplate_helpers

sys.path.append("pysvglabel")
from labelcore import SvgTemplate

kTemplateFile = "template_3cb.svg"

# kTestIcalUrl = "https://calendar.google.com/calendar/ical/gv8rblqs5t8hm6br9muf9uo2f0%40group.calendar.google.com/public/basic.ics"
# kTestTitle = "ELLIOTT ROOM\nRoom 53-135 ENGR IV"

kTestIcalUrl = "https://calendar.google.com/calendar/ical/ogo00tv2chnq8m02539314helg%40group.calendar.google.com/public/basic.ics"
kTestTitle = "TESLA ROOM\nRoom 53-125 ENGR IV"

kFudgeAdvanceTime = timedelta(minutes=5)  # add this for the "current" time to account for clock drift and whatnot

def render(ical_url, title) -> Tuple[bytes, datetime]:
  """Renders the calendar to a PNG, given the ical url and title,
  returning the PNG data and next update time"""
  template = SvgTemplate(kTemplateFile)
  label = template._create_instance()

  data = urlopen(ical_url).read()
  calendar = Calendar.from_ical(data)
  current = datetime.now().astimezone() + kFudgeAdvanceTime
  day_start = current.replace(hour=0, minute=0, second=0, microsecond=0)
  events = recurring_ical_events.of(calendar).between(day_start, day_start + timedelta(days=1))

  # don't highlight current events past the end cutoff
  if current.hour < caltemplate_helpers.kEndHr:
    current_events = recurring_ical_events.of(calendar).between(current, current)
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

  png_data = cairosvg.svg2png(bytestring=ET.tostring(root, 'utf-8'),
                              output_width=480, output_height=800)

  # compute the next update time
  if current.hour >= caltemplate_helpers.kEndHr:
    nexttime = day_start + timedelta(days=1, hours=1)
  elif current.hour < caltemplate_helpers.kStartHr:
    nexttime = day_start + timedelta(hours=caltemplate_helpers.kStartHr)
  else:
    event_times = list(chain.from_iterable([[event.get('DTSTART').dt, event.get('DTEND').dt] for event in events]))
    event_times.extend([  # refresh a couple times a day
      day_start.replace(hour=12),
      day_start.replace(hour=16),
    ])
    event_times = [time for time in event_times if time > current]
    nexttime = sorted(event_times)[0]

  return (png_data, nexttime)


if __name__ == '__main__':
  png_data, nexttime = render(kTestIcalUrl, kTestTitle)
  with open('temp.png', 'wb') as f:
    f.write(png_data)
    print(f"render: {kTestTitle} size={len(png_data)}: next update {nexttime}")
