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
    template_filename="template_3cb.svg",
    # ota_ver=4,
    # ota_data=read_file("../edg-pcbs/IoTDisplay/.pio/build/iotdisplay/firmware.bin"),
  ),
}


class ImageTestCase(unittest.TestCase):
  def test_image_inuse(self):
    with patch('app.datetime') as mock_datetime:
      mock_datetime.now.return_value = datetime(2024, 7, 1, 8, 0, 0).astimezone(pytz.timezone('America/Los_Angeles'))

      with app.app.test_client() as client:
        response = client.get('/image')

        self.assertEqual(response.status_code, 200)
        with open('ref_inuse.png', 'rb') as f:
          self.assertEqual(f.read(), response.data)

  def test_image_empty(self):
    with patch('app.datetime') as mock_datetime:
      mock_datetime.now.return_value = datetime(2024, 7, 1, 15, 0, 0).astimezone(pytz.timezone('America/Los_Angeles'))

      with app.app.test_client() as client:
        response = client.get('/image')

        self.assertEqual(response.status_code, 200)
        with open('ref_empty.png', 'rb') as f:
          self.assertEqual(f.read(), response.data)
