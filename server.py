import xml.etree.ElementTree as ET
import cairosvg


# because pysvglabel isn't structured as a package, we hack around it by adding it to PYTHONPATH
# TODO clean this up by a lot
import sys
sys.path.append("pysvglabel")
from labelcore import SvgTemplate


TEMPLATE_FILE = "template_3cb.svg"


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
        # reload the template each time
        print("GET: start")
        template = SvgTemplate(TEMPLATE_FILE)
        label = template._create_instance()

        print("GET: apply")
        instance = template.apply_instance({}, [], 0)
        label.append(instance)
        root = ET.ElementTree(label).getroot()
        print("GET: rendering")
        png_data = cairosvg.svg2png(bytestring=ET.tostring(root, 'utf-8'),
                                    # output_width=448, output_height=600)
                                    output_width=480, output_height=800)
        print("GET: sending")
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.end_headers()
        self.wfile.write(png_data)

    def do_POST(self):
        self.do_GET()

if __name__ == '__main__':
    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
    print("Server started")
    server.serve_forever()
