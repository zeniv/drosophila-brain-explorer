from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID
import logging

from app.core.database import get_db
from app.models.experiment import Experiment, ExperimentStatus
from app.models.schemas import (
    ExperimentCreate, ExperimentResponse,
    CompareRequest, CompareResponse, NeuronDiff,
    SimulationParams,
)
from app.services.simulation import DrosophilaSimulator

router = APIRouter(prefix="/experiments", tags=["experiments"])
logger = logging.getLogger(__name__)


async def _run_in_background(exp_id: str, db_session_factory):
    """Запустить симуляцию в фоне (без Celery — для dev)."""
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        exp = await session.get(Experiment, UUID(exp_id))
        if not exp:
            return
        exp.status = ExperimentStatus.RUNNING
        await session.commit()
        try:
            params = SimulationParams(**exp.params)
            result = DrosophilaSimulator.run_experiment(
                neu_exc=exp.neu_exc,
                neu_slnc=exp.neu_slnc or [],
                neu_exc2=exp.neu_exc2 or [],
                params=params,
                exp_name=exp_id,
            )
            exp.status = ExperimentStatus.COMPLETED
            exp.result_summary = result.model_dump()
            from datetime import datetime, timezone
            exp.completed_at = datetime.now(timezone.utc)
        except Exception as e:
            logger.error(f"Simulation failed: {e}", exc_info=True)
            exp.status = ExperimentStatus.FAILED
            exp.error_message = str(e)
        await session.commit()


@router.post("/", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    payload: ExperimentCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Создать и запустить эксперимент (BackgroundTasks без Celery)."""
    exp = Experiment(
        name=payload.name,
        description=payload.description,
        params=payload.params.model_dump(),
        neu_exc=payload.neu_exc,
        neu_slnc=payload.neu_slnc,
        neu_exc2=payload.neu_exc2,
        hypothesis_id=payload.hypothesis_id,
        tags=payload.tags,
        status=ExperimentStatus.PENDING,
    )
    db.add(exp)
    await db.flush()
    await db.commit()
    await db.refresh(exp)

    # Запуск в фоне (FastAPI BackgroundTasks)
    background_tasks.add_task(_run_in_background, str(exp.id), None)

    logger.info(f"Создан эксперимент {exp.id}")
    return _to_response(exp)


@router.get("/", response_model=list[ExperimentResponse])
async def list_experiments(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Experiment).order_by(desc(Experiment.created_at)).limit(limit).offset(offset)
    if status:
        q = q.where(Experiment.status == status)
    result = await db.execute(q)
    return [_to_response(e) for e in result.scalars().all()]


@router.get("/{exp_id}", response_model=ExperimentResponse)
async def get_experiment(exp_id: UUID, db: AsyncSession = Depends(get_db)):
    exp = await db.get(Experiment, exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Эксперимент не найден")
    return _to_response(exp)


@router.delete("/{exp_id}", status_code=204)
async def delete_experiment(exp_id: UUID, db: AsyncSession = Depends(get_db)):
    exp = await db.get(Experiment, exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Не найден")
    await db.delete(exp)


@router.post("/compare", response_model=CompareResponse)
async def compare_experiments(req: CompareRequest, db: AsyncSession = Depends(get_db)):
    exp_a = await db.get(Experiment, req.experiment_id_a)
    exp_b = await db.get(Experiment, req.experiment_id_b)

    if not exp_a or not exp_b:
        raise HTTPException(status_code=404, detail="Один из экспериментов не найден")
    if exp_a.status != ExperimentStatus.COMPLETED or exp_b.status != ExperimentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Оба эксперимента должны быть завершены")

    res_a = exp_a.result_summary or {}
    res_b = exp_b.result_summary or {}

    rate_a = res_a.get("mean_network_rate", 0.0)
    rate_b = res_b.get("mean_network_rate", 0.0)

    top_a = {n["neuron_id"]: n["mean_rate"] for n in res_a.get("top_neurons", [])}
    top_b = {n["neuron_id"]: n["mean_rate"] for n in res_b.get("top_neurons", [])}

    common = set(top_a) & set(top_b)
    diffs = [
        NeuronDiff(
            neuron_id=nid,
            rate_a=top_a[nid], rate_b=top_b[nid],
            delta=round(top_b[nid] - top_a[nid], 3),
            delta_pct=round((top_b[nid] - top_a[nid]) / (top_a[nid] + 1e-9) * 100, 1),
        )
        for nid in common
    ]
    diffs.sort(key=lambda x: x.delta, reverse=True)

    p_value, significant = None, None
    rates_a_list = [n["mean_rate"] for n in res_a.get("top_neurons", [])]
    rates_b_list = [n["mean_rate"] for n in res_b.get("top_neurons", [])]
    if len(rates_a_list) >= 5 and len(rates_b_list) >= 5:
        try:
            from scipy.stats import mannwhitneyu
            _, p_value = mannwhitneyu(rates_a_list, rates_b_list, alternative="two-sided")
            significant = bool(p_value < 0.05)
        except ImportError:
            pass

    return CompareResponse(
        experiment_a=exp_a.name, experiment_b=exp_b.name,
        network_rate_a=rate_a, network_rate_b=rate_b,
        network_rate_delta=round(rate_b - rate_a, 4),
        top_increased=diffs[:10], top_decreased=list(reversed(diffs))[:10],
        p_value=round(p_value, 6) if p_value else None,
        significant=significant,
    )


def _to_response(exp: Experiment) -> ExperimentResponse:
    return ExperimentResponse(
        id=exp.id, name=exp.name, description=exp.description,
        status=exp.status.value,
        params=exp.params,
        neu_exc=exp.neu_exc or [], neu_slnc=exp.neu_slnc or [], neu_exc2=exp.neu_exc2 or [],
        tags=exp.tags or [],
        hypothesis_id=exp.hypothesis_id,
        result_summary=exp.result_summary,
        error_message=exp.error_message,
        created_at=exp.created_at,
        completed_at=exp.completed_at,
    )
