from typing import TypedDict, Tuple, Optional
from datetime import datetime

class Event(TypedDict):  # internal interchange format for calendar events
  name: str  # name of event
  start: datetime
  end: datetime
