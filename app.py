from datetime import datetime
import pytz
from typing import Optional
from flask import Flask, jsonify, send_file
from pydantic import BaseModel
import base64
import io

from render import render as label_render, kTestIcalUrl, kTestTitle


# TODO LEGACY - TO BE REMOVED
class DisplayResponse(BaseModel):
  nextUpdateSec: int  # seconds to next update
  image_b64: Optional[str] = None  # display image data
  err: Optional[str] = None

class MetaResponse(BaseModel):
  nextUpdateSec: int  # seconds to next update
  ota: bool = False  # whether to run OTA
  err: Optional[str] = None


app = Flask(__name__)

import logging
logging.basicConfig(level=logging.INFO)


@app.route("/version", methods=['GET'])
def version():
  return "0.1"


# TODO LEGACY - TO BE REMOVED
@app.route("/render", methods=['GET'])
def render():
  try:
    starttime = datetime.now(pytz.timezone('America/Los_Angeles'))

    png_data, nexttime = label_render(kTestIcalUrl, kTestTitle, starttime)
    png_b64 = base64.b64encode(png_data).decode("utf-8")
    next_update_sec = (nexttime - starttime).seconds

    endtime = datetime.now().astimezone()
    runtime = (endtime - starttime).seconds + (endtime - starttime).microseconds / 1e6

    title_printable = kTestTitle.split('\n')[0]
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

    png_data, nexttime = label_render(kTestIcalUrl, kTestTitle, starttime)

    endtime = datetime.now().astimezone()
    runtime = (endtime - starttime).seconds + (endtime - starttime).microseconds / 1e6

    title_printable = kTestTitle.split('\n')[0]
    app.logger.info(f"render: {title_printable} ({runtime} s): {len(png_data)} B")

    return send_file(io.BytesIO(png_data), mimetype='image/png')
  except Exception as e:
    app.logger.exception(f"image: exception: {repr(e)}")
    return repr(e), 400


@app.route("/meta", methods=['GET'])
def meta():
  try:
    starttime = datetime.now(pytz.timezone('America/Los_Angeles'))

    png_data, nexttime = label_render(kTestIcalUrl, kTestTitle, starttime)
    next_update_sec = (nexttime - starttime).seconds

    endtime = datetime.now().astimezone()
    runtime = (endtime - starttime).seconds + (endtime - starttime).microseconds / 1e6

    title_printable = kTestTitle.split('\n')[0]
    app.logger.info(f"meta: {title_printable} ({runtime} s): next {nexttime} ({next_update_sec} s)")

    response = MetaResponse(nextUpdateSec=next_update_sec)
    return jsonify(response.model_dump(exclude_none=True))
  except Exception as e:
    app.logger.exception(f"meta: exception: {repr(e)}")
    return repr(e), 400
