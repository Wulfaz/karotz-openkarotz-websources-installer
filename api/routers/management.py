"""
API Router for Application and System Management

This module handles application installation, firmware updates, and other
management tasks. It replaces legacy scripts like `get_apps_list`,
`apps.clock.install`, `get_update_list`, and `flash_update`.
"""

import os
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional

from ..core import config, utils

router = APIRouter(
    prefix="/management",
    tags=["Management"],
)

# --- Pydantic Models ---

class App(BaseModel):
    id: str
    name: str
    version: str
    is_installed: bool

class UpdateInfo(BaseModel):
    id: str
    version: str
    description: str

class ActionResponse(BaseModel):
    message: str

# --- Endpoints ---

@router.get("/apps", response_model=List[App])
def list_apps():
    """
    Lists all available applications and their installation status.
    Replaces `get_apps_list`.
    """
    # This is a simplified representation. A real implementation would parse a manifest file.
    return [
        App(id="clock", name="Clock", version="1.2", is_installed=os.path.exists("/usr/karotz/apps/clock")),
        App(id="moods", name="Moods", version="1.0", is_installed=os.path.exists("/usr/karotz/apps/moods")),
        App(id="story", name="Stories", version="1.1", is_installed=os.path.exists("/usr/karotz/apps/story")),
    ]

@router.post("/apps/{app_id}/install", response_model=ActionResponse)
def install_app(app_id: str):
    """
    Installs or updates a specific application.
    Replaces `apps.clock.install`, `apps.moods.install`, etc.
    """
    utils.log_info(f"Received install request for app: {app_id}", subsystem="Mgmt")

    install_script = f"/usr/karotz/apps/{app_id}/install.sh"
    if not os.path.exists(install_script):
        raise HTTPException(status_code=404, detail=f"Install script for app '{app_id}' not found.")

    success, output = utils.run_command([install_script])
    if not success:
        raise HTTPException(status_code=500, detail=f"Installation failed: {output}")
    return {"message": f"Application '{app_id}' installed successfully."}

@router.get("/updates", response_model=List[UpdateInfo])
def list_updates():
    """
    Checks for and lists available firmware updates and patches.
    Replaces `get_firmware_list`, `get_update_list`, `get_patch_list`.
    """
    # This is a simplified representation. A real implementation would fetch this from a server.
    return [
        UpdateInfo(id="update-2.1", version="2.1", description="Major firmware update."),
        UpdateInfo(id="patch-2.1.1", version="2.1.1", description="Security patch for v2.1."),
    ]

@router.get("/updates/{update_id}", response_model=str)
def read_update_file(update_id: str, file: str):
    """
    Reads a specific file from an update package before installing.
    Replaces `read_update` and `read_patch`.
    """
    utils.log_info(f"Reading file '{file}' from update '{update_id}'.", subsystem="Mgmt")
    # This is a placeholder for a complex operation (e.g., reading from a tarball).
    return f"Contents of {file} from {update_id} would be here."

@router.post("/updates/flash", response_model=ActionResponse)
def flash_update(file: str = Body(..., description="The path to the update package to flash.")):
    """
    Flashes a firmware update package to the device.
    Replaces `flash_update`.
    """
    utils.log_info(f"Flashing update file: {file}", subsystem="Mgmt")

    if not os.path.exists(file):
        raise HTTPException(status_code=404, detail=f"Update file not found: {file}")

    # WARNING: This is a critical, potentially dangerous operation.
    success, output = utils.run_command(["/usr/karotz/bin/flash.sh", file])
    if not success:
        raise HTTPException(status_code=500, detail=f"Flashing failed: {output}")
    return {"message": "Firmware flashing process initiated."}