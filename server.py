import xml.etree.ElementTree as ET
import os.path
from urllib.request import urlopen
from icalendar import Calendar
import recurring_ical_events
import cairosvg

from caltemplate_helpers import *


# because pysvglabel isn't structured as a package, we hack around it by adding it to PYTHONPATH
# TODO clean this up by a lot
import sys
sys.path.append("pysvglabel")
from labelcore import SvgTemplate

ICAL_URL = "https://calendar.google.com/calendar/ical/gv8rblqs5t8hm6br9muf9uo2f0%40group.calendar.google.com/public/basic.ics"
CACHE_FILE = "cache.ics"

TEMPLATE_FILE = "template.svg"
template = SvgTemplate(TEMPLATE_FILE)


from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse

class WebRequestHandler(BaseHTTPRequestHandler):
    @cached_property
    def url(self):
        return urlparse(self.path)

    @cached_property
    def query_data(self):
        return dict(parse_qsl(self.url.query))

    @cached_property
    def post_data(self):
        content_length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(content_length)

    @cached_property
    def form_data(self):
        return dict(parse_qsl(self.post_data.decode("utf-8")))

    @cached_property
    def cookies(self):
        return SimpleCookie(self.headers.get("Cookie"))

    def do_GET(self):
        label = template._create_instance()
        instance = template.apply_instance({}, [], 0)
        label.append(instance)
        root = ET.ElementTree(label).getroot()

        png_data = cairosvg.svg2png(bytestring=ET.tostring(root, 'utf-8'),
                                    output_width=448, output_height=600)

        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.end_headers()
        self.wfile.write(png_data)

    def do_POST(self):
        self.do_GET()

if __name__ == '__main__':
    if not os.path.isfile(CACHE_FILE):  # fetch if needed
        print(f"fetching from {ICAL_URL}")
        data = urlopen(ICAL_URL).read()
        with open(CACHE_FILE, 'wb') as f:
            f.write(data)

    with open(CACHE_FILE, 'rb') as f:
        data = f.read()

    cal = Calendar.from_ical(data)
    events = recurring_ical_events.of(cal).between((2024, 1, 9), (2024, 1, 10))

    for event in events:
        print(event)

    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
    print("Server started")
    server.serve_forever()
