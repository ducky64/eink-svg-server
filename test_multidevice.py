import unittest
import app
from test_common import test_get_cached_ical
from datetime import datetime
from unittest.mock import patch, MagicMock

app.app.testing = True


devices = app.DeviceMap({
  'a1b1': app.DeviceRecord(
    title="TestCalendar",
    ical_url="TestCalendar.ics",
    template_filename="../template_750c.svg",
  ),
  'a2b2': app.DeviceRecord(
    title="EmptyCalendar",
    ical_url="EmptyCalendar.ics",
    template_filename="../template_750c.svg",
  ),
})

class MultiDeviceTestCase(unittest.TestCase):
  def test_multidevice(self):
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'meta_csv', MagicMock()),
          patch.object(app, 'devices', devices),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          app.app.test_client() as client):
      mock_datetime.now.return_value = datetime(2024, 7, 1, 8, 0, 0).astimezone(app.kTimezone)
      response = client.get('/meta?mac=a1b1')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json['nextUpdateSec'], 1*60*60)  # event end at 9pm

      response = client.get('/meta?mac=a2b2')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json['nextUpdateSec'], 4*60*60)  # update interval at 4pm
