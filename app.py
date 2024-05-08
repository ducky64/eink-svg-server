from typing import Optional
from flask import Flask, jsonify
from pydantic import BaseModel
import base64

from render import render as label_render, kTestIcalUrl, kTestTitle, kTestTitle2


class DisplayResponse(BaseModel):
  nextUpdateSec: int  # seconds to next update
  image_b64: Optional[str] = None  # display image data
  err: Optional[str] = None


app = Flask(__name__)


@app.route("/version", methods=['GET'])
def version():
  return "0.1"

@app.route("/render", methods=['GET'])
def render():
  try:
    png_data, events = label_render(kTestIcalUrl, kTestTitle, kTestTitle2)
    png_b64 = base64.b64encode(png_data).decode("utf-8")
    response = DisplayResponse(nextUpdateSec=60,
                               image_b64=png_b64)
  except Exception as e:
    app.logger.exception(f"generate: exception: {repr(e)}")
    response = DisplayResponse(nextUpdateSec=60,
                               error=repr(e))
  return jsonify(response.model_dump(exclude_none=True))
