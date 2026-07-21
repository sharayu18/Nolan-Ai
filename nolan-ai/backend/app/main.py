import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analytics, chat, errors, feedback, scripts, topics
from app.config import settings
from app.scheduler import create_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Nolan AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(topics.router)
app.include_router(scripts.router)
app.include_router(analytics.router)
app.include_router(feedback.router)
app.include_router(errors.router)


@app.get("/health")
def health():
    return {"status": "ok", "channel": settings.channel_handle}
