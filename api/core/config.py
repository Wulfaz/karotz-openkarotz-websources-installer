"""
Core Configuration for the OpenKarotz On-Device API

This file replaces the legacy `setup.inc` shell script by providing a
centralized location for all system paths, constants, and configuration
values used throughout the FastAPI application.
"""

import os

# --- System Paths ---
# It's crucial to use absolute paths to ensure the API works reliably,
# regardless of where it's started from.

# Root directory for Karotz-specific data and executables
KAROTZ_DIR = "/usr/karotz"
# Directory for persistent data, settings, and run state
DATA_DIR = os.path.join(KAROTZ_DIR, "data")
# Directory for the web server root
WWW_DIR = "/www"
# Path to the CGI-BIN directory (for reference during migration)
CGI_BIN_DIR = os.path.join(WWW_DIR, "cgi-bin")

# --- Data and Run State Subdirectories ---
RUN_DIR = os.path.join(DATA_DIR, "Run")
TMP_DIR = os.path.join(DATA_DIR, "Tmp")
RFID_DIR = os.path.join(DATA_DIR, "Rfid")
MOODS_DIR = os.path.join(DATA_DIR, "Moods")
SOUNDS_DIR = os.path.join(DATA_DIR, "Sounds")
STORIES_DIR = os.path.join(DATA_DIR, "Stories")
SNAPSHOTS_DIR = os.path.join(DATA_DIR, "Snapshots")

# --- Key Files ---
# Paths to specific files that control or report device state.
OK_VERSION_FILE = os.path.join(WWW_DIR, "ok.version")
OK_PATCH_FILE = os.path.join(WWW_DIR, "ok_patch")
LED_COLOR_FILE = os.path.join(RUN_DIR, "led.color")
LED_PULSE_FILE = os.path.join(RUN_DIR, "led.pulse")
EARS_DISABLED_FILE = os.path.join(RUN_DIR, "ears.disabled")
KAROTZ_SLEEP_FILE = os.path.join(RUN_DIR, "karotz.sleep")
KAROTZ_TIME_SLEEP_FILE = os.path.join(RUN_DIR, "karotz.time.sleep")

# --- Default Values & Constants ---
# Replaces hardcoded values from the original scripts.
DEFAULT_LED_COLOR = "00FF00"  # Green
BLACK_COLOR = "000000"
DEFAULT_EAR_POSITION = 9
MIN_EAR_POSITION = 0
MAX_EAR_POSITION = 16

# --- Network & Services ---
# This can be expanded to include default ports, etc.
LOCALHOST = "127.0.0.1"

# --- Logging ---
# Configuration for the system logger.
LOGGER_TAG = "OpenKarotz-API"

# --- Device Hardware ---
# Paths to device nodes or control interfaces if they exist.
# These are speculative and would need to be confirmed on the actual device.
# For example:
# LED_DEVICE = "/dev/led"
# EARS_DEVICE = "/dev/ears"