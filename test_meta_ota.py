import unittest
import app
from test_common import test_get_cached_ical
from datetime import datetime
import pytz
from unittest.mock import patch

app.app.testing = True
app.get_cached_ical = test_get_cached_ical


class MetaOtaTestCase(unittest.TestCase):
  def test_ota_empty(self):
    app.kDeviceMap = {
      '': app.DeviceRecord(
        title="",
        ical_url="TestCalendar.ics",
        template_filename="",
      ),
    }
    with patch('app.datetime') as mock_datetime:
      mock_datetime.now.return_value = datetime(2024, 7, 1, 0, 0, 0).astimezone(pytz.timezone('America/Los_Angeles'))

      with app.app.test_client() as client:
        response = client.get('/meta?fwVer=5')
        self.assertEqual(response.json['ota'], False)

        response = client.get('/meta?fwVer=0')
        self.assertEqual(response.json['ota'], False)

  def test_ota(self):
    app.kDeviceMap = {
      '': app.DeviceRecord(
        title="",
        ical_url="TestCalendar.ics",
        template_filename="",
        ota_ver=5,
        ota_data=b'this is real firmware data, I swear',
      ),
    }
    with patch('app.datetime') as mock_datetime:
      mock_datetime.now.return_value = datetime(2024, 7, 1, 0, 0, 0).astimezone(pytz.timezone('America/Los_Angeles'))

      with app.app.test_client() as client:
        app.ota_done_devices = set()  # clear OTA records

        response = client.get('/meta?fwVer=5')
        self.assertEqual(response.json['ota'], False)

        response = client.get('/meta?fwVer=6')
        self.assertEqual(response.json['ota'], False)

        response = client.get('/meta?fwVer=0')
        self.assertEqual(response.json['ota'], True)

        response = client.get('/meta?fwVer=4')
        self.assertEqual(response.json['ota'], True)

        response = client.get('/ota?fwVer=0')
        self.assertEqual(response.data, app.kDeviceMap[''].ota_data)


  def test_ota_antirollback(self):
    app.kDeviceMap = {
      '': app.DeviceRecord(
        title="",
        ical_url="TestCalendar.ics",
        template_filename="",
        ota_ver=5,
        ota_data=b'this is real firmware data, I swear',
      ),
    }
    with patch('app.datetime') as mock_datetime:
      mock_datetime.now.return_value = datetime(2024, 7, 1, 0, 0, 0).astimezone(pytz.timezone('America/Los_Angeles'))

      with app.app.test_client() as client:
        app.ota_done_devices = set()  # clear OTA records

        response = client.get('/meta?fwVer=4')
        self.assertEqual(response.json['ota'], True)

        client.get('/ota?fwVer=0')  # simulate downloading firmware

        response = client.get('/meta?fwVer=5')
        self.assertEqual(response.json['ota'], False)  # as expected

        response = client.get('/meta?fwVer=4')
        self.assertEqual(response.json['ota'], False)  # once firmware downloaded, no more OTA requests allowed
