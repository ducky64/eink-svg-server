import os
import unittest
import app
from csv_logger import CsvLogger
from test_common import test_get_cached_ical
from datetime import datetime
from unittest.mock import patch

app.app.testing = True


class MetaLoggingTestCase(unittest.TestCase):
  TEST_DIR = "test"
  TEST_FILE = f"{TEST_DIR}/test_meta.csv"

  def test_log(self):
    os.makedirs(self.TEST_DIR, exist_ok=True)
    if os.path.isfile(self.TEST_FILE):
      os.remove(self.TEST_FILE)

    # note, testing of CsvLogger edge cases in its own dedicated test
    config = app.ServerConfig(devices={
      'abcd': app.DeviceRecord(
        title="",
        ical_url="TestCalendar.ics",
        template_filename="",
      ),
    })
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'meta_csv', CsvLogger(self.TEST_FILE, app.meta_csv._default_headers)),
          patch.object(app, 'config', config),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          app.app.test_client() as client):
      mock_datetime.now.return_value = datetime(2024, 7, 1, 0, 0, 0).astimezone(app.kTimezone)
      client.get('/meta?mac=abcd&fwVer=5&vbat=3900')

      mock_datetime.now.return_value = datetime(2024, 7, 1, 6, 0, 0).astimezone(app.kTimezone)
      client.get('/meta?mac=abcd&fwVer=5&vbat=3850')

      with open(self.TEST_FILE, 'r') as f:
        self.assertEqual(f.read(), """timestamp,mac,vbat,fwVer,boot,rst,part,rssi,lastDisplayTime
1719817200.0,abcd,3900,5,,,,,
1719838800.0,abcd,3850,5,,,,,
""")
