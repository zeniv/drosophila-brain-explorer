"""
Обёртка над Brian2 моделью мозга дрозофилы.
Источник: github.com/philshiu/Drosophila_brain_model
Данные:   doi:10.17617/3.CZODIW (Edmond MPG)
"""
import os
import uuid
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from app.core.config import settings
from app.models.schemas import SimulationParams, ExperimentResult, NeuronResult

logger = logging.getLogger(__name__)


def _get_brian2():
    """Ленивый импорт Brian2 — только внутри воркера."""
    try:
        import brian2 as b2
        return b2
    except ImportError as e:
        raise RuntimeError(
            "Brian2 не установлен. Запустите: conda env create -f environment.yml"
        ) from e


class DrosophilaSimulator:
    """
    Singleton-обёртка над коннектомом и Brian2 симулятором.
    Коннектом загружается один раз при старте воркера.
    """

    _connectivity: Optional[pd.DataFrame] = None
    _completeness: Optional[pd.DataFrame] = None

    @classmethod
    def load_data(cls) -> None:
        """Загрузить коннектом в память (вызывается при старте воркера)."""
        con_path = Path(settings.PATH_CONNECTOME)
        cmp_path = Path(settings.PATH_COMPLETENESS)

        if not con_path.exists():
            logger.warning(
                f"Файл коннектома не найден: {con_path}. "
                "Скачайте данные с https://edmond.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.CZODIW"
            )
            return

        logger.info("Загружаю коннектом...")
        cls._connectivity = pd.read_parquet(con_path)

        # Реальные колонки: Presynaptic_ID, Postsynaptic_ID, Connectivity, Excitatory
        # Нормализуем для унификации кода
        cls._connectivity = cls._connectivity.rename(columns={
            "Presynaptic_ID":  "pre_root_id",
            "Postsynaptic_ID": "post_root_id",
            "Connectivity":    "n_syn",
            "Excitatory":      "excitatory",
        })

        cls._completeness = pd.read_csv(cmp_path)
        # Реальные колонки: Unnamed: 0 (root_id), Completed
        cls._completeness = cls._completeness.rename(columns={"Unnamed: 0": "root_id"})

        logger.info(
            f"Коннектом загружен: {len(cls._connectivity):,} синапсов, "
            f"{cls._completeness['root_id'].nunique():,} нейронов"
        )

    @classmethod
    def run_experiment(
        cls,
        neu_exc:  list[int],
        neu_slnc: list[int],
        neu_exc2: list[int],
        params:   SimulationParams,
        exp_name: str = "experiment",
        output_dir: Optional[str] = None,
    ) -> ExperimentResult:
        """
        Запустить Brian2 симуляцию.

        Parameters
        ----------
        neu_exc   : FlyWire IDs нейронов для возбуждения (r_poi)
        neu_slnc  : FlyWire IDs нейронов для заглушения
        neu_exc2  : FlyWire IDs нейронов для вторичной частоты (r_poi2)
        params    : SimulationParams — все настраиваемые параметры
        exp_name  : имя для сохранения файла результатов
        output_dir: директория для parquet файла

        Returns
        -------
        ExperimentResult с агрегированной статистикой
        """
        if cls._connectivity is None:
            cls.load_data()

        if cls._connectivity is None:
            logger.warning("Коннектом не загружен → mock режим")
            return cls._mock_result(neu_exc, params)

        # Проверить наличие Brian2 до начала симуляции
        try:
            b2 = _get_brian2()
        except RuntimeError:
            logger.warning("Brian2 не установлен → mock режим (установите через conda)")
            return cls._mock_result(neu_exc, params)

        # ── Настройка Brian2 ───────────────────────────────────────────────
        if params.n_proc == -1:
            import multiprocessing
            n_proc = multiprocessing.cpu_count()
        else:
            n_proc = params.n_proc

        b2.prefs.devices.cpp_standalone.openmp_threads = n_proc

        # ── Фильтрация коннектома по выбранным нейронам ───────────────────
        all_neurons = set(neu_exc) | set(neu_slnc) | set(neu_exc2)

        # Берём подграф достижимый из возбуждённых нейронов
        # (упрощённо: все синапсы где pre ИЛИ post в активных нейронах)
        conn = cls._connectivity
        mask = conn["pre_root_id"].isin(all_neurons) | conn["post_root_id"].isin(all_neurons)
        conn_sub = conn[mask].copy()

        unique_ids = pd.unique(
            np.concatenate([conn_sub["pre_root_id"].values, conn_sub["post_root_id"].values])
        )
        n_neurons = len(unique_ids)
        id_to_idx = {nid: i for i, nid in enumerate(unique_ids)}

        pre_idx  = conn_sub["pre_root_id"].map(id_to_idx).values
        post_idx = conn_sub["post_root_id"].map(id_to_idx).values

        # Знак синапса: Excitatory=1 → +1, Excitatory=0 → -1 (inhibitory)
        sign = np.where(conn_sub["excitatory"].values == 1, 1, -1)

        # ── Brian2 нейронная группа (LIF) ─────────────────────────────────
        eqs = """
            dv/dt = (-(v - v_0) + I_syn) / t_mbr : volt (unless refractory)
            I_syn : volt
        """

        neurons = b2.NeuronGroup(
            n_neurons,
            model=eqs,
            threshold="v > v_th",
            reset="v = v_rst",
            refractory=params.t_rfc * b2.ms,
            namespace={
                "v_0":  params.v_0  * b2.mV,
                "v_th": params.v_th * b2.mV,
                "v_rst":params.v_rst* b2.mV,
                "t_mbr":params.t_mbr* b2.ms,
            },
        )
        neurons.v = params.v_0 * b2.mV

        # ── Синапсы ───────────────────────────────────────────────────────
        synapses = b2.Synapses(
            neurons, neurons,
            model="w : volt",
            on_pre=f"I_syn_post += w",
            delay=params.t_dly * b2.ms,
        )
        synapses.connect(i=pre_idx, j=post_idx)
        synapses.w = (sign * params.w_syn) * b2.mV

        # ── Poisson входы ─────────────────────────────────────────────────
        exc_idx   = [id_to_idx[n] for n in neu_exc  if n in id_to_idx]
        exc2_idx  = [id_to_idx[n] for n in neu_exc2 if n in id_to_idx]
        slnc_idx  = [id_to_idx[n] for n in neu_slnc if n in id_to_idx]

        if exc_idx:
            poi_input = b2.PoissonInput(
                target=neurons[exc_idx],
                target_var="I_syn",
                N=int(params.f_poi),
                rate=params.r_poi * b2.Hz,
                weight=params.w_syn * b2.mV,
            )

        if exc2_idx and params.r_poi2 > 0:
            poi_input2 = b2.PoissonInput(
                target=neurons[exc2_idx],
                target_var="I_syn",
                N=int(params.f_poi),
                rate=params.r_poi2 * b2.Hz,
                weight=params.w_syn * b2.mV,
            )

        # Заглушение — обнуляем веса
        if slnc_idx:
            for idx in slnc_idx:
                synapses.w[synapses.j == idx] = 0 * b2.mV

        # ── Мониторы ──────────────────────────────────────────────────────
        spike_mon  = b2.SpikeMonitor(neurons)
        rate_mon   = b2.PopulationRateMonitor(neurons)

        # ── Прогоны ───────────────────────────────────────────────────────
        all_spikes = []

        for run_idx in range(params.n_run):
            b2.run(params.t_run * b2.ms)
            spikes_i = spike_mon.i[:]
            spikes_t = spike_mon.t / b2.ms

            df_run = pd.DataFrame({
                "neuron_idx": spikes_i,
                "time_ms":    spikes_t,
                "trial":      run_idx,
                "neuron_id":  unique_ids[spikes_i],
            })
            all_spikes.append(df_run)
            spike_mon.active = False
            spike_mon.active = True

        # ── Сохранение результатов ────────────────────────────────────────
        result_df = pd.concat(all_spikes, ignore_index=True)
        result_df["experiment"] = exp_name

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            result_path = os.path.join(output_dir, f"{exp_name}.parquet")
            result_df.to_parquet(result_path, index=False)
            logger.info(f"Результаты сохранены: {result_path}")

        # ── Агрегация ─────────────────────────────────────────────────────
        return cls._aggregate(result_df, params.t_run, params.n_run, neu_exc)

    @staticmethod
    def _aggregate(
        df: pd.DataFrame,
        t_run: float,
        n_run: int,
        neu_exc: list[int],
    ) -> ExperimentResult:
        """Агрегировать spikes → ExperimentResult."""
        t_sec = t_run / 1000.0

        per_neuron = (
            df.groupby(["neuron_id", "trial"])
              .size()
              .reset_index(name="spikes")
        )
        stats = per_neuron.groupby("neuron_id")["spikes"].agg(["mean", "std"]).reset_index()
        stats["mean_rate"] = stats["mean"] / t_sec
        stats["std_rate"]  = stats["std"]  / t_sec
        stats["spike_count"] = stats["mean"].astype(int)

        stats = stats.sort_values("mean_rate", ascending=False)

        top = [
            NeuronResult(
                neuron_id=int(row["neuron_id"]),
                mean_rate=round(float(row["mean_rate"]), 3),
                spike_count=int(row["spike_count"]),
                std_rate=round(float(row["std_rate"]) if not np.isnan(row["std_rate"]) else 0.0, 3),
            )
            for _, row in stats.head(100).iterrows()
        ]

        return ExperimentResult(
            total_neurons_active=int((stats["mean_rate"] > 0).sum()),
            top_neurons=top,
            mean_network_rate=round(float(stats["mean_rate"].mean()), 4),
            duration_ms=t_run,
        )

    @classmethod
    def _mock_result(cls, neu_exc: list[int], params: SimulationParams) -> ExperimentResult:
        """
        Mock-режим: реалистичные синтетические данные.
        Если коннектом загружен — берём реальных соседей возбуждённых нейронов.
        """
        logger.warning("MOCK режим (Brian2 не установлен или нет данных)")
        rng = np.random.default_rng(seed=hash(tuple(sorted(neu_exc))) % (2**32))

        # Если есть коннектом — найти реальных downstream нейронов
        if cls._connectivity is not None and len(neu_exc) > 0:
            conn = cls._connectivity
            mask = conn["pre_root_id"].isin(neu_exc)
            downstream = conn[mask]["post_root_id"].unique()
            all_ids = list(neu_exc) + list(downstream[:200])
        else:
            all_ids = list(neu_exc)

        n = max(len(all_ids), 10)

        # Генерируем реалистичные firing rates (экспоненциальное распределение)
        # Возбуждённые нейроны — выше, downstream — ниже
        top = []
        for i, nid in enumerate(all_ids[:100]):
            if nid in neu_exc:
                rate = round(float(rng.exponential(25.0)), 3)
            else:
                rate = round(float(rng.exponential(8.0)), 3)
            top.append(NeuronResult(
                neuron_id=int(nid),
                mean_rate=rate,
                spike_count=int(rate * params.t_run / 1000 * params.n_run),
                std_rate=round(rate * float(rng.uniform(0.1, 0.3)), 3),
            ))

        top.sort(key=lambda x: x.mean_rate, reverse=True)

        return ExperimentResult(
            total_neurons_active=n,
            top_neurons=top,
            mean_network_rate=round(float(np.mean([t.mean_rate for t in top])), 4),
            duration_ms=params.t_run,
        )
