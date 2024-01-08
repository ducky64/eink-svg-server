from urllib.request import urlopen
from icalendar import Calendar
import recurring_ical_events

ICAL_URL = "https://calendar.google.com/calendar/ical/gv8rblqs5t8hm6br9muf9uo2f0%40group.calendar.google.com/public/basic.ics"


data = urlopen(ICAL_URL).read()
cal = Calendar.from_ical(data)
events = recurring_ical_events.of(cal).between((2024, 1, 9), (2024, 1, 10))

if __name__ == '__main__':
    for event in events:
        print(event)
