from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID

from app.core.database import get_db
from app.models.experiment import Hypothesis
from app.models.schemas import HypothesisCreate, HypothesisUpdate, HypothesisResponse

router = APIRouter(prefix="/hypotheses", tags=["hypotheses"])


@router.post("/", response_model=HypothesisResponse, status_code=201)
async def create_hypothesis(
    payload: HypothesisCreate,
    db: AsyncSession = Depends(get_db),
):
    hyp = Hypothesis(**payload.model_dump())
    db.add(hyp)
    await db.commit()
    await db.refresh(hyp)
    return hyp


@router.get("/", response_model=list[HypothesisResponse])
async def list_hypotheses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Hypothesis).order_by(desc(Hypothesis.created_at))
    )
    return result.scalars().all()


@router.get("/{hyp_id}", response_model=HypothesisResponse)
async def get_hypothesis(hyp_id: UUID, db: AsyncSession = Depends(get_db)):
    hyp = await db.get(Hypothesis, hyp_id)
    if not hyp:
        raise HTTPException(status_code=404, detail="Гипотеза не найдена")
    return hyp


@router.patch("/{hyp_id}", response_model=HypothesisResponse)
async def update_hypothesis(
    hyp_id: UUID,
    payload: HypothesisUpdate,
    db: AsyncSession = Depends(get_db),
):
    hyp = await db.get(Hypothesis, hyp_id)
    if not hyp:
        raise HTTPException(status_code=404, detail="Не найдена")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(hyp, field, value)

    await db.commit()
    await db.refresh(hyp)
    return hyp


@router.post("/{hyp_id}/attach/{exp_id}", response_model=HypothesisResponse)
async def attach_experiment(
    hyp_id: UUID,
    exp_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Привязать эксперимент к гипотезе."""
    hyp = await db.get(Hypothesis, hyp_id)
    if not hyp:
        raise HTTPException(status_code=404, detail="Гипотеза не найдена")

    ids = list(hyp.experiment_ids or [])
    if str(exp_id) not in ids:
        ids.append(str(exp_id))
        hyp.experiment_ids = ids

    await db.commit()
    await db.refresh(hyp)
    return hyp
