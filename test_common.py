import icalendar


def test_get_cached_ical(url: str) -> icalendar.cal.Component:
  with open(url) as f:
    data = f.read()
  calendar = icalendar.Calendar.from_ical(data)
  return calendar
