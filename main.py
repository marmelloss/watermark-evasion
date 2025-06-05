from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import hashlib
import base64

app = FastAPI()

# Serve static files (your React app) from the "dist" folder
app.mount("/static", StaticFiles(directory="dist"), name="static")
templates = Jinja2Templates(directory=".")

def hash_to_binary(data):
    """Hash input data using SHA-256 and return binary string"""
    h = hashlib.sha256(data.encode()).digest()
    return ''.join(f"{byte:08b}" for byte in h)

def binary_to_unicode(bits):
    """
    Convert binary string to invisible Unicode characters
    0 → Zero Width Non-Joiner (\u200C)
    1 → Zero Width Joiner (\u200D)
    """
    mapping = {'0': '\u200C', '1': '\u200D'}
    return ''.join(mapping[b] for b in bits)

@app.post("/bypass")
async def bypass_watermark(data: dict):
    text = data.get("text", "")
    
    # Metadata to encode
    metadata = "prompt_id:none|model:gpt-4|timestamp:2025-06-05"

    # Hash and convert to invisible watermark
    bits = hash_to_binary(metadata)
    watermark = binary_to_unicode(bits)

    # Insert into text
    midpoint = len(text) // 2
    result = text[:midpoint] + watermark + text[midpoint:]

    return {"result": result}

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
