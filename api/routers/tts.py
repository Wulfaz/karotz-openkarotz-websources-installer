"""
API Router for Text-to-Speech (TTS) Functionality

This module handles TTS-related actions, including listing available voices,
generating speech from text, and managing the audio cache. It replaces
the legacy scripts `tts`, `voice_list`, `clear_cache`, and `display_cache`.
"""

import os
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional

from ..core import config, utils

router = APIRouter(
    prefix="/tts",
    tags=["TTS"],
)

# --- Pydantic Models ---

class Voice(BaseModel):
    id: str = Field(..., description="The identifier for the voice (e.g., 'alice').")
    language: str = Field(..., description="The language of the voice (e.g., 'en-US').")
    gender: str = Field(..., description="The gender of the voice.")

class TtsRequest(BaseModel):
    text: str = Field(..., description="The text to be converted to speech.")
    voice: str = Field(..., description="The ID of the voice to use.")
    nocache: bool = Field(False, description="If true, bypass the cache and force regeneration.")

class CacheItem(BaseModel):
    filename: str
    size_kb: int

class ActionResponse(BaseModel):
    message: str

# --- Endpoints ---

@router.get("/voices", response_model=List[Voice])
def list_voices():
    """
    Lists all available TTS voices. Replaces `voice_list`.
    """
    # This is a simplified representation. A real implementation would parse a config file.
    return [
        Voice(id="alice", language="en-US", gender="female"),
        Voice(id="bob", language="en-GB", gender="male"),
        Voice(id="claire", language="fr-FR", gender="female"),
    ]

@router.post("/generate", response_model=ActionResponse)
def generate_speech(request: TtsRequest):
    """
    Generates speech from text and plays it. Replaces `tts`.
    """
    utils.log_info(f"Generating speech for text: '{request.text}' with voice '{request.voice}'.", subsystem="TTS")

    # This is a simplified placeholder for a complex process.
    # A real implementation would need to handle caching, voice mapping, etc.
    cache_filename = f"{hash(request.text)}.mp3"
    cache_path = os.path.join(config.TMP_DIR, cache_filename)

    if request.nocache or not os.path.exists(cache_path):
        # Using pico2wave as an example TTS engine.
        # The voice ID would need to be mapped to a language code.
        voice_map = {"alice": "en-US", "bob": "en-GB", "claire": "fr-FR"}
        lang = voice_map.get(request.voice, "en-US")

        gen_success, gen_output = utils.run_command([
            "pico2wave", "--wave", cache_path, "-l", lang, request.text
        ])
        if not gen_success:
            raise HTTPException(status_code=500, detail=f"TTS generation failed: {gen_output}")

    play_success, play_output = utils.run_command(["/usr/bin/mplayer", cache_path])
    if not play_success:
        raise HTTPException(status_code=500, detail=f"Playback failed: {play_output}")

    return {"message": "Speech generation and playback initiated."}

@router.get("/cache", response_model=List[CacheItem])
def display_tts_cache():
    """
    Displays the contents of the TTS audio cache. Replaces `display_cache`.
    """
    if not os.path.isdir(config.TMP_DIR):
        return []

    items = []
    for f in os.listdir(config.TMP_DIR):
        if f.endswith(('.mp3', '.wav')):
            f_path = os.path.join(config.TMP_DIR, f)
            items.append(CacheItem(filename=f, size_kb=int(os.path.getsize(f_path) / 1024)))
    return items

@router.delete("/cache", response_model=ActionResponse)
def clear_tts_cache():
    """
    Deletes all files from the TTS audio cache. Replaces `clear_cache`.
    """
    utils.log_info("Clearing TTS cache.", subsystem="TTS")
    if not os.path.isdir(config.TMP_DIR):
        return {"message": "Cache directory does not exist."}

    for f in os.listdir(config.TMP_DIR):
        if f.endswith(('.mp3', '.wav')):
            os.remove(os.path.join(config.TMP_DIR, f))
    return {"message": "TTS cache has been cleared."}