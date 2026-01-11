import os
import uuid
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
GENERATED_DIR = os.path.join(BASE_DIR, "generated")
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

os.makedirs(GENERATED_DIR, exist_ok=True)

# Mount static files
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
app.mount("/generated", StaticFiles(directory=GENERATED_DIR), name="generated")

# Serve frontend
@app.get("/")
async def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Data
CHARACTERS = [
    {"id": "hulk", "name": "Hulk", "image_url": "/assets/hulk.png"},
    {"id": "spiderman", "name": "Spiderman", "image_url": "/assets/spiderman.png"}
]

class GenerateRequest(BaseModel):
    character_id: str
    script: str
    language: str  # 'en' or 'hi'

@app.get("/api/characters")
async def get_characters():
    return CHARACTERS

@app.post("/api/generate")
def generate_video(request: GenerateRequest):
    character = next((c for c in CHARACTERS if c["id"] == request.character_id), None)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Generate unique ID for this request
    request_id = str(uuid.uuid4())
    audio_path = os.path.join(GENERATED_DIR, f"{request_id}.mp3")
    video_path = os.path.join(GENERATED_DIR, f"{request_id}.mp4")
    
    try:
        # 1. Generate Audio (TTS)
        # Map 'hindi' to 'hi' and 'english' to 'en' if needed, but gTTS uses ISO codes
        lang = request.language.lower()
        if lang == 'hindi': lang = 'hi'
        if lang == 'english': lang = 'en'
        
        tts = gTTS(text=request.script, lang=lang, slow=False)
        tts.save(audio_path)
        
        # 2. Generate Video
        # Load audio to get duration
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        
        # Load image
        image_path = os.path.join(ASSETS_DIR, f"{request.character_id}.png")
        image_clip = ImageClip(image_path).with_duration(duration)
        image_clip = image_clip.with_audio(audio_clip)
        
        # Write video file
        # codec='libx264' is standard. fps=24 is sufficient for static image.
        image_clip.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac")
        
        # Cleanup audio file (optional, maybe keep for debugging)
        # os.remove(audio_path)
        
        video_url = f"/generated/{request_id}.mp4"
        return {"video_url": video_url}

    except Exception as e:
        print(f"Error generating video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
