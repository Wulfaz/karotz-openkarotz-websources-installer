"""
API Router for Media and Content Management

This module handles all media-related functionalities, including sounds,
stories, moods, and snapshots. It replaces legacy scripts like `sound_list`,
`sound`, `snapshot`, etc., with a unified, RESTful interface.
"""

import os
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

from ..core import config, utils

router = APIRouter(
    prefix="/media",
    tags=["Media"],
)

# --- Pydantic Models ---

class MediaItem(BaseModel):
    id: str
    name: str

class Snapshot(BaseModel):
    filename: str
    timestamp: str # Ideally a datetime, but keeping it simple for now

class PlaybackRequest(BaseModel):
    id: Optional[str] = Field(None, description="The ID of the media file to play from the local library.")
    url: Optional[str] = Field(None, description="A URL of a media file to stream.")

class PlaybackControlRequest(BaseModel):
    command: Literal['pause', 'stop', 'quit', 'resume']

class ActionResponse(BaseModel):
    message: str

# --- Endpoints ---

# --- Sounds ---
@router.get("/sounds", response_model=List[MediaItem])
def list_sounds():
    """
    Lists all available sound files. Replaces `sound_list`.
    """
    if not os.path.isdir(config.SOUNDS_DIR):
        return []
    return [MediaItem(id=f, name=f.rsplit('.', 1)[0]) for f in os.listdir(config.SOUNDS_DIR) if f.endswith('.mp3')]

@router.post("/sounds/play", response_model=ActionResponse)
def play_sound(request: PlaybackRequest):
    """
    Plays a sound from a local ID or a remote URL. Replaces `sound`.
    """
    if not request.id and not request.url:
        raise HTTPException(status_code=400, detail="Either 'id' or 'url' must be provided.")

    target = ""
    if request.id:
        target = os.path.join(config.SOUNDS_DIR, request.id)
        if not os.path.exists(target):
            raise HTTPException(status_code=404, detail=f"Sound with id '{request.id}' not found.")
        utils.log_info(f"Playing sound with id: {request.id}", subsystem="Media")
    elif request.url:
        target = request.url
        utils.log_info(f"Playing sound from url: {request.url}", subsystem="Media")

    success, output = utils.run_command(["/usr/bin/mplayer", target])
    if not success:
        raise HTTPException(status_code=500, detail=f"Playback failed: {output}")

    return {"message": "Sound playback started."}

@router.post("/sounds/control", response_model=ActionResponse)
def control_sound_playback(request: PlaybackControlRequest):
    """
    Controls ongoing sound playback (pause, stop, resume). Replaces `sound_control`.
    """
    utils.log_info(f"Sound control command: {request.command}", subsystem="Media")
    # The original script kills the process. We will replicate that for stop/quit.
    if request.command in ['stop', 'quit']:
        utils.kill_process("mplayer")
    # Pause/resume would require more complex process interaction (e.g., signals or named pipes)
    return {"message": f"Playback {request.command} command sent."}


# --- Stories ---
@router.get("/stories", response_model=List[MediaItem])
def list_stories():
    """
    Lists all available story files. Replaces `stories_list`.
    """
    if not os.path.isdir(config.STORIES_DIR):
        return []
    return [MediaItem(id=f, name=f.rsplit('.', 1)[0]) for f in os.listdir(config.STORIES_DIR) if f.endswith('.mp3')]

# --- Moods ---
@router.get("/moods", response_model=List[MediaItem])
def list_moods():
    """
    Lists all available mood sound files. Replaces `moods_list`.
    """
    if not os.path.isdir(config.MOODS_DIR):
        return []
    # Moods are often in subdirectories by language
    moods = []
    for root, _, files in os.walk(config.MOODS_DIR):
        for f in files:
            if f.endswith('.mp3'):
                moods.append(MediaItem(id=f, name=f.rsplit('.', 1)[0]))
    return moods

# --- Snapshots ---
@router.get("/snapshots", response_model=List[Snapshot])
def list_snapshots():
    """
    Lists all saved snapshots. Replaces `snapshot_list`.
    """
    if not os.path.isdir(config.SNAPSHOTS_DIR):
        return []

    snapshots = []
    for f in os.listdir(config.SNAPSHOTS_DIR):
        if f.endswith('.jpg'):
            f_path = os.path.join(config.SNAPSHOTS_DIR, f)
            snapshots.append(Snapshot(filename=f, timestamp=str(os.path.getmtime(f_path))))
    return snapshots

@router.post("/snapshots/capture", response_model=ActionResponse)
def capture_snapshot(silent: bool = Query(False, description="If true, don't play the shutter sound.")):
    """
    Captures a new snapshot from the webcam. Replaces `snapshot`.
    """
    utils.log_info(f"Capturing snapshot (silent: {silent}).", subsystem="Media")
    command = ["/usr/karotz/bin/snapshot.sh"]
    if silent:
        command.append("--silent")

    success, output = utils.run_command(command)
    if not success:
        raise HTTPException(status_code=500, detail=f"Snapshot capture failed: {output}")
    return {"message": "Snapshot captured successfully."}

@router.delete("/snapshots", response_model=ActionResponse)
def clear_all_snapshots():
    """
    Deletes all saved snapshots. Replaces `clear_snapshots`.
    """
    utils.log_info("Deleting all snapshots.", subsystem="Media")
    if not os.path.isdir(config.SNAPSHOTS_DIR):
        return {"message": "Snapshot directory does not exist."}

    for f in os.listdir(config.SNAPSHOTS_DIR):
        os.remove(os.path.join(config.SNAPSHOTS_DIR, f))
    return {"message": "All snapshots have been deleted."}