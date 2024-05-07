from typing import Tuple, List
from urllib.request import urlopen
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import recurring_ical_events
import xml.etree.ElementTree as ET
import cairosvg

# because pysvglabel isn't structured as a package, we hack around it by adding it to PYTHONPATH
# TODO clean this up by a lot
import sys
sys.path.append("pysvglabel")
from labelcore import SvgTemplate

TEMPLATE_FILE = "template_3cb.svg"

TEST_ICAL_URL = "https://calendar.google.com/calendar/ical/gv8rblqs5t8hm6br9muf9uo2f0%40group.calendar.google.com/public/basic.ics"


def render(ical_url) -> Tuple[bytes, List[Event]]:
  template = SvgTemplate(TEMPLATE_FILE)
  label = template._create_instance()

  data = urlopen(ical_url).read()
  calendar = Calendar.from_ical(data)
  start = datetime.now().astimezone().replace(minute=0, hour=0, second=0, microsecond=0)
  events = recurring_ical_events.of(calendar).between(start, start + timedelta(days=1))

  instance = template.apply_instance({
    'events': events,
    'day': start},
    [], 0)
  label.append(instance)
  root = ET.ElementTree(label).getroot()

  png_data = cairosvg.svg2png(bytestring=ET.tostring(root, 'utf-8'),
                              output_width=480, output_height=800)

  return (png_data, events)


if __name__ == '__main__':
  png_data, events = render(TEST_ICAL_URL)
  with open('temp.png', 'wb') as f:
    f.write(png_data)
