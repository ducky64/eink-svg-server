from typing import TypedDict, Tuple, List, Dict, Any
from datetime import datetime
from math import ceil, floor

class Event(TypedDict):  # internal interchange format for calendar events
  name: str  # name of event
  start: datetime
  end: datetime

def time_elts(start_hr: float, end_hr: float) -> List[Tuple[float, Dict[str, Any]]]:
  """returns the time env elements between start_hr and end_hr, inclusive"""
  def hr_to_str(hr: float) -> str:
    num = hr % 12
    if num == 0:
      num = 12
    return f"{num}{'a' if hr < 12 else 'p'}"

  scale = 1.0 / (end_hr - start_hr)
  return [((hr - start_hr) * scale, {'time': hr_to_str(hr)})
          for hr in range(ceil(start_hr), floor(end_hr) + 1)]
