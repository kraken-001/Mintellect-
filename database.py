from datetime import datetime, UTC
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, schedule, notes, attachments, groups

app = FastAPI(title="Mintellect API")

# Разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(schedule.router, prefix="/api", tags=["Schedule"])
app.include_router(notes.router, prefix="/api", tags=["Notes"])
app.include_router(attachments.router, prefix="/api", tags=["Attachments"])
app.include_router(groups.router, prefix="/api", tags=["Groups"])


@app.get("/")
async def root():
    return {"message": "🐺 Волк АУФ! Mintellect API работает!"}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "mintellect-api"
    }