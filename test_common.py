import icalendar


def test_get_cached_ical(url: str) -> icalendar.cal.Component:
  if url.startswith('http'):  # ignroe web requests
    return icalendar.Calendar()
  with open(url) as f:
    data = f.read()
  calendar = icalendar.Calendar.from_ical(data)
  return calendar
