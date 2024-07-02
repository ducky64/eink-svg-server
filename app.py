from typing import NamedTuple, Dict, Set

from datetime import datetime, timedelta
from dateutil import parser  # type: ignore
import pytz  # type: ignore
from typing import Optional
from flask import Flask, jsonify, send_file, request
from pydantic import BaseModel  # type: ignore
import io
from urllib.request import urlopen
import icalendar
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore

from render import render as label_render, next_update


app = Flask(__name__)

import logging
logging.basicConfig(level=logging.INFO)


class DeviceRecord(NamedTuple):
  title: str
  ical_url: str
  template_filename: str
  ota_ver: int = 0  # OTA if reported version is less than this
  ota_data: Optional[bytes] = None  # bytes of firmware .bin as generated by PlatformIO
  ota_after: Optional[datetime] = None  # only OTA after this time

def read_file(filename: str) -> Optional[bytes]:
  try:
    with open(filename, 'rb') as file:
      return file.read()
  except FileNotFoundError:
    app.logger.exception(f"file does not exist: {filename}")
    return None


kTimezone = pytz.timezone('America/Los_Angeles')
kDeviceMap = {
  'ecda3b46255c': DeviceRecord(
    title="TESLA ROOM\nRoom 53-125 ENGR IV",
    ical_url="https://calendar.google.com/calendar/ical/ogo00tv2chnq8m02539314helg%40group.calendar.google.com/public/basic.ics",
    template_filename="template_3cb.svg",
    ota_ver=4,
    ota_data=read_file("firmware_750c_Z08_4.bin"),
  ),
  'maxwell': DeviceRecord(
    title="MAXWELL ROOM\nRoom 57-124 ENGR IV",
    ical_url="https://calendar.google.com/calendar/ical/bf1sneoveru7n49gbf5ig6hj0c@group.calendar.google.com/public/basic.ics",
    template_filename="template_3cb.svg",
  ),
  '': DeviceRecord(  # dallback
    title="TESLA ROOM\nRoom 53-125 ENGR IV",
    ical_url="https://calendar.google.com/calendar/ical/ogo00tv2chnq8m02539314helg%40group.calendar.google.com/public/basic.ics",
    template_filename="template_3cb.svg",
  )
}

def get_device(mac: str) -> DeviceRecord:
  device_opt = kDeviceMap.get(mac, None)
  if device_opt is not None:
    return device_opt
  else:
    app.logger.warning(f"render: unknown device: {mac}")
    return list(kDeviceMap.items())[-1][-1]

ota_done_devices: Set[DeviceRecord] = set()


kCacheValidTime = timedelta(hours=4)  # cache is stale after this time

class ICalCacheRecord(NamedTuple):
  fetch_time: datetime
  calendar: icalendar.cal.Component  # ical data

ical_cache: Dict[str, ICalCacheRecord] = {}

def get_cached_ical(url: str) -> icalendar.cal.Component:
  record = ical_cache.get(url, None)
  fetch_time = datetime.now()
  if record is None or ((fetch_time - record.fetch_time) > kCacheValidTime):
    app.logger.info(f"cache: refill: {url}")
    data = urlopen(url).read()
    calendar = icalendar.Calendar.from_ical(data)
    record = ICalCacheRecord(fetch_time, calendar)
    ical_cache[url] = record
  return record.calendar

def refresh_cache():
  for mac, device in kDeviceMap.items():
    get_cached_ical(device.ical_url)

# refresh_cache()  # pre-fill the cache on startup
scheduler = BackgroundScheduler()
scheduler.add_job(func=refresh_cache, trigger="interval", seconds=3600)  # TODO synchronize on update points
scheduler.start()


class MetaResponse(BaseModel):
  nextUpdateSec: int  # seconds to next update
  ota: bool = False  # whether to run OTA
  err: Optional[str] = None


@app.route("/version", methods=['GET'])
def version():
  return "0.3"


@app.route("/image", methods=['GET'])
def image():
  try:
    starttime = datetime.now(kTimezone)

    rendertime = starttime
    force_time = request.args.get('forceTime', default=None)
    if force_time is not None:
      rendertime = parser.parse(force_time)
      if not rendertime.tzinfo:
        rendertime = rendertime.astimezone(kTimezone)

    device = get_device(request.args.get('mac', default=''))
    ical_data = get_cached_ical(device.ical_url)
    png_data = label_render(device.template_filename, ical_data, device.title, rendertime)

    endtime = datetime.now(kTimezone)
    runtime = (endtime - starttime).seconds + (endtime - starttime).microseconds / 1e6

    title_printable = device.title.split('\n')[0]
    app.logger.info(f"render: {title_printable} ({runtime} s): {len(png_data)} B")

    return send_file(io.BytesIO(png_data), mimetype='image/png')
  except Exception as e:
    app.logger.exception(f"image: exception: {repr(e)}")
    return repr(e), 400


@app.route("/meta", methods=['GET'])
def meta():
  try:
    starttime = datetime.now(kTimezone)

    device = get_device(request.args.get('mac', default=''))
    ical_data = get_cached_ical(device.ical_url)
    nexttime = next_update(ical_data, starttime)
    next_update_sec = (nexttime - starttime).seconds

    try:
      fwVer = int(request.args.get('fwVer', default=''))
    except ValueError:
      import sys
      fwVer = sys.maxsize
    if (device.ota_ver > fwVer) and (device.ota_data is not None) and (device not in ota_done_devices) \
        and (device.ota_after is None or starttime >= device.ota_after):
      run_ota = True
    else:
      run_ota = False

    endtime = datetime.now().astimezone()
    runtime = (endtime - starttime).seconds + (endtime - starttime).microseconds / 1e6

    title_printable = device.title.split('\n')[0]
    app.logger.info(f"meta: {title_printable} ({runtime} s): next {nexttime} ({next_update_sec} s)")

    response = MetaResponse(nextUpdateSec=next_update_sec, ota=run_ota)
    return jsonify(response.model_dump(exclude_none=True))
  except Exception as e:
    app.logger.exception(f"meta: exception: {repr(e)}")
    return repr(e), 400


@app.route("/ota", methods=['GET'])
def ota():
  try:
    device = get_device(request.args.get('mac', default=''))
    ota_done_devices.add(device)
    title_printable = device.title.split('\n')[0]
    ota_data = device.ota_data
    assert ota_data is not None
    app.logger.info(f"ota: {title_printable}: {len(ota_data)} B")

    return send_file(io.BytesIO(ota_data), mimetype='application/octet-stream')
  except Exception as e:
    app.logger.exception(f"ota: exception: {repr(e)}")
    return repr(e), 400
