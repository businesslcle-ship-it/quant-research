"""
Exporta o sinal da v2 (alocacao por ativo) para out/sinais_{ATIVO}.csv.
Mesma logica do rotacao.py: direcao (media de 4 janelas) -> vol target no
portfolio -> pesos congelados por semana.
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from _paths import DADOS, OUT

VOL_ALVO, JANELA_VOL, N = 0.20, 20, 252
LOOKBACKS = [126, 189, 252, 315]
ATIVOS = ["PRIO3", "ITUB3", "ABEV3"]

px  = pd.concat({a: pd.read_csv(DADOS / f"{a}.csv", parse_dates=["date"]).set_index("date")["adjustedClose"]
                 for a in ATIVOS}, axis=1, sort=True)  # historia completa (E37)
ret = px.pct_change(fill_method=None)

def lider(L):
    b = px.pct_change(L, fill_method=None).rank(axis=1)
    b = b.eq(b.max(axis=1), axis=0).astype(float)
    return b.div(b.sum(axis=1), axis=0)

direcao = sum(lider(L) for L in LOOKBACKS) / len(LOOKBACKS)
r_dir   = (direcao.shift(1) * ret).sum(axis=1)
fator   = (VOL_ALVO / (r_dir.rolling(JANELA_VOL).std() * np.sqrt(N))).clip(0, 1)
peso    = direcao.mul(fator, axis=0).fillna(0).resample("W-FRI").last().reindex(px.index, method="ffill")
mom12   = px.pct_change(252, fill_method=None)
peso_out = peso.loc["2008":]

for a in ATIVOS:
    out = pd.DataFrame({"adjustedClose": px[a], "momentum_12m": mom12[a], "peso": peso_out[a]}).dropna(subset=["peso"])
    path = OUT / f"sinais_{a}.csv"
    out.to_csv(path)
    print(f"{path}  ({len(out)} linhas)  | peso hoje: {peso_out[a].iloc[-1]:.0%}")
