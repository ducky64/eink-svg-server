import unittest
import app
from test_common import test_get_cached_ical
from datetime import datetime
from unittest.mock import patch

app.app.testing = True


devices = app.DeviceMap({
  '': app.DeviceRecord(
    title="TestCalendar",
    ical_url="TestCalendar.ics",
    template_filename="",
  ),
})


class MetaScheduleTestCase(unittest.TestCase):
  def test_nextevent(self):
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'devices', devices),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          app.app.test_client() as client):
      # before 8am event
      mock_datetime.now.return_value = datetime(2024, 7, 1, 8, 50, 0).astimezone(app.kTimezone)
      response = client.get('/meta')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json['nextUpdateSec'], 10*60)

      # start of 4pm event
      mock_datetime.now.return_value = datetime(2024, 7, 1, 15, 20, 0).astimezone(app.kTimezone)
      response = client.get('/meta')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json['nextUpdateSec'], 40*60)

      # end of 4pm event
      mock_datetime.now.return_value = datetime(2024, 7, 1, 16, 0, 0).astimezone(app.kTimezone)
      response = client.get('/meta')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json['nextUpdateSec'], 30*60)

      # end of late nighter
      mock_datetime.now.return_value = datetime(2024, 7, 1, 20, 10, 0).astimezone(app.kTimezone)
      response = client.get('/meta')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json['nextUpdateSec'], 110*60)

      # schedule for next day
      mock_datetime.now.return_value = datetime(2024, 7, 1, 22, 30, 0).astimezone(app.kTimezone)
      response = client.get('/meta')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json['nextUpdateSec'], 150*60)
