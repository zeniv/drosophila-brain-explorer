from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.api import experiments, hypotheses, neurons

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: создать таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("База данных инициализирована")
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Drosophila Brain Explorer API

Веб-интерфейс для симуляции нейронных цепей мозга **Drosophila melanogaster**
на основе полного коннектома FlyWire (125 000+ нейронов, 50M синапсов).

**Модель:** Leaky integrate-and-fire (Brian2)
**Данные:** [doi:10.17617/3.CZODIW](https://edmond.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.CZODIW)
**Статья:** [Nature 2024](https://www.nature.com/articles/s41586-024-07763-9)
    """,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роуты
app.include_router(experiments.router, prefix="/api/v1")
app.include_router(hypotheses.router,  prefix="/api/v1")
app.include_router(neurons.router,     prefix="/api/v1")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}", "docs": "/docs"}
