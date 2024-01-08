from urllib.request import urlopen
from icalendar import Calendar

ICAL_URL = "https://calendar.google.com/calendar/ical/gv8rblqs5t8hm6br9muf9uo2f0%40group.calendar.google.com/public/basic.ics"


data = urlopen(ICAL_URL).read()
cal = Calendar.from_ical(data)

if __name__ == '__main__':
    print(cal)
