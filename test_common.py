from icalendar import Calendar


def test_get_cached_ical(url: str) -> str:
  with open(url) as f:
    data = f.read()
  calendar = Calendar.from_ical(data)
  return calendar