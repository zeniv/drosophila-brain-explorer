"""
Celery задачи для асинхронного выполнения симуляций.
"""
import logging
from datetime import datetime, timezone
from uuid import UUID

from celery import shared_task
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.celery_app import celery_app
from app.models.experiment import Experiment, ExperimentStatus
from app.models.schemas import SimulationParams
from app.services.simulation import DrosophilaSimulator

logger = logging.getLogger(__name__)

# Синхронное подключение для Celery воркера
_sync_engine = create_engine(
    settings.DATABASE_URL.replace("+asyncpg", "+psycopg2"),
    pool_pre_ping=True,
)
SyncSession = sessionmaker(bind=_sync_engine)


@celery_app.task(
    bind=True,
    name="run_simulation",
    max_retries=1,
    soft_time_limit=3600,  # 1 час max
    time_limit=3660,
)
def run_simulation(self, experiment_id: str) -> dict:
    """
    Основная задача: запустить Brian2 симуляцию для experiment_id.
    """
    logger.info(f"[Task {self.request.id}] Запуск симуляции для experiment={experiment_id}")

    with SyncSession() as session:
        exp = session.get(Experiment, UUID(experiment_id))
        if not exp:
            raise ValueError(f"Эксперимент {experiment_id} не найден")

        # Обновить статус → RUNNING
        exp.status = ExperimentStatus.RUNNING
        exp.celery_task_id = self.request.id
        session.commit()

        try:
            params = SimulationParams(**exp.params)
            result = DrosophilaSimulator.run_experiment(
                neu_exc=exp.neu_exc,
                neu_slnc=exp.neu_slnc or [],
                neu_exc2=exp.neu_exc2 or [],
                params=params,
                exp_name=str(experiment_id),
                output_dir=settings.RESULTS_DIR,
            )

            # Сохранить результат
            exp.status = ExperimentStatus.COMPLETED
            exp.result_summary = result.model_dump()
            exp.completed_at = datetime.now(timezone.utc)
            session.commit()

            logger.info(
                f"[Task {self.request.id}] Завершено: "
                f"{result.total_neurons_active} активных нейронов, "
                f"mean rate={result.mean_network_rate:.2f} Hz"
            )
            return {"status": "completed", "experiment_id": experiment_id}

        except Exception as exc:
            logger.error(f"[Task {self.request.id}] Ошибка: {exc}", exc_info=True)
            exp.status = ExperimentStatus.FAILED
            exp.error_message = str(exc)
            session.commit()
            raise self.retry(exc=exc, countdown=5)


@celery_app.task(name="preload_connectome")
def preload_connectome() -> str:
    """Предзагрузка коннектома при старте воркера."""
    DrosophilaSimulator.load_data()
    return "connectome_loaded"
