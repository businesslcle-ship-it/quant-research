"""
Rotacao v2 + grafico (3 paineis): patrimonio (log) / drawdown / alocacao.
Mesma logica do rotacao.py (regua oficial 20 bps); salva figures/rotacao.png.

Integridade do painel 1: B&H e a v2 usam a MESMA janela e base ~1.
Nunca fazer cumprod(B&H) desde o inicio da serie e so reindexar em 2008 —
isso inchava o B&H com o pre-2008 e mentia no grafico.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from _paths import DADOS, FIGS
from _cdi import cdi_diario

CUSTO_OFICIAL = 0.0020
VOL_ALVO, JANELA_VOL, DIAS_NO_ANO = 0.20, 20, 252
LOOKBACKS = [126, 189, 252, 315]
ATIVOS = ["PRIO3", "ITUB3", "ABEV3"]
CORES  = {"PRIO3": "#eb6834", "ITUB3": "#2a78d6", "ABEV3": "#1baf7a"}
AVALIAR_DESDE = "2008"

precos = pd.concat({a: pd.read_csv(DADOS / f"{a}.csv", parse_dates=["date"]).set_index("date")["adjustedClose"]
                    for a in ATIVOS}, axis=1, sort=True)
ret   = precos.pct_change(fill_method=None)
cdi_d = cdi_diario(precos.index)

def lider_da_janela(L):
    b = precos.pct_change(L, fill_method=None).rank(axis=1)
    b = b.eq(b.max(axis=1), axis=0).astype(float)
    return b.div(b.sum(axis=1), axis=0)

direcao = sum(lider_da_janela(L) for L in LOOKBACKS) / len(LOOKBACKS)
r_dir   = (direcao.shift(1) * ret).sum(axis=1)
fator   = (VOL_ALVO / (r_dir.rolling(JANELA_VOL).std() * np.sqrt(DIAS_NO_ANO))).clip(0, 1)
peso    = direcao.mul(fator, axis=0).fillna(0).resample("W-FRI").last().reindex(precos.index, method="ffill")
caixa   = 1 - peso.sum(axis=1)

ret_estrategia = ((peso.shift(1) * ret).sum(axis=1) + caixa.shift(1) * cdi_d
                  - peso.diff().abs().sum(axis=1) * CUSTO_OFICIAL).dropna().loc[AVALIAR_DESDE:]
peso = peso.loc[AVALIAR_DESDE:]
patrimonio = (1 + ret_estrategia).cumprod()
buy_hold = (1 + ret.mean(axis=1).reindex(patrimonio.index)).cumprod()
if not (0.9 <= float(buy_hold.iloc[0]) <= 1.1):
    raise AssertionError(
        f"B&H deve comecar ~1 na janela de avaliacao; veio {buy_hold.iloc[0]:.3f}. "
        "Provavel cumprod pre-janela sem rebase."
    )

drawdown = (patrimonio / patrimonio.cummax() - 1) * 100
sharpe   = ret_estrategia.mean() / ret_estrategia.std() * np.sqrt(DIAS_NO_ANO)
print(f"Sharpe (vs zero, 20 bps)={sharpe:.2f}  MaxDD={drawdown.min():.0f}%  ret={patrimonio.iloc[-1]-1:.0%}")
print(f"B&H 1/3 mesma janela: ret={buy_hold.iloc[-1]-1:.0%}  (v2 / B&H no fim = {patrimonio.iloc[-1]/buy_hold.iloc[-1]:.2f}x)")

fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(13, 10), sharex=True, height_ratios=[2, 1, 1], facecolor="#fcfcfb")
patrimonio.plot(ax=a1, color="#2a78d6", lw=2, label="Rotacao v2 (com CDI no caixa)")
buy_hold.plot(ax=a1, color="#8a8a85", lw=1, ls="--", label="Buy & Hold 1/3 (mesma janela, base 1)")
a1.set_yscale("log")
a1.set_title("Patrimonio acumulado (escala log) — mesma janela e base 1")
a1.legend(loc="upper left"); a1.grid(alpha=0.25)
a2.fill_between(drawdown.index, drawdown.values, 0, color="#e34948", alpha=0.35)
a2.set_title("Drawdown (%)"); a2.grid(alpha=0.25)
peso.plot.area(ax=a3, color=[CORES[a] for a in ATIVOS], linewidth=0, alpha=0.85)
a3.set_title("Alocacao (o vazio ate 1 e o caixa em CDI)"); a3.legend(loc="upper left"); a3.set_ylim(0, 1)
fig.tight_layout(); fig.savefig(FIGS / "rotacao.png", dpi=130, facecolor="#fcfcfb")
print(f"Grafico salvo: {FIGS / 'rotacao.png'}")
