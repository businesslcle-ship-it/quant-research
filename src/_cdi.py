# -*- coding: utf-8 -*-
"""CDI — fonte unica para o repo.

Prioridade: dados/cdi_bcb_diario.csv (BCB SGS serie 12, gerado no lab).
Fallback: mapa anual hardcoded (so se o CSV faltar).

Nao misturar: taxa anual do ano incompleto (ex. 2026 YTD) como se fosse
ano cheio — por isso o diario e a fonte preferida.
"""
from __future__ import annotations

import pandas as pd
from pathlib import Path

from _paths import DADOS

# Fallback (anos fechados ~iguais ao BCB; 2025/2026 no mapa antigo estavam defasados)
CDI_ANUAL_FALLBACK = {
    2008: 0.1238, 2009: 0.0988, 2010: 0.0975, 2011: 0.1160, 2012: 0.0841,
    2013: 0.0806, 2014: 0.1081, 2015: 0.1324, 2016: 0.1400, 2017: 0.0993,
    2018: 0.0642, 2019: 0.0596, 2020: 0.0276, 2021: 0.0442, 2022: 0.1239,
    2023: 0.1304, 2024: 0.1088, 2025: 0.1432, 2026: 0.1500,  # 2026 = provisório
}


def cdi_diario(index: pd.DatetimeIndex) -> pd.Series:
    """Fator diario do CDI alinhado ao indice (ffill)."""
    path = DADOS / "cdi_bcb_diario.csv"
    if path.exists():
        s = (pd.read_csv(path, comment="#", parse_dates=["data"])
             .set_index("data")["cdi_dia"]
             .sort_index())
        out = s.reindex(index).ffill().bfill()
        if out.isna().any():
            raise ValueError("CDI diario com NaN apos ffill/bfill — cheque a cobertura do CSV")
        return out
    anual = pd.Series(index.year, index=index).map(CDI_ANUAL_FALLBACK)
    if anual.isna().any():
        raise ValueError("Ano sem CDI no fallback")
    return (1 + anual) ** (1 / 252) - 1


def cdi_anual_por_ano() -> dict:
    """Mapa ano -> fator acumulado no ano (para scripts mensais/60min)."""
    path = DADOS / "cdi_bcb_anual.csv"
    if path.exists():
        an = pd.read_csv(path, comment="#")
        m = dict(zip(an["ano"].astype(int), an["cdi_acumulado_ano"].astype(float)))
        # 2026 no arquivo BCB e YTD, nao ano cheio — manter provisório se absurdo
        if m.get(2026, 1) < 0.10:
            m[2026] = CDI_ANUAL_FALLBACK[2026]
        return m
    return dict(CDI_ANUAL_FALLBACK)
