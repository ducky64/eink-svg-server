import unittest
import app
from test_common import test_get_cached_ical
from datetime import datetime
from unittest.mock import patch
import labelcore
import xml.etree.ElementTree as ET

app.app.testing = True


kDeviceMap = {
  '': app.DeviceRecord(
    title="TESLA ROOM",
    ical_url="TestCalendar.ics",
    template_filename="template_3cb.svg",
  ),
}


class EasterEggTestCase(unittest.TestCase):
  def test_image(self):
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'kDeviceMap', kDeviceMap),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          patch.object(labelcore.SvgTemplate, 'apply_instance') as apply_instance_mock,
          app.app.test_client() as client):
      apply_instance_mock.return_value = ET.Element('g')  # return something structurally valid to not crash

      mock_datetime.now.return_value = datetime(2024, 7, 5, 8, 0, 0).astimezone(app.kTimezone)
      client.get('/image')
      self.assertEqual(apply_instance_mock.call_args.args[0]['duck_image'], 'ext_art/sub_duck.svg')

      mock_datetime.now.return_value = datetime(2024, 7, 3, 18, 20, 0).astimezone(app.kTimezone)
      client.get('/image')
      self.assertEqual(apply_instance_mock.call_args.args[0]['duck_image'], 'ext_art/sub_duck_serious.svg')

      mock_datetime.now.return_value = datetime(2024, 7, 3, 18, 30, 0).astimezone(app.kTimezone)
      client.get('/image')
      self.assertEqual(apply_instance_mock.call_args.args[0]['duck_image'], 'ext_art/sub_duck_boardgames.svg')

      mock_datetime.now.return_value = datetime(2024, 7, 3, 23, 30, 0).astimezone(app.kTimezone)
      client.get('/image')
      self.assertEqual(apply_instance_mock.call_args.args[0]['duck_image'], 'ext_art/sub_duck_boardgames.svg')

  def test_meta(self):
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'kDeviceMap', kDeviceMap),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          app.app.test_client() as client):
      # check board games night duck gets scheduled
      mock_datetime.now.return_value = datetime(2024, 7, 3, 18, 20, 0).astimezone(app.kTimezone)
      response = client.get('/meta')
      self.assertEqual(response.json['nextUpdateSec'], 10*60)

      mock_datetime.now.return_value = datetime(2024, 7, 3, 18, 30, 0).astimezone(app.kTimezone)
      response = client.get('/meta')
      self.assertEqual(response.json['nextUpdateSec'], 90*60)
