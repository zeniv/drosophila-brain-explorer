from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


# ── Параметры симуляции ─────────────────────────────────────────────────────

class SimulationParams(BaseModel):
    """Все настраиваемые параметры Brian2 модели"""
    # Временные
    t_run: float = Field(default=1000.0, ge=100.0, le=10000.0,
                         description="Длительность симуляции, мс")
    n_run: int   = Field(default=30,     ge=1,     le=200,
                         description="Число прогонов (для статистики)")

    # Мембранные
    v_0:   float = Field(default=-52.0,  ge=-80.0, le=-30.0,
                         description="Потенциал покоя, мВ")
    v_rst: float = Field(default=-52.0,  ge=-80.0, le=-30.0,
                         description="Потенциал сброса, мВ")
    v_th:  float = Field(default=-45.0,  ge=-65.0, le=-20.0,
                         description="Порог спайка, мВ")
    t_mbr: float = Field(default=20.0,   ge=1.0,   le=100.0,
                         description="Мембранная константа, мс")
    tau:   float = Field(default=5.0,    ge=0.5,   le=50.0,
                         description="Синаптическая константа, мс")
    t_rfc: float = Field(default=2.2,    ge=0.5,   le=20.0,
                         description="Рефрактерный период, мс")
    t_dly: float = Field(default=1.8,    ge=0.1,   le=10.0,
                         description="Синаптическая задержка, мс")

    # Синаптические
    w_syn: float = Field(default=0.275,  ge=0.01,  le=2.0,
                         description="Вес синапса, мВ")
    r_poi: float = Field(default=150.0,  ge=1.0,   le=1000.0,
                         description="Частота Poisson входа, Гц")
    r_poi2:float = Field(default=0.0,    ge=0.0,   le=1000.0,
                         description="Вторичная частота Poisson, Гц")
    f_poi: float = Field(default=250.0,  ge=10.0,  le=2000.0,
                         description="Масштаб Poisson синапсов")

    # Процессоры
    n_proc: int  = Field(default=-1, ge=-1,
                         description="Число CPU (-1 = все)")


# ── Эксперименты ────────────────────────────────────────────────────────────

class ExperimentCreate(BaseModel):
    name: str              = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    params: SimulationParams = Field(default_factory=SimulationParams)
    neu_exc:  List[int]    = Field(..., description="FlyWire IDs — возбуждение")
    neu_slnc: List[int]    = Field(default=[], description="FlyWire IDs — заглушить")
    neu_exc2: List[int]    = Field(default=[], description="FlyWire IDs — вторичная частота")
    hypothesis_id: Optional[UUID4] = None
    tags: List[str]        = Field(default=[])


class ExperimentStatus(str, Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"


class NeuronResult(BaseModel):
    neuron_id: int
    mean_rate: float      # Гц
    spike_count: int
    std_rate: float


class ExperimentResult(BaseModel):
    total_neurons_active: int
    top_neurons: List[NeuronResult]
    mean_network_rate: float
    duration_ms: float


class ExperimentResponse(BaseModel):
    id: UUID4
    name: str
    description: Optional[str]
    status: ExperimentStatus
    params: dict
    neu_exc: List[int]
    neu_slnc: List[int]
    neu_exc2: List[int]
    tags: List[str]
    hypothesis_id: Optional[UUID4]
    result_summary: Optional[ExperimentResult]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Гипотезы ────────────────────────────────────────────────────────────────

class HypothesisStatus(str, Enum):
    UNTESTED            = "untested"
    CONFIRMED           = "confirmed"
    REFUTED             = "refuted"
    REQUIRES_VALIDATION = "requires_validation"


class HypothesisCreate(BaseModel):
    title: str                 = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    prediction: Optional[str]  = None
    arxiv_section: Optional[str] = None


class HypothesisUpdate(BaseModel):
    status: Optional[HypothesisStatus] = None
    notes: Optional[str] = None
    prediction: Optional[str] = None


class HypothesisResponse(BaseModel):
    id: UUID4
    title: str
    description: Optional[str]
    prediction: Optional[str]
    status: HypothesisStatus
    notes: Optional[str]
    experiment_ids: Optional[List[str]]
    arxiv_section: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Сравнение экспериментов ─────────────────────────────────────────────────

class CompareRequest(BaseModel):
    experiment_id_a: UUID4
    experiment_id_b: UUID4


class NeuronDiff(BaseModel):
    neuron_id: int
    rate_a: float
    rate_b: float
    delta: float
    delta_pct: float


class CompareResponse(BaseModel):
    experiment_a: str
    experiment_b: str
    network_rate_a: float
    network_rate_b: float
    network_rate_delta: float
    top_increased: List[NeuronDiff]
    top_decreased: List[NeuronDiff]
    p_value: Optional[float]      # Mann-Whitney U
    significant: Optional[bool]


# ── Parameter Space ─────────────────────────────────────────────────────────

class ParameterSpaceRequest(BaseModel):
    base_params: SimulationParams
    neu_exc: List[int]
    param_x: str    = Field(..., description="Имя параметра по оси X")
    values_x: List[float]
    param_y: str    = Field(..., description="Имя параметра по оси Y")
    values_y: List[float]


class ParameterSpaceResponse(BaseModel):
    param_x: str
    param_y: str
    values_x: List[float]
    values_y: List[float]
    grid: List[List[float]]   # [y][x] -> mean network rate
    job_ids: List[str]
