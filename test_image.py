import unittest
import app
from test_common import test_get_cached_ical
from datetime import datetime
from unittest.mock import patch

app.app.testing = True


# test all the templates to make sure they all work
kAllTemplates = ['template_750c.svg', 'template_1330c.svg', 'template_1330c_mininext.svg']
devices = app.DeviceMap({
  filename: app.DeviceRecord(
    title="TestCalendar",
    ical_url="TestCalendar.ics",
    template_filename="../" + filename,  # path is config-relative
  )
  for filename in kAllTemplates
})


class ImageTestCase(unittest.TestCase):
  def test_image_inuse(self):
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'devices', devices),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          app.app.test_client() as client):
      mock_datetime.now.return_value = datetime(2024, 7, 1, 16, 10, 0).astimezone(app.kTimezone)
      for filename in kAllTemplates:
        response = client.get(f'/image?mac={filename}')
        self.assertEqual(response.status_code, 200)
        with open(f'test/test_inuse_{filename}.png', 'wb') as f:
          f.write(response.data)
        # with open('ref_inuse.png', 'rb') as f:  # result seems to be platform-dependent
        #   self.assertEqual(f.read(), response.data)

  def test_image_empty(self):
    with (patch('app.datetime') as mock_datetime,
          patch.object(app, 'devices', devices),
          patch.object(app, 'get_cached_ical', test_get_cached_ical),
          app.app.test_client() as client):
      mock_datetime.now.return_value = datetime(2024, 7, 1, 15, 0, 0).astimezone(app.kTimezone)
      for filename in kAllTemplates:
        response = client.get(f'/image?mac={filename}')
        self.assertEqual(response.status_code, 200)
        with open(f'test/test_empty_{filename}.png', 'wb') as f:
          f.write(response.data)
        # with open('ref_empty.png', 'rb') as f:  # result seems to be platform-dependent
        #   self.assertEqual(f.read(), response.data)
