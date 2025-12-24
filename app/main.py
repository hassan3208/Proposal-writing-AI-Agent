from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from app.routes import router
import os

load_dotenv()

app = FastAPI(
    title="AI Proposal Generator",
    version="1.0.0"
)

# ------------------ CORS ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ API ROUTES ------------------
app.include_router(router, prefix="/api")

# ------------------ FRONTEND SERVING ------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Serve static assets (CSS, JS)
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)

# Serve frontend at root "/"
@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
