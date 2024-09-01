This folder stores the device configurations, that map device MAC to the title, template, and ical URL.
Filenames, like templates and OTA binaries, are relative to the config file's directory.
So, to reference templates in the main folder, use `..`.

When starting app.py directly, the configurations are loaded from this folder as a test template.
When using docker, this config folder is NOT copied to the container but instead must be configured as a mount.
