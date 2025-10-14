"""
Core Utility Functions for the OpenKarotz On-Device API

This module replaces the legacy `utils.inc` and `url.inc` shell scripts.
It provides a set of common, reusable Python functions for tasks such as
file system interaction, command execution, and logging.
"""

import os
import subprocess
import syslog
from typing import Optional, List
from . import config

# --- Logging ---

def log_info(message: str, subsystem: str = "General"):
    """
    Logs an informational message to the system log.
    Example: log_info("Starting media playback.", subsystem="Media")
    """
    syslog.openlog(config.LOGGER_TAG)
    syslog.syslog(syslog.LOG_INFO, f"[{subsystem}] {message}")
    syslog.closelog()

def log_error(message: str, subsystem: str = "General"):
    """
    Logs an error message to the system log.
    Example: log_error("Failed to read RFID tag.", subsystem="RFID")
    """
    syslog.openlog(config.LOGGER_TAG)
    syslog.syslog(syslog.LOG_ERR, f"[ERROR] [{subsystem}] {message}")
    syslog.closelog()


# --- File System Interaction ---

def get_file_content(path: str, default: Optional[str] = None) -> Optional[str]:
    """
    Safely reads and strips the content of a file.
    Returns the default value if the file does not exist.
    """
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read().strip()
    return default

def write_file_content(path: str, content: str):
    """
    Writes content to a file, creating parent directories if necessary.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def get_dir_file_count(path: str) -> int:
    """
    Counts the number of files in a directory, ignoring subdirectories.
    Returns 0 if the directory does not exist.
    """
    if not os.path.isdir(path):
        return 0
    return len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])

def get_mac_address(interface: str) -> Optional[str]:
    """
    Retrieves the MAC address for a given network interface.
    """
    path = f'/sys/class/net/{interface}/address'
    return get_file_content(path, default="00:00:00:00:00:00")


# --- Command Execution ---

def run_command(command: List[str]) -> (bool, str):
    """
    Executes a shell command safely using a list of arguments.
    Returns a tuple: (success: bool, output: str).
    Output contains stdout on success or stderr on failure.
    """
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        return True, result.stdout.strip()
    except FileNotFoundError as e:
        log_error(f"Command not found: {e.filename}", subsystem="Shell")
        return False, f"Command not found: {e.filename}"
    except subprocess.CalledProcessError as e:
        log_error(f"Command '{e.cmd}' failed with exit code {e.returncode}: {e.stderr.strip()}", subsystem="Shell")
        return False, e.stderr.strip()
    except Exception as e:
        log_error(f"An unexpected error occurred while running command: {command}", subsystem="Shell")
        return False, str(e)

def kill_process(process_name: str):
    """
    Terminates a process by name using 'killall'.
    """
    success, output = run_command(["killall", process_name])
    if not success and "no process found" not in output:
        log_error(f"Failed to kill process '{process_name}': {output}", subsystem="Process")
    return success