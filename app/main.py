from fastapi import FastAPI
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

# Register routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(teacher.router)
app.include_router(classroom.router)
app.include_router(attendance.router)
app.include_router(fees.router)
app.include_router(results.router)

# Home route
@app.get("/")
def home():
    return {
        "message": "School Management System Running"
    }