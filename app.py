from typing import Any, NamedTuple, Dict

from datetime import datetime, timedelta
import pytz
from typing import Optional
from flask import Flask, jsonify, send_file, request
from pydantic import BaseModel
import base64
import io
from urllib.request import urlopen
from icalendar import Calendar
from apscheduler.schedulers.background import BackgroundScheduler

from render import render as label_render


app = Flask(__name__)

import logging
logging.basicConfig(level=logging.INFO)


class DeviceRecord(NamedTuple):
  title: str
  ical_url: str
  template_filename: str
  ota_ver: int = 0  # OTA if reported version is less than this
  ota_filename: Optional[str] = None  # relpath filename of OTA file to send


DEVICE_MAP = {
  'e17514': DeviceRecord(  # v1 board deployed
    title="ELLIOTT ROOM\nRoom 53-135 ENGR IV",
    ical_url="https://calendar.google.com/calendar/ical/gv8rblqs5t8hm6br9muf9uo2f0%40group.calendar.google.com/public/basic.ics",
    template_filename="template_3cb.svg",
    ota_ver=0
  ),
  'd9a8ec': DeviceRecord(  # v1 board development
    title="TESLA ROOM\nRoom 53-125 ENGR IV",
    ical_url="https://calendar.google.com/calendar/ical/ogo00tv2chnq8m02539314helg%40group.calendar.google.com/public/basic.ics",
    template_filename="template_3cb.svg",
    ota_ver=2

  ),
  'xx': DeviceRecord(
    title="TESLA ROOM\nRoom 53-125 ENGR IV",
    ical_url="https://calendar.google.com/calendar/ical/ogo00tv2chnq8m02539314helg%40group.calendar.google.com/public/basic.ics",
    template_filename="template_3cb.svg",
    ota_ver=2
  )
}

def get_device(mac: str) -> DeviceRecord:
  device_opt = DEVICE_MAP.get(mac, None)
  if device_opt is not None:
    return device_opt
  else:
    app.logger.error(f"render: unknown device: {mac}")
    return list(DEVICE_MAP.items())[-1][-1]


kCacheValidTime = timedelta(hours=4)  # cache is stale after this time

class ICalCacheRecord(NamedTuple):
  fetch_time: datetime
  calendar: Any  # ical data

ical_cache: Dict[str, ICalCacheRecord] = {}

def get_cached_ical(url: str) -> bytes:
  record = ical_cache.get(url, None)
  fetch_time = datetime.now()
  if record is None or (fetch_time - record.fetch_time > kCacheValidTime):
    app.logger.info(f"cache: refill: {url}")
    data = urlopen(url).read()
    calendar = Calendar.from_ical(data)
    record = ICalCacheRecord(fetch_time, calendar)
    ical_cache[url] = record
  return record.calendar

def refresh_cache():
  for mac, device in DEVICE_MAP.items():
    get_cached_ical(device.ical_url)

refresh_cache()  # pre-fill the cache on startup
scheduler = BackgroundScheduler()
scheduler.add_job(func=refresh_cache, trigger="interval", seconds=3600)  # TODO synchronize on update points
scheduler.start()


# TODO LEGACY - TO BE REMOVED
class DisplayResponse(BaseModel):
  nextUpdateSec: int  # seconds to next update
  image_b64: Optional[str] = None  # display image data
  err: Optional[str] = None

class MetaResponse(BaseModel):
  nextUpdateSec: int  # seconds to next update
  ota: bool = False  # whether to run OTA
  err: Optional[str] = None


@app.route("/version", methods=['GET'])
def version():
  return "0.2"


# TODO LEGACY - TO BE REMOVED
@app.route("/render", methods=['GET'])
def render():
  try:
    starttime = datetime.now(pytz.timezone('America/Los_Angeles'))

    device = get_device(request.args.get('mac', default=''))
    ical_data = get_cached_ical(device.ical_url)
    png_data, nexttime = label_render(device.template_filename, ical_data, device.title, starttime)
    png_b64 = base64.b64encode(png_data).decode("utf-8")
    next_update_sec = (nexttime - starttime).seconds

    endtime = datetime.now().astimezone()
    runtime = (endtime - starttime).seconds + (endtime - starttime).microseconds / 1e6

    title_printable = device.title.split('\n')[0]
    app.logger.info(f"render: {title_printable}: {len(png_data)} B, {runtime} s: next {nexttime} ({next_update_sec} s)")

    response = DisplayResponse(nextUpdateSec=next_update_sec,
                               image_b64=png_b64)
  except Exception as e:
    app.logger.exception(f"render: exception: {repr(e)}")
    response = DisplayResponse(nextUpdateSec=60,
                               error=repr(e))
  return jsonify(response.model_dump(exclude_none=True))


@app.route("/image", methods=['GET'])
def image():
  try:
    starttime = datetime.now(pytz.timezone('America/Los_Angeles'))

    device = get_device(request.args.get('mac', default=''))
    ical_data = get_cached_ical(device.ical_url)
    png_data, nexttime = label_render(device.template_filename, ical_data, device.title, starttime)

    endtime = datetime.now().astimezone()
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
    starttime = datetime.now(pytz.timezone('America/Los_Angeles'))

    device = get_device(request.args.get('mac', default=''))
    ical_data = get_cached_ical(device.ical_url)
    png_data, nexttime = label_render(device.template_filename, ical_data, device.title, starttime)
    next_update_sec = (nexttime - starttime).seconds

    endtime = datetime.now().astimezone()
    runtime = (endtime - starttime).seconds + (endtime - starttime).microseconds / 1e6

    title_printable = device.title.split('\n')[0]
    app.logger.info(f"meta: {title_printable} ({runtime} s): next {nexttime} ({next_update_sec} s)")

    response = MetaResponse(nextUpdateSec=next_update_sec)
    return jsonify(response.model_dump(exclude_none=True))
  except Exception as e:
    app.logger.exception(f"meta: exception: {repr(e)}")
    return repr(e), 400
