import os
import json
import subprocess
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional

# --- Configuration ---
# In a real on-device deployment, these paths would be constants.
CNF_DATADIR = "/usr/karotz/data"
WWW_DIR = "/www"
BLACK = "000000"
CNF_BREEZE_COLOR = "00FF00"


# --- Pydantic Models ---
class KarotzStatus(BaseModel):
    version: str
    patch: str
    ears_disabled: str
    sleep: str
    sleep_time: str
    led_color: str
    led_pulse: str
    tts_cache_size: int
    usb_free_space: str
    karotz_free_space: str
    eth_mac: str
    wlan_mac: str
    nb_tags: int
    nb_moods: int
    nb_sounds: int
    nb_stories: int
    karotz_percent_used_space: str
    usb_percent_used_space: str
    data_dir: str

class LedAction(BaseModel):
    color: str
    color2: Optional[str] = None
    pulse: Optional[bool] = False
    blink: Optional[bool] = False
    nomemory: Optional[bool] = False
    speed: Optional[int] = 700

class ActionResponse(BaseModel):
    return_code: str
    message: str

class EarsAction(BaseModel):
    left: Optional[int] = None
    right: Optional[int] = None
    reset: Optional[bool] = False


# --- Helper Functions ---
def get_file_content(path, default="0"):
    return open(path).read().strip() if os.path.exists(path) else default

def get_mac_address(interface):
    try:
        with open(f'/sys/class/net/{interface}/address') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "00:00:00:00:00:00"

def get_dir_count(path):
    if not os.path.isdir(path):
        return 0
    return len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])

def run_command(command):
    """Executes a shell command and returns its output."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # In a real scenario, we would have more robust logging.
        print(f"Error executing command: {e.stderr}")
        return ""

# --- FastAPI App and Routers ---
app = FastAPI(
    title="OpenKarotz Modern API",
    description="A modern, on-device API for the OpenKarotz, replacing the legacy cgi-bin scripts.",
    version="1.1.0",
)
status_router = APIRouter()
leds_router = APIRouter()
actions_router = APIRouter()


# --- API Endpoints ---
@status_router.get("/status", response_model=KarotzStatus, tags=["Status"])
def get_status():
    """Retrieves the current status of the Karotz device."""
    # This logic is a Python reimplementation of the 'status' cgi-bin script.

    # Filesystem space
    kfs_stat = os.statvfs('/usr')
    kfs_free = kfs_stat.f_bavail * kfs_stat.f_frsize
    kfs_total = kfs_stat.f_blocks * kfs_stat.f_frsize
    kfs_used_percent = int(((kfs_total - kfs_free) / kfs_total) * 100) if kfs_total > 0 else 0

    ufs_free = "-1"
    ufs_used_percent = "-1"
    if os.path.ismount('/mnt/usbkey'):
        ufs_stat = os.statvfs('/mnt/usbkey')
        ufs_free_bytes = ufs_stat.f_bavail * ufs_stat.f_frsize
        ufs_total = ufs_stat.f_blocks * ufs_stat.f_frsize
        ufs_free = f"{ufs_free_bytes / (1024*1024*1024):.1f}G"
        ufs_used_percent = int(((ufs_total - ufs_free_bytes) / ufs_total) * 100) if ufs_total > 0 else 0

    return {
        "version": get_file_content(f"{WWW_DIR}/ok.version"),
        "patch": get_file_content(f"{WWW_DIR}/ok_patch"),
        "ears_disabled": "1" if os.path.exists(f"{CNF_DATADIR}/Run/ears.disabled") else "0",
        "sleep": "1" if os.path.exists(f"{CNF_DATADIR}/Run/karotz.sleep") else "0",
        "sleep_time": get_file_content(f"{CNF_DATADIR}/Run/karotz.time.sleep"),
        "led_color": get_file_content(f"{CNF_DATADIR}/Run/led.color", CNF_BREEZE_COLOR),
        "led_pulse": get_file_content(f"{CNF_DATADIR}/Run/led.pulse"),
        "tts_cache_size": get_dir_count(f"{CNF_DATADIR}/Tmp"),
        "usb_free_space": ufs_free,
        "karotz_free_space": f"{kfs_free / (1024*1024):.0f}M",
        "eth_mac": get_mac_address("eth0"),
        "wlan_mac": get_mac_address("wlan0"),
        "nb_tags": get_dir_count(f"{CNF_DATADIR}/Rfid"),
        "nb_moods": get_dir_count(f"{CNF_DATADIR}/Moods/fr"),
        "nb_sounds": get_dir_count(f"{CNF_DATADIR}/Sounds"),
        "nb_stories": get_dir_count(f"{CNF_DATADIR}/Stories"),
        "karotz_percent_used_space": str(kfs_used_percent),
        "usb_percent_used_space": str(ufs_used_percent),
        "data_dir": CNF_DATADIR,
    }

@leds_router.post("/leds", response_model=ActionResponse, tags=["LEDs"])
def set_led(action: LedAction):
    """Controls the Karotz's LED."""
    if action.pulse and action.blink:
        raise HTTPException(status_code=400, detail="Cannot use 'blink' and 'pulse' at the same time.")

    # This logic replaces the 'leds' cgi-bin script.
    # It would interact with the low-level LED control mechanism.
    # As a placeholder, we'll just log the command.
    print(f"LED command: color={action.color}, pulse={action.pulse}, blink={action.blink}")

    # In a real implementation, we would call the actual driver, e.g.:
    # run_command(f"ioctl_led {action.color} ...")

    if not action.nomemory:
        with open(f"{CNF_DATADIR}/Run/led.color", "w") as f:
            f.write(action.color)

    return {"return_code": "0", "message": "LED command received."}


@actions_router.post("/ears", response_model=ActionResponse, tags=["Device Actions"])
def set_ears(action: EarsAction):
    """Controls the Karotz's ears."""
    # This logic replaces the 'ears' cgi-bin script.
    # As a placeholder, we log the command.
    print(f"Ears command: left={action.left}, right={action.right}, reset={action.reset}")

    # In a real implementation, we would call the motor driver, e.g.:
    # if action.reset:
    #   run_command("ioctl_ears --reset")
    # else:
    #   run_command(f"ioctl_ears --left {action.left} --right {action.right}")

    return {"return_code": "0", "message": "Ears command received."}

@actions_router.post("/reboot", response_model=ActionResponse, tags=["Device Actions"])
def reboot_device():
    """Reboots the Karotz device."""
    print("Reboot command received. Simulating reboot.")
    # In a real implementation, this would be:
    # run_command("reboot")
    return {"return_code": "0", "message": "Reboot command sent successfully."}

@actions_router.post("/sleep", response_model=ActionResponse, tags=["Device Actions"])
def sleep_device():
    """Puts the Karotz device to sleep."""
    print("Sleep command received. Simulating sleep.")
    # In a real implementation, this would be:
    # run_command("sleep.sh")
    return {"return_code": "0", "message": "Sleep command sent successfully."}


# --- MCP Integration ---
# Import and include the MCP router at the end to avoid circular imports.
from .mcp import mcp_router

app.include_router(status_router, prefix="/api")
app.include_router(leds_router, prefix="/api")
app.include_router(actions_router, prefix="/api/action")
app.include_router(mcp_router, prefix="/agent")