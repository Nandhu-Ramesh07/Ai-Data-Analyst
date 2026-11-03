import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.analyst import DataAnalystAgent
from app.routers import datasets, health


def warmup(app: FastAPI):

    try:
        app.state.model_ready = app.state.agent.warmup()
    except Exception:
        app.state.model_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.agent = DataAnalystAgent()
    app.state.model_ready = None

    # Load the model in the background so the API starts immediately
    threading.Thread(target=warmup, args=(app,), daemon=True).start()

    yield


app = FastAPI(title="AI Data Analyst API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health.router, prefix="/api")
app.include_router(datasets.router, prefix="/api")
