from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import uuid


class ExperimentStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class HypothesisStatus(str, enum.Enum):
    UNTESTED = "untested"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    REQUIRES_VALIDATION = "requires_validation"


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Параметры симуляции (полный снапшот)
    params = Column(JSON, nullable=False)

    # Нейроны
    neu_exc = Column(JSON, nullable=False)        # список FlyWire IDs — возбуждение
    neu_slnc = Column(JSON, nullable=True)        # заглушить
    neu_exc2 = Column(JSON, nullable=True)        # вторичная частота

    # Статус
    status = Column(SAEnum(ExperimentStatus), default=ExperimentStatus.PENDING)
    celery_task_id = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)

    # Результаты (агрегированные)
    result_summary = Column(JSON, nullable=True)  # топ нейроны, средние ставки
    result_file = Column(String(512), nullable=True)  # путь к parquet файлу

    # Мета
    hypothesis_id = Column(UUID(as_uuid=True), nullable=True)
    tags = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    prediction = Column(Text, nullable=True)   # что ожидаем увидеть

    status = Column(SAEnum(HypothesisStatus), default=HypothesisStatus.UNTESTED)
    notes = Column(Text, nullable=True)         # результаты, выводы

    # Связанные эксперименты
    experiment_ids = Column(JSON, nullable=True)  # список UUID

    # Для статьи
    arxiv_section = Column(String(100), nullable=True)  # "Results", "Methods", etc.

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
