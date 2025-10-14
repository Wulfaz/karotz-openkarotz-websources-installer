"""
API Router for Diagnostic Tools and Utilities

This module provides endpoints for system diagnostics, including viewing
processes and logs, browsing the filesystem, and managing backups. It
replaces legacy scripts like `tools_ps`, `tools_log`, and `rfid_backup`.
"""

import os
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

from ..core import config, utils

router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
)

# --- Pydantic Models ---

class Process(BaseModel):
    pid: int
    user: str
    command: str

class FileSystemItem(BaseModel):
    name: str
    type: Literal['file', 'directory']
    size: Optional[int] = None

class ActionResponse(BaseModel):
    message: str

# --- Endpoints ---

@router.get("/processes", response_model=List[Process])
def list_processes():
    """
    Lists all running processes on the system. Replaces `tools_ps`.
    """
    success, output = utils.run_command(["ps", "-eo", "pid,user,comm"])
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to list processes: {output}")

    processes = []
    for line in output.strip().split('\n')[1:]: # Skip header
        parts = line.split()
        processes.append(Process(pid=int(parts[0]), user=parts[1], command=" ".join(parts[2:])))
    return processes

@router.get("/logs", response_model=str)
def get_system_logs():
    """
    Retrieves the system logs. Replaces `tools_log`.
    """
    # This is a common log path, but might need adjustment for the specific device.
    log_path = "/var/log/messages"
    content = utils.get_file_content(log_path)
    if content is None:
        raise HTTPException(status_code=404, detail=f"Log file not found at {log_path}")
    return content

@router.delete("/logs", response_model=ActionResponse)
def clear_system_logs():
    """
    Clears the system logs. Replaces `tools_clearlog`.
    """
    utils.log_info("Clearing system logs.", subsystem="Tools")
    log_path = "/var/log/messages"
    # Overwriting with an empty string to clear it.
    utils.write_file_content(log_path, "")
    return {"message": "System logs have been cleared."}

@router.get("/files", response_model=List[FileSystemItem])
def list_files(directory: str = Query("/", description="The directory to list.")):
    """
    Lists files and directories at a given path. Replaces `tools_ls`.
    """
    if not os.path.isdir(directory) or not os.path.isabs(directory):
        raise HTTPException(status_code=400, detail="Invalid or non-absolute directory path provided.")

    items = []
    try:
        for name in os.listdir(directory):
            path = os.path.join(directory, name)
            if os.path.isdir(path):
                items.append(FileSystemItem(name=name, type="directory"))
            else:
                items.append(FileSystemItem(name=name, type="file", size=os.path.getsize(path)))
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied to access directory: {directory}")
    return items

@router.get("/backup/rfid", response_model=ActionResponse)
def backup_rfid_data():
    """
    Creates a backup of the RFID data. Replaces `rfid_backup`.
    """
    utils.log_info("Creating RFID backup.", subsystem="Tools")
    backup_path = "/tmp/rfid_backup.tar.gz"
    success, output = utils.run_command(["tar", "-czf", backup_path, config.RFID_DIR])
    if not success:
        raise HTTPException(status_code=500, detail=f"RFID backup failed: {output}")
    return {"message": f"RFID backup created successfully at {backup_path}"}

@router.post("/restore/rfid", response_model=ActionResponse)
async def restore_rfid_data(file: UploadFile = File(...)):
    """
    Restores RFID data from an uploaded backup file. Replaces `rfid_restore`.
    """
    utils.log_info(f"Restoring RFID data from file: {file.filename}", subsystem="Tools")

    restore_path = f"/tmp/{file.filename}"
    contents = await file.read()
    with open(restore_path, "wb") as f:
        f.write(contents)

    success, output = utils.run_command(["tar", "-xzf", restore_path, "-C", "/"])
    if not success:
        raise HTTPException(status_code=500, detail=f"RFID restore failed: {output}")

    os.remove(restore_path) # Clean up the uploaded tarball
    return {"message": "RFID data restored successfully."}