import unittest
import app
from test_common import test_get_cached_ical
from datetime import datetime
import pytz
from unittest.mock import patch

app.app.testing = True
app.get_cached_ical = test_get_cached_ical


app.kDeviceMap = {
  '': app.DeviceRecord(
    title="TestCalendar",
    ical_url="TestCalendar.ics",
    template_filename="",
  ),
}


class MetaScheduleTestCase(unittest.TestCase):
  def test_nextevent(self):
      with app.app.test_client() as client:
        with patch('app.datetime') as mock_datetime:  # to start of 4pm event
          mock_datetime.now.return_value = datetime(2024, 7, 1, 15, 20, 0).astimezone(pytz.timezone('America/Los_Angeles'))
          response = client.get('/meta')
          self.assertEqual(response.status_code, 200)
          self.assertEqual(response.json['nextUpdateSec'], 40*60)

        with patch('app.datetime') as mock_datetime:  # end of 4pm event
          mock_datetime.now.return_value = datetime(2024, 7, 1, 16, 0, 0).astimezone(pytz.timezone('America/Los_Angeles'))
          response = client.get('/meta')
          self.assertEqual(response.status_code, 200)
          self.assertEqual(response.json['nextUpdateSec'], 30*60)

        with patch('app.datetime') as mock_datetime:  # end of 7pm event
          mock_datetime.now.return_value = datetime(2024, 7, 1, 8, 50, 0).astimezone(pytz.timezone('America/Los_Angeles'))
          response = client.get('/meta')
          self.assertEqual(response.status_code, 200)
          self.assertEqual(response.json['nextUpdateSec'], 10*60)
