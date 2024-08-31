# eink-svg-server
Prototype image server for an eink display using SVG templates and rendering to PNG for the device

This can be run directly (`flask run --port 80 --host 0.0.0.0`) or in the included Docker container build.

If run directly, the device configurations (mapping device MAC to ical) are loaded from the `config` folder.
If run in Docker, a folder including `config.json` (and any other supporting files, like custom templates) must be mounted to `/usr/app/config` in the container.
The config schema is listed as a pydantic model in `app.py`.
