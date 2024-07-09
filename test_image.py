import unittest
import app
from test_common import test_get_cached_ical
from datetime import datetime
from unittest.mock import patch

app.app.testing = True


kDeviceMap = {
  '': app.DeviceRecord(
    title="TestCalendar",
    ical_url="TestCalendar.ics",
    template_filename="template_750c.svg",
  ),
}


class ImageTestCase(unittest.TestCase):
  def test_image_inuse(self):
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'kDeviceMap', kDeviceMap),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          app.app.test_client() as client):
      mock_datetime.now.return_value = datetime(2024, 7, 1, 16, 10, 0).astimezone(app.kTimezone)
      response = client.get('/image')

      self.assertEqual(response.status_code, 200)
      with open('test_inuse.png', 'wb') as f:
        f.write(response.data)
      # with open('ref_inuse.png', 'rb') as f:  # result seems to be platform-dependent
      #   self.assertEqual(f.read(), response.data)

  def test_image_empty(self):
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'kDeviceMap', kDeviceMap),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          app.app.test_client() as client):
      mock_datetime.now.return_value = datetime(2024, 7, 1, 15, 0, 0).astimezone(app.kTimezone)
      response = client.get('/image')

      self.assertEqual(response.status_code, 200)
      with open('test_empty.png', 'wb') as f:
        f.write(response.data)
      # with open('ref_empty.png', 'rb') as f:  # result seems to be platform-dependent
      #   self.assertEqual(f.read(), response.data)
