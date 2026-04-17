"""
Endpoint для поиска нейронов по FlyWire ID, типу клетки, региону мозга.
"""
from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import numpy as np
from pathlib import Path

from app.core.config import settings
from app.core.database import get_db

router = APIRouter(prefix="/neurons", tags=["neurons"])

_completeness_cache: pd.DataFrame | None = None


def _load_completeness() -> pd.DataFrame | None:
    global _completeness_cache
    if _completeness_cache is not None:
        return _completeness_cache

    path = Path(settings.PATH_COMPLETENESS)
    if not path.exists():
        return None

    _completeness_cache = pd.read_csv(path)
    return _completeness_cache


@router.get("/search")
async def search_neurons(
    q: str | None = Query(default=None, description="Поиск по типу клетки / region"),
    ids: str | None = Query(default=None, description="FlyWire IDs через запятую"),
    limit: int = Query(default=50, le=500),
):
    """
    Поиск нейронов.
    - `q` — текстовый поиск по cell_type, super_class, region
    - `ids` — список конкретных FlyWire IDs
    """
    df = _load_completeness()

    if df is None:
        # Возвращаем примеры известных нейронов (из статьи)
        return {
            "total": 5,
            "neurons": [
                {"id": 720575940621039145, "cell_type": "Gr5a-GRN",     "region": "SEZ", "note": "Sugar taste"},
                {"id": 720575940617946228, "cell_type": "Gr64f-GRN",    "region": "SEZ", "note": "Water taste"},
                {"id": 720575940628913183, "cell_type": "FDNC-motor",   "region": "GNG", "note": "Feeding motor"},
                {"id": 720575940616452186, "cell_type": "Johnston-AN",  "region": "AL",  "note": "Mechanosensory"},
                {"id": 720575940625807983, "cell_type": "vDN-grooming", "region": "VNC", "note": "Grooming"},
            ],
            "mock": True,
        }

    result = df.copy()

    if ids:
        id_list = [int(x.strip()) for x in ids.split(",") if x.strip().isdigit()]
        result = result[result["root_id"].isin(id_list)]

    if q:
        mask = pd.Series(False, index=result.index)
        for col in ["cell_type", "super_class", "cell_class", "nt_type"]:
            if col in result.columns:
                mask |= result[col].astype(str).str.contains(q, case=False, na=False)
        result = result[mask]

    result = result.head(limit)

    return {
        "total": len(result),
        "neurons": result.to_dict(orient="records"),
    }


@router.get("/presets")
async def get_presets():
    """Пресеты нейронов для быстрого старта (из оригинальной статьи Nature 2024)."""
    return {
        "presets": [
            {
                "name": "Sugar taste (Gr5a)",
                "description": "Вкусовые нейроны — сахар. Активируют пробоскис.",
                "neu_exc": [720575940621039145, 720575940614307712],
                "hypothesis": "Активация сахарных GRN приводит к возбуждению мотонейронов GNG",
            },
            {
                "name": "Water taste (Gr64f)",
                "description": "Вкусовые нейроны — вода.",
                "neu_exc": [720575940617946228, 720575940628354985],
                "hypothesis": "Водные и сахарные пути аддитивно активируют пробоскис",
            },
            {
                "name": "Sugar + Water (combined)",
                "description": "Комбинированная активация для проверки аддитивности.",
                "neu_exc": [720575940621039145, 720575940614307712,
                            720575940617946228, 720575940628354985],
                "hypothesis": "Совместная активация > каждого по отдельности",
            },
            {
                "name": "Antennal grooming (Johnston)",
                "description": "Механосенсорные нейроны — инициация груминга антенн.",
                "neu_exc": [720575940616452186],
                "hypothesis": "Активация JO → каскад груминговых нейронов VNC",
            },
        ]
    }
