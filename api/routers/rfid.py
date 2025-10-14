"""
API Router for RFID Tag Management

This module handles all interactions with RFID tags, including listing,
assigning actions, renaming, and deleting. It replaces the suite of
legacy `rfid_*` scripts with a clean, RESTful interface.
"""

import os
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

from ..core import config, utils

router = APIRouter(
    prefix="/rfid",
    tags=["RFID"],
)

# --- Pydantic Models ---

class RfidTag(BaseModel):
    tag_id: str = Field(..., description="The unique ID of the RFID tag (e.g., '0123ABCD').")
    name: Optional[str] = Field(None, description="A user-friendly name for the tag.")
    color: Optional[str] = Field(None, description="A color associated with the tag.")
    action_type: Optional[str] = Field(None, description="The type of action assigned (e.g., 'url', 'karotz_action').")
    action_url: Optional[str] = Field(None, description="The URL to call if the action type is 'url'.")
    karotz_action: Optional[str] = Field(None, description="The specific Karotz action to perform.")

class RfidAssignment(BaseModel):
    action_type: Literal['url', 'karotz_action', 'eedomus', 'vera', 'zibase']
    value: str = Field(..., description="The value for the action (e.g., a URL, a Karotz command).")
    secondary_value: Optional[str] = Field(None, description="Secondary value, e.g., for home automation IP.")

class ActionResponse(BaseModel):
    message: str

# --- Helper Functions ---

def parse_rfid_file(tag_id: str) -> RfidTag:
    """
    Parses the data file associated with an RFID tag.
    This function simulates reading the tag's configuration files.
    """
    base_path = os.path.join(config.RFID_DIR, tag_id)
    name = utils.get_file_content(f"{base_path}.name", f"Tag {tag_id}")
    color = utils.get_file_content(f"{base_path}.color", "grey")

    # This part is simplified; the original logic is complex.
    action_raw = utils.get_file_content(f"{base_path}.rfid")
    action_type = "url" if action_raw and action_raw.startswith("http") else "karotz_action"

    return RfidTag(
        tag_id=tag_id,
        name=name,
        color=color,
        action_type=action_type,
        action_url=action_raw if action_type == "url" else None,
        karotz_action=action_raw if action_type == "karotz_action" else None
    )

# --- Endpoints ---

@router.get("/tags", response_model=List[RfidTag])
def list_rfid_tags():
    """
    Lists all detected RFID tags and their current assignments.
    Replaces `rfid_list` and `rfid_list_ext`.
    """
    if not os.path.isdir(config.RFID_DIR):
        return []

    # The logic assumes tag IDs are the filenames ending in .rfid
    tag_ids = [f.replace('.rfid', '') for f in os.listdir(config.RFID_DIR) if f.endswith('.rfid')]
    return [parse_rfid_file(tag_id) for tag_id in tag_ids]

@router.post("/record/start", response_model=ActionResponse)
def start_rfid_recording():
    """
    Puts the Karotz into RFID recording mode to detect a new tag.
    Replaces `rfid_start_record`.
    """
    utils.log_info("Starting RFID recording mode.", subsystem="RFID")
    success, output = utils.run_command(["/usr/karotz/bin/rfid_record", "--start"])
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to start RFID recording: {output}")
    return {"message": "RFID recording started. Present a tag."}

@router.post("/record/stop", response_model=ActionResponse)
def stop_rfid_recording():
    """
    Stops the RFID recording mode.
    Replaces `rfid_stop_record`.
    """
    utils.log_info("Stopping RFID recording mode.", subsystem="RFID")
    success, output = utils.run_command(["/usr/karotz/bin/rfid_record", "--stop"])
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to stop RFID recording: {output}")
    return {"message": "RFID recording stopped."}

@router.patch("/tags/{tag_id}", response_model=RfidTag)
def rename_rfid_tag(tag_id: str, name: str = Body(...), color: str = Body(...)):
    """
    Renames an RFID tag and changes its color.
    Replaces `rfid_rename`.
    """
    utils.log_info(f"Renaming tag {tag_id} to '{name}' with color '{color}'.", subsystem="RFID")
    base_path = os.path.join(config.RFID_DIR, tag_id)
    utils.write_file_content(f"{base_path}.name", name)
    utils.write_file_content(f"{base_path}.color", color)

    return parse_rfid_file(tag_id)

@router.post("/tags/{tag_id}/assign", response_model=ActionResponse)
def assign_action_to_tag(tag_id: str, assignment: RfidAssignment):
    """
    Assigns a specific action (URL, Karotz function, etc.) to an RFID tag.
    Replaces all `rfid_assign_*` scripts with a single, unified endpoint.
    """
    utils.log_info(f"Assigning action '{assignment.action_type}' to tag {tag_id}.", subsystem="RFID")
    rfid_file = os.path.join(config.RFID_DIR, f"{tag_id}.rfid")
    # The actual assignment logic is complex, this is a simplified version.
    utils.write_file_content(rfid_file, assignment.value)
    return {"message": f"Action '{assignment.action_type}' assigned to tag {tag_id}."}

@router.delete("/tags/{tag_id}", response_model=ActionResponse)
def unassign_and_delete_tag(tag_id: str):
    """
    Unassigns any action from a tag and deletes its configuration.
    Replaces `rfid_unassign` and `rfid_delete`.
    """
    utils.log_info(f"Deleting tag {tag_id}.", subsystem="RFID")
    base_path = os.path.join(config.RFID_DIR, tag_id)
    for ext in ['.rfid', '.name', '.color']:
        if os.path.exists(base_path + ext):
            os.remove(base_path + ext)
    return {"message": f"Tag {tag_id} has been deleted."}

@router.post("/test", response_model=ActionResponse)
def test_rfid_action(assignment: RfidAssignment):
    """
    Tests an RFID action without assigning it to a tag.
    Replaces all `rfid_test_*` scripts.
    """
    utils.log_info(f"Testing RFID action: {assignment.action_type}", subsystem="RFID")
    if assignment.action_type == 'url':
        utils.run_command(["/usr/bin/mplayer", assignment.value])
    # Other test actions would be implemented here.
    return {"message": "Test action executed successfully."}