from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
# Import all models so SQLAlchemy can create tables
import app.models
# Import routers
from app.routers import auth
from app.routers import students 
from app.routers import teacher 
from app.routers import classroom
from app.routers import attendance 
from app.routers import fees 
from app.routers import results

# Create database tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="School Management System API",
    version="1.0.0"
 ) 

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

if frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")

# Register routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(teacher.router)
app.include_router(classroom.router)
app.include_router(attendance.router)
app.include_router(fees.router)
app.include_router(results.router)

# Frontend route
@app.get("/", include_in_schema=False)
def frontend_home():
    return FileResponse(frontend_dir / "index.html")

@app.get("/test-ui", include_in_schema=False)
def test_ui():
    return FileResponse(frontend_dir / "index.html")

@app.get("/api/status")
def api_status():
    return {
        "message": "School Management System Running"
    }
