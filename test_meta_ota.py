import unittest
import app
from test_common import test_get_cached_ical
from datetime import datetime
from unittest.mock import patch, MagicMock

app.app.testing = True


class MetaOtaTestCase(unittest.TestCase):
  def test_ota_empty(self):
    devices = app.DeviceMap({
      '': app.DeviceRecord(
        title="",
        ical_url="TestCalendar.ics",
        template_filename="",
      ),
    })
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'meta_csv', MagicMock()),
          patch.object(app, 'devices', devices),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          patch.object(app, 'ota_done_devices', set()),  # clear OTA records
          app.app.test_client() as client):
      mock_datetime.now.return_value = datetime(2024, 7, 1, 0, 0, 0).astimezone(app.kTimezone)

      response = client.get('/meta?fwVer=5')
      self.assertEqual(response.json['ota'], False)

      response = client.get('/meta?fwVer=0')
      self.assertEqual(response.json['ota'], False)

  def test_ota(self):
    devices = app.DeviceMap({
      '': app.DeviceRecord(
        title="",
        ical_url="TestCalendar.ics",
        template_filename="",
        ota_filename="../test/test_ota.bin",
        ota_ver=5,
      ),
    })
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'meta_csv', MagicMock()),
          patch.object(app, 'devices', devices),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          patch.object(app, 'ota_done_devices', set()),  # clear OTA records
          app.app.test_client() as client):
      mock_datetime.now.return_value = datetime(2024, 7, 1, 0, 0, 0).astimezone(app.kTimezone)

      response = client.get('/meta?fwVer=5')
      self.assertEqual(response.json['ota'], False)

      response = client.get('/meta?fwVer=6')
      self.assertEqual(response.json['ota'], False)

      response = client.get('/meta?fwVer=0')
      self.assertEqual(response.json['ota'], True)

      response = client.get('/meta?fwVer=4')
      self.assertEqual(response.json['ota'], True)

      response = client.get('/ota?fwVer=0')
      self.assertEqual(response.data, b"this is real firmware data, I swear")

  def test_ota_after(self):
    devices = app.DeviceMap({
      '': app.DeviceRecord(
        title="",
        ical_url="TestCalendar.ics",
        template_filename="",
        ota_filename="../test/test_ota.bin",
        ota_ver=5,
        ota_after=datetime(2024, 7, 1, 8, 0, 0).astimezone(app.kTimezone)
      ),
    })
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'meta_csv', MagicMock()),
          patch.object(app, 'devices', devices),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          patch.object(app, 'ota_done_devices', set()),  # clear OTA records
          app.app.test_client() as client):
      mock_datetime.now.return_value = datetime(2024, 7, 1, 7, 0, 0).astimezone(app.kTimezone)
      response = client.get('/meta?fwVer=0')
      self.assertEqual(response.json['ota'], False)

      mock_datetime.now.return_value = datetime(2024, 7, 1, 8, 0, 0).astimezone(app.kTimezone)
      response = client.get('/meta?fwVer=4')
      self.assertEqual(response.json['ota'], True)

  def test_ota_antiretry(self):
    devices = app.DeviceMap({
      '': app.DeviceRecord(
        title="",
        ical_url="TestCalendar.ics",
        template_filename="",
        ota_filename="../test/test_ota.bin",
        ota_ver=5,
      ),
    })
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'meta_csv', MagicMock()),
          patch.object(app, 'devices', devices),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          patch.object(app, 'ota_done_devices', set()),  # clear OTA records
          app.app.test_client() as client):
      mock_datetime.now.return_value = datetime(2024, 7, 1, 0, 0, 0).astimezone(app.kTimezone)

      response = client.get('/meta?fwVer=4')
      self.assertEqual(response.json['ota'], True)

      client.get('/ota?fwVer=0')  # simulate downloading firmware

      response = client.get('/meta?fwVer=5')
      self.assertEqual(response.json['ota'], False)  # as expected

      response = client.get('/meta?fwVer=4')
      self.assertEqual(response.json['ota'], False)  # once firmware downloaded, no more OTA requests allowed
