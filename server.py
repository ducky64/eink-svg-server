from typing import Optional
from flask import Flask, jsonify
from pydantic import BaseModel, Base64Bytes

from render import render as label_render, TEST_ICAL_URL


class DisplayResponse(BaseModel):
  nextUpdateSec: int  # seconds to next update
  image: Optional[Base64Bytes] = None  # display image data
  err: Optional[str] = None


app = Flask(__name__)


@app.route("/version", methods=['GET'])
def version():
  return "0.1"

@app.route("/render", methods=['GET'])
def render():
  try:
    png_data, events = label_render(TEST_ICAL_URL)
    response = DisplayResponse(nextUpdateSec=60,
                               image=png_data)
  except Exception as e:
    app.logger.exception(f"generate: exception: {repr(e)}")
    response = DisplayResponse(nextUpdateSec=60,
                               error=repr(e))
  return jsonify(response.model_dump())
