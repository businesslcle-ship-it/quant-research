"""
Comparativo — Rotacao v2 x v2 sem freio x Dual Momentum x Buy & Hold
--------------------------------------------------------------------
Mesma janela, mesma regua (diaria), tudo liquido de 20 bps/ordem, self-contained
(roda so com os CSVs em dados/). Imprime as metricas e salva comparativo.png
(2 paineis: patrimonio em escala log + drawdown).
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

VOL_ALVO, JANELA_VOL, N, CUSTO = 0.20, 20, 252, 0.0020
LOOKBACKS = [126, 189, 252, 315]
ATIVOS    = ["PRIO3", "ITUB3", "ABEV3"]
CDI_POR_ANO = {2008:0.1238, 2009:0.0988, 2010:0.0975, 2011:0.1160, 2012:0.0841,
               2013:0.0806, 2014:0.1081, 2015:0.1324, 2016:0.1400, 2017:0.0993,
               2018:0.0642, 2019:0.0596, 2020:0.0276, 2021:0.0442, 2022:0.1239,
               2023:0.1304, 2024:0.1088, 2025:0.1350, 2026:0.1500}

# ---------- base diaria ----------
precos = pd.concat({a: pd.read_csv(DADOS / f"{a}.csv", parse_dates=["date"]).set_index("date")["adjustedClose"]
                    for a in ATIVOS}, axis=1, sort=True).loc["2008":]
ret   = precos.pct_change()
cdi_d = (1 + pd.Series(precos.index.year, index=precos.index).map(CDI_POR_ANO)) ** (1/N) - 1
# janela comum: onde os 3 ativos + 12m de historico existem (entra a PRIO em 2015)
INICIO = (precos.dropna().index[0] + pd.Timedelta(days=370)).strftime("%Y-%m")

def lider(mom):
    b = mom.rank(axis=1).eq(mom.rank(axis=1).max(axis=1), axis=0).astype(float)
    return b.div(b.sum(axis=1), axis=0)

def perf(w):
    return ((w.shift(1) * ret).sum(axis=1) + (1 - w.sum(axis=1)).shift(1) * cdi_d
            - w.diff().abs().sum(axis=1) * CUSTO).dropna().loc[INICIO:]

# ---------- Rotacao v2 (freio) e v2 sem freio ----------
direcao = sum(lider(precos.pct_change(L)) for L in LOOKBACKS) / len(LOOKBACKS)
r_dir   = (direcao.shift(1) * ret).sum(axis=1)
fator   = (VOL_ALVO / (r_dir.rolling(JANELA_VOL).std() * np.sqrt(N))).clip(0, 1)
w_freio = direcao.mul(fator, axis=0).fillna(0).resample("W-FRI").last().reindex(precos.index, method="ffill")
w_puro  = direcao.fillna(0).resample("W-FRI").last().reindex(precos.index, method="ffill")
series  = {"Rotacao v2 (freio)": perf(w_freio), "v2 sem freio": perf(w_puro)}

# ---------- Dual Momentum (mensal, replicado em resolucao diaria) ----------
pm    = precos.resample("ME").last()
cdi_m = (1 + pd.Series(pm.index.year, index=pm.index).map(CDI_POR_ANO)) ** (1/12) - 1
mom   = pm.pct_change(12)
led   = mom.dropna(how="all").idxmax(axis=1).reindex(mom.index)
inv   = mom.max(axis=1) > (1 + cdi_m).rolling(12).apply(np.prod, raw=True) - 1
wA = pd.DataFrame(0.0, index=pm.index, columns=ATIVOS)
for t in wA.index[12:]:
    if inv.loc[t]:
        wA.loc[t, led.loc[t]] = 1.0
series["Dual Momentum (livro)"] = perf(wA.reindex(precos.index, method="ffill").fillna(0))
series["Buy & Hold 1/3"]        = ret.mean(axis=1).dropna().loc[INICIO:]

# ---------- metricas ----------
print(f"=== {INICIO} a {precos.index[-1]:%Y-%m} | regua diaria | liquido de 20 bps ===")
print(f"{'estrategia':24}{'CAGR':>7}{'vol':>6}{'Sharpe':>8}{'MaxDD':>7}{'ret total':>11}")
curvas = {}
for nome, r in series.items():
    eq = (1 + r).cumprod(); curvas[nome] = eq
    print(f"{nome:24}{eq.iloc[-1]**(N/len(r))-1:>7.1%}{r.std()*np.sqrt(N):>6.0%}"
          f"{r.mean()/r.std()*np.sqrt(N):>8.2f}{(eq/eq.cummax()-1).min():>7.0%}{eq.iloc[-1]-1:>11.0%}")

# ---------- grafico ----------
CORES = {"Rotacao v2 (freio)": "#2a78d6", "v2 sem freio": "#1baf7a",
         "Dual Momentum (livro)": "#eda100", "Buy & Hold 1/3": "#8a8a85"}
fig, (ax_eq, ax_dd) = plt.subplots(2, 1, figsize=(13, 9), sharex=True,
                                   height_ratios=[2, 1], facecolor="#fcfcfb")
fig.suptitle("Rotacao v2 (freio) x Dual Momentum x Buy & Hold — mesma janela, liquido de 20 bps",
             fontsize=13, weight="bold")
for nome, eq in curvas.items():
    estilo = "--" if nome == "Buy & Hold 1/3" else "-"
    ax_eq.plot(eq.index, eq.values, estilo, color=CORES[nome], lw=2, label=nome)
    ax_dd.plot(eq.index, (eq / eq.cummax() - 1).values * 100, estilo, color=CORES[nome], lw=1.4)
finais = sorted(((eq.iloc[-1], nome) for nome, eq in curvas.items()), reverse=True)
y_ant = None
for valor, nome in finais:
    y = valor if y_ant is None or valor <= y_ant / 1.35 else y_ant / 1.35
    ax_eq.annotate(f" {(valor-1)*100:+,.0f}%".replace(",", "."), xy=(curvas[nome].index[-1], y),
                   color=CORES[nome], fontsize=10, weight="bold", va="center"); y_ant = y
ax_eq.set_yscale("log"); ax_eq.set_ylabel("patrimonio acumulado (log, base 1)")
ax_eq.legend(loc="upper left", frameon=False, fontsize=9); ax_eq.grid(alpha=0.25)
ax_eq.spines[["top", "right"]].set_visible(False)
ax_eq.set_xlim(curvas["Rotacao v2 (freio)"].index[0], curvas["Rotacao v2 (freio)"].index[-1] + pd.Timedelta(days=320))
ax_dd.set_ylabel("drawdown (%)"); ax_dd.grid(alpha=0.25); ax_dd.spines[["top", "right"]].set_visible(False)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig(FIGS / "comparativo.png", dpi=130, facecolor="#fcfcfb")
print(f"\nGrafico salvo: {FIGS / 'comparativo.png'}")
