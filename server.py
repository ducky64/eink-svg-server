import xml.etree.ElementTree as ET
import os.path
from urllib.request import urlopen
from icalendar import Calendar
import recurring_ical_events

from caltemplate_helpers import *

# because pysvglabel isn't structured as a package, we hack around it by adding it to PYTHONPATH
# TODO clean this up by a lot
import sys
sys.path.append("pysvglabel")
from labelcore import SvgTemplate

ICAL_URL = "https://calendar.google.com/calendar/ical/gv8rblqs5t8hm6br9muf9uo2f0%40group.calendar.google.com/public/basic.ics"
CACHE_FILE = "cache.ics"

TEMPLATE_FILE = "template.svg"


if __name__ == '__main__':
    template = SvgTemplate(TEMPLATE_FILE)

    if not os.path.isfile(CACHE_FILE):  # fetch if needed
        print(f"fetching from {ICAL_URL}")
        data = urlopen(ICAL_URL).read()
        with open(CACHE_FILE, 'wb') as f:
            f.write(data)

    with open(CACHE_FILE, 'rb') as f:
        data = f.read()

    cal = Calendar.from_ical(data)
    events = recurring_ical_events.of(cal).between((2024, 1, 9), (2024, 1, 10))

    for event in events:
        print(event)

    label = template._create_instance()
    instance = template.apply_instance({}, [], 0)
    label.append(instance)
    root = ET.ElementTree(label)
    root.write("applied.svg")
