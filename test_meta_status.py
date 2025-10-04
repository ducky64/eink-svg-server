import unittest
import app
from test_common import test_get_cached_ical
from datetime import datetime
from unittest.mock import patch, MagicMock

app.app.testing = True


class MetaStatusTestCase(unittest.TestCase):
  def test_log(self):
    config = app.ServerConfig(devices={
      'abcd': app.DeviceRecord(
        title="",
        ical_url="TestCalendar.ics",
        template_filename="",
      )
    }, admin_password='password')
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'meta_csv', MagicMock()),
          patch.object(app, 'config', config),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          app.app.test_client() as client):
      resp = client.get('/admin/status?password=password')
      self.assertEqual(resp.status_code, 200)  # should complete even with no data

      mock_datetime.now.return_value = datetime(2024, 7, 1, 0, 0, 0).astimezone(app.kTimezone)
      client.get('/meta?mac=abcd&fwVer=5&vbat=3900')

      resp = client.get('/admin/status?password=password')
      assert "3900" in resp.data.decode('utf-8')
      assert "2024-07-01 00:00:00" in resp.data.decode('utf-8')
      assert "0:00:00 ago" in resp.data.decode('utf-8')

      mock_datetime.now.return_value = datetime(2024, 7, 1, 3, 0, 0).astimezone(app.kTimezone)
      resp = client.get('/admin/status?password=password')
      assert "3900" in resp.data.decode('utf-8')
      assert "2024-07-01 00:00:00" in resp.data.decode('utf-8')
      assert "3:00:00 ago" in resp.data.decode('utf-8')

      mock_datetime.now.return_value = datetime(2024, 7, 1, 6, 0, 0).astimezone(app.kTimezone)
      client.get('/meta?mac=abcd&fwVer=5&vbat=3850')
      resp = client.get('/admin/status?password=password')
      assert "3900" not in resp.data.decode('utf-8')
      assert "3850" in resp.data.decode('utf-8')
      assert "2024-07-01 06:00:00" in resp.data.decode('utf-8')
      assert "0:00:00 ago" in resp.data.decode('utf-8')
