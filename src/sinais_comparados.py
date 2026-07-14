"""
Sinais das DUAS estrategias, separados e lado a lado
----------------------------------------------------
Exporta o sinal do Dual Momentum (sinais_dm.csv, mensal) e desenha as duas
alocacoes no mesmo eixo do tempo (sinais_comparados.png):
  - v2  : pesos fracionarios (cada ativo entre 0 e 1) + caixa em CDI
  - Dual Momentum : binario (100% num ativo OU 100% caixa)
Deixa visivel a diferenca de COMPORTAMENTO: a v2 dosa e mantem caixa; o Dual
Momentum aposta tudo ou sai. Self-contained (roda so com dados/).
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from _paths import DADOS, FIGS, OUT
from _cdi import cdi_anual_por_ano

VOL_ALVO, JANELA_VOL, N = 0.20, 20, 252
LOOKBACKS = [126, 189, 252, 315]
ATIVOS = ["PRIO3", "ITUB3", "ABEV3"]
CORES  = {"PRIO3": "#eb6834", "ITUB3": "#2a78d6", "ABEV3": "#1baf7a", "caixa": "#c9c9c2"}
CDI_POR_ANO = cdi_anual_por_ano()

precos = pd.concat({a: pd.read_csv(DADOS / f"{a}.csv", parse_dates=["date"]).set_index("date")["adjustedClose"]
                    for a in ATIVOS}, axis=1, sort=True)  # historia completa (E37)
ret    = precos.pct_change(fill_method=None)
INICIO = (precos.dropna().index[0] + pd.Timedelta(days=370)).strftime("%Y-%m")

# ---------- v2: direcao (media de 4 janelas) -> vol target no portfolio -> semanal ----------
def lider(mom):
    b = mom.rank(axis=1).eq(mom.rank(axis=1).max(axis=1), axis=0).astype(float)
    return b.div(b.sum(axis=1), axis=0)
direcao = sum(lider(precos.pct_change(L, fill_method=None)) for L in LOOKBACKS) / len(LOOKBACKS)
r_dir   = (direcao.shift(1) * ret).sum(axis=1)
fator   = (VOL_ALVO / (r_dir.rolling(JANELA_VOL).std() * np.sqrt(N))).clip(0, 1)
peso_v2 = direcao.mul(fator, axis=0).fillna(0).resample("W-FRI").last().reindex(precos.index, method="ffill").loc[INICIO:]

# ---------- Dual Momentum: mensal, 12m, filtro vs CDI, 100% ou caixa ----------
pm    = precos.resample("ME").last()
cdi_m = (1 + pd.Series(pm.index.year, index=pm.index).map(CDI_POR_ANO)) ** (1/12) - 1
mom   = pm.pct_change(12)
led   = mom.dropna(how="all").idxmax(axis=1).reindex(mom.index)
inv   = mom.max(axis=1) > (1 + cdi_m).rolling(12).apply(np.prod, raw=True) - 1
peso_dm_m = pd.DataFrame(0.0, index=pm.index, columns=ATIVOS)
for t in peso_dm_m.index[12:]:
    if inv.loc[t]:
        peso_dm_m.loc[t, led.loc[t]] = 1.0

# ---------- exporta o sinal do Dual Momentum (SEPARADO do da v2) ----------
sinal_dm = peso_dm_m.copy()
sinal_dm["caixa"] = 1 - sinal_dm.sum(axis=1)
sinal_dm["lider"] = led.where(inv, "CAIXA")
sinal_dm = sinal_dm.loc[INICIO:]
sinal_dm.to_csv(OUT / "sinais_dm.csv")
print(f"{OUT / 'sinais_dm.csv'}  ({len(sinal_dm)} meses)  | alocacao de hoje: {sinal_dm['lider'].iloc[-1]}")
print(f"sinais_*.csv (v2) sao separados: v2 = pesos diarios fracionarios; DM = alocacao mensal binaria")

# ---------- visualizacao: as duas alocacoes lado a lado ----------
peso_dm_d = peso_dm_m.reindex(precos.index, method="ffill").fillna(0).loc[INICIO:]
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True, facecolor="#fcfcfb")
fig.suptitle("Como cada estrategia aloca — v2 (dosa + caixa) vs Dual Momentum (tudo ou nada)",
             fontsize=13, weight="bold")
for ax, peso, titulo in [(ax1, peso_v2, "Rotacao v2 — pesos fracionarios (o vazio ate 1 e caixa em CDI)"),
                         (ax2, peso_dm_d, "Dual Momentum — 100% num ativo ou 100% caixa")]:
    ax.stackplot(peso.index, [peso[a] for a in ATIVOS], colors=[CORES[a] for a in ATIVOS],
                 labels=ATIVOS, alpha=0.9)
    ax.fill_between(peso.index, peso.sum(axis=1), 1, color=CORES["caixa"], alpha=0.7, label="caixa (CDI)")
    ax.set_title(titulo, fontsize=10); ax.set_ylim(0, 1); ax.margins(x=0)
ax1.legend(loc="upper left", ncol=4, fontsize=8, framealpha=0.9)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(FIGS / "sinais_comparados.png", dpi=130, facecolor="#fcfcfb")
print(f"Grafico salvo: {FIGS / 'sinais_comparados.png'}")
