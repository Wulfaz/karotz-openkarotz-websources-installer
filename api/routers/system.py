"""
API Router for System and Device Management

This module handles core functionalities like checking the device status,
versioning, rebooting, and managing sleep states. It is a functional
replacement for legacy scripts like `status`, `get_version`, `reboot`,
and `sleep`.
"""

import os
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..core import config, utils

router = APIRouter(
    prefix="/system",
    tags=["System"],
)

# --- Pydantic Models ---

class SystemVersion(BaseModel):
    version: str
    patch: str

class SystemStatus(BaseModel):
    version: str
    patch: str
    ears_disabled: bool
    sleep_active: bool
    sleep_time_remaining: int
    led_color: str
    led_is_pulsing: bool
    mac_address_eth: str
    mac_address_wlan: str
    storage_karotz_used_percent: int
    storage_usb_used_percent: int
    storage_karotz_free_space: str
    storage_usb_free_space: str
    count_tts_cache: int
    count_rfid_tags: int
    count_moods: int
    count_sounds: int
    count_stories: int

class ActionResponse(BaseModel):
    message: str

# --- Helper Functions ---

def get_disk_usage(path: str) -> (int, str):
    """
    Runs the `df` command to get disk usage percentage and free space.
    Returns a tuple of (percentage_used, free_space_str).
    Mirrors the logic from the original `status` script.
    """
    if not os.path.ismount(path) and not os.path.isdir(path):
        return -1, "-1"

    # Get percentage used
    success, output = utils.run_command(["df", path])
    percent_used = -1
    if success:
        last_line = output.strip().split('\n')[-1]
        percent_str = re.search(r'(\d+)%', last_line)
        if percent_str:
            percent_used = int(percent_str.group(1))

    # Get human-readable free space
    success, output = utils.run_command(["df", "-Ph", path])
    free_space = "-1"
    if success:
        free_space = output.strip().split('\n')[-1].split()[3]

    return percent_used, free_space

# --- Endpoints ---

@router.get("/version", response_model=SystemVersion)
def get_version():
    """
    Retrieves the software version and patch level of the OpenKarotz installation.
    Replaces `get_version`.
    """
    return {
        "version": utils.get_file_content(config.OK_VERSION_FILE, "0"),
        "patch": utils.get_file_content(config.OK_PATCH_FILE, "0"),
    }

@router.get("/status", response_model=SystemStatus)
def get_status():
    """
    Provides a comprehensive status of the Karotz device.
    This is a full Python reimplementation of the `status` cgi-bin script.
    """
    try:
        karotz_usage, karotz_free = get_disk_usage('/usr')
        usb_usage, usb_free = get_disk_usage('/mnt/usbkey')

        return {
            "version": utils.get_file_content(config.OK_VERSION_FILE, "0"),
            "patch": utils.get_file_content(config.OK_PATCH_FILE, "0"),
            "ears_disabled": os.path.exists(config.EARS_DISABLED_FILE),
            "sleep_active": os.path.exists(config.KAROTZ_SLEEP_FILE),
            "sleep_time_remaining": int(utils.get_file_content(config.KAROTZ_TIME_SLEEP_FILE, "0")),
            "led_color": utils.get_file_content(config.LED_COLOR_FILE, config.DEFAULT_LED_COLOR),
            "led_is_pulsing": utils.get_file_content(config.LED_PULSE_FILE, "0") == "1",
            "mac_address_eth": utils.get_mac_address("eth0"),
            "mac_address_wlan": utils.get_mac_address("wlan0"),
            "storage_karotz_used_percent": karotz_usage,
            "storage_usb_used_percent": usb_usage,
            "storage_karotz_free_space": karotz_free,
            "storage_usb_free_space": usb_free,
            "count_tts_cache": utils.get_dir_file_count(config.TMP_DIR),
            "count_rfid_tags": utils.get_dir_file_count(config.RFID_DIR),
            "count_moods": utils.get_dir_file_count(os.path.join(config.MOODS_DIR, "fr")), # Assuming 'fr'
            "count_sounds": utils.get_dir_file_count(config.SOUNDS_DIR),
            "count_stories": utils.get_dir_file_count(config.STORIES_DIR),
        }
    except Exception as e:
        utils.log_error(f"Failed to get system status: {e}", subsystem="System")
        raise HTTPException(status_code=500, detail="Failed to retrieve system status.")


@router.post("/reboot", response_model=ActionResponse)
def reboot_device():
    """
    Reboots the Karotz device. Replaces `reboot`.
    """
    utils.log_info("Received reboot request.", subsystem="System")
    success, output = utils.run_command(["/sbin/reboot"])
    if not success:
        raise HTTPException(status_code=500, detail=f"Reboot command failed: {output}")
    return {"message": "Karotz device is rebooting."}


@router.post("/sleep", response_model=ActionResponse)
def sleep_device():
    """
    Puts the Karotz device to sleep. Replaces `sleep`.
    """
    utils.log_info("Received sleep request.", subsystem="System")
    success, output = utils.run_command(["/usr/karotz/bin/sleep.sh"])
    if not success:
        raise HTTPException(status_code=500, detail=f"Sleep command failed: {output}")
    return {"message": "Karotz device is going to sleep."}


@router.post("/wakeup", response_model=ActionResponse)
def wakeup_device():
    """
    Wakes the Karotz device from sleep. Replaces `wakeup`.
    """
    utils.log_info("Received wakeup request.", subsystem="System")
    success, output = utils.run_command(["/usr/karotz/bin/wakeup.sh"])
    if not success:
        raise HTTPException(status_code=500, detail=f"Wakeup command failed: {output}")
    return {"message": "Karotz device is waking up."}

@router.post("/correct-permissions", response_model=ActionResponse)
def correct_permissions():
    """
    Resets data directory permissions to their default state.
    Replaces `correct_permissions`.
    """
    utils.log_info("Correcting permissions on data directory.", subsystem="System")
    success, output = utils.run_command(["/bin/chmod", "-R", "755", config.DATA_DIR])
    if not success:
        raise HTTPException(status_code=500, detail=f"Permission correction failed: {output}")
    return {"message": "Data directory permissions have been corrected."}