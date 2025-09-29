# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the OpenKarotz Web Sources Installer, a FORK of official OpenKarotz sources that automatically installs the
OpenKarotz Web Application from local sources (no USB install required). The project targets Karotz devices and provides
a complete web-based interface for managing the device.

## Architecture

The project consists of two main components in the `sources/` directory:

1. **openkarotz/** - Core configuration files and data directories
	- Apps/, Moods/, Rfid/, Stories/ - Application and content directories
	- Sounds/, Voice/ - Audio content directories
	- Run/, Snapshots/, Tmp/ - Runtime and temporary directories

2. **sources/www/** - Web application files
	- HTML pages for device management interface (index.html, apps.html, etc.)
	- **cgi-bin/** - CGI scripts that handle all backend functionality:
		- Device control scripts (ears, leds, sounds)
		- App installation scripts (apps.*.install)
		- System management (status, tools_*, update)
		- API endpoints for external integrations
		- Utility libraries (utils.inc, url.inc)

The web interface is built using jQuery and provides tabs for different device functions (LEDs, ears, sounds, apps,
etc.).

## Installation & Setup

**Installation:**

```bash
# Copy files to Karotz device
bash install
```

The install script:

- Copies sources/openkarotz/* to /usr/openkarotz/
- Copies sources/www/ to /www/
- Creates symbolic links for snapshots and TTS cache
- Sets proper permissions (755)

**Configuration:**

- Main config in `setup.inc` defines paths and base URLs
- Target directories: `/usr/www/` (web app), `/usr/openkarotz/` (data)
- Base URL configured for karotz.filippi.org

## Key Components

**CGI Backend (sources/www/cgi-bin/):**

- All backend logic implemented as bash CGI scripts
- Common utilities in `utils.inc` (logging, LED colors, process management, URL handling)
- URL building functions in `url.inc` for home automation integration (Vera, Eedomus, Zibase)
- JSON responses for API calls
- Integration with D-Bus for hardware control

**Home Automation Integration:**

- Supports multiple home automation platforms (Vera, Eedomus, Zibase, Calaos)
- URL building functions for different protocols
- Authentication support for secured endpoints

**Device Control:**

- LED management with predefined colors and effects
- Ear movement control
- Sound playback with conflict prevention
- RFID tag management and recording

## Development Notes

- All CGI scripts are bash-based with consistent error handling via Log() function
- JSON responses follow standard format: `{"return":"0/1","msg":"..."}`
- Process management prevents conflicts (e.g., stopping sounds before playing new ones)
- RFID functionality includes tag recording/playback with visual/audio feedback
- URL encoding/decoding utilities for parameter handling
- Curl-based HTTP client with timeout and authentication support

**File Permissions:** The install script sets 755 permissions on all web files to ensure CGI execution.

**Logging:** All components use centralized logging via the Log() function to system logger with [OpenKarotz] prefix.