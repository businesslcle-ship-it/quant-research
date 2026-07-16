"""
Comparativo — Rotacao v2 x Dual Momentum x Buy & Hold x estrategia-propria
--------------------------------------------------------------------------
Mesma janela calendário, régua diária. Ativas líquidas de 20 bps/perna.
Buy & Hold 1/3 sem corretagem.

estrategia-propria = breadth Path B 145 (série exportada do lab E48, combo 3/6/9/12m).
UNIVERSO DISTINTO dos 3 ativos — curva alinhada só no calendário.
Lookbacks v2/DM usam história completa (E37); avaliação desde INICIO.
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
from _cdi import cdi_diario, cdi_anual_por_ano

VOL_ALVO, JANELA_VOL, N, CUSTO = 0.20, 20, 252, 0.0020
LOOKBACKS = [126, 189, 252, 315]
ATIVOS    = ["PRIO3", "ITUB3", "ABEV3"]
CDI_POR_ANO = cdi_anual_por_ano()

precos = pd.concat({a: pd.read_csv(DADOS / f"{a}.csv", parse_dates=["date"]).set_index("date")["adjustedClose"]
                    for a in ATIVOS}, axis=1, sort=True)
ret   = precos.pct_change(fill_method=None)
cdi_d = cdi_diario(precos.index)
INICIO = (precos.dropna().index[0] + pd.Timedelta(days=370)).strftime("%Y-%m")

def lider(mom):
    b = mom.rank(axis=1).eq(mom.rank(axis=1).max(axis=1), axis=0).astype(float)
    return b.div(b.sum(axis=1), axis=0)

def perf(w):
    return ((w.shift(1) * ret).sum(axis=1) + (1 - w.sum(axis=1)).shift(1) * cdi_d
            - w.diff().abs().sum(axis=1) * CUSTO).dropna().loc[INICIO:]

direcao = sum(lider(precos.pct_change(L, fill_method=None)) for L in LOOKBACKS) / len(LOOKBACKS)
r_dir   = (direcao.shift(1) * ret).sum(axis=1)
fator   = (VOL_ALVO / (r_dir.rolling(JANELA_VOL).std() * np.sqrt(N))).clip(0, 1)
w_freio = direcao.mul(fator, axis=0).fillna(0).resample("W-FRI").last().reindex(precos.index, method="ffill")
w_puro  = direcao.fillna(0).resample("W-FRI").last().reindex(precos.index, method="ffill")
series  = {"Rotacao v2 (freio)": perf(w_freio), "v2 sem freio": perf(w_puro)}

pm    = precos.resample("ME").last()
cdi_m = (1 + pd.Series(pm.index.year, index=pm.index).map(CDI_POR_ANO)) ** (1 / 12) - 1
mom   = pm.pct_change(12)
led   = mom.dropna(how="all").idxmax(axis=1).reindex(mom.index)
inv   = mom.max(axis=1) > (1 + cdi_m).rolling(12).apply(np.prod, raw=True) - 1
wA = pd.DataFrame(0.0, index=pm.index, columns=ATIVOS)
for t in wA.index[12:]:
    if inv.loc[t]:
        wA.loc[t, led.loc[t]] = 1.0
series["Dual Momentum (livro)"] = perf(wA.reindex(precos.index, method="ffill").fillna(0))
series["Buy & Hold 1/3"]        = ret.mean(axis=1).dropna().loc[INICIO:]

ep_path = DADOS / "estrategia_propria_diario.csv"
assert ep_path.exists(), f"Falta {ep_path} (export lab E45 → estrategia-propria)"
ep = pd.read_csv(ep_path, parse_dates=["dia"]).set_index("dia")["retorno_liquido"]
series["estrategia-propria"] = ep.dropna().loc[INICIO:]
print(
    "AVISO: estrategia-propria = Path B 145 (lab E48, combo 3/6/9/12m). "
    "Universo DISTINTO dos 3 ativos; não é apples-to-apples de painel."
)

print(f"{INICIO}→{precos.index[-1]:%Y-%m} | ativas @20bps; B&H sem corretagem")
print(f"{'estrategia':24}{'CAGR':>7}{'vol':>6}{'Sharpe':>8}{'MaxDD':>7}{'ret':>11}")
curvas = {}
for nome, r in series.items():
    eq = (1 + r).cumprod(); curvas[nome] = eq
    if not (0.9 <= float(eq.iloc[0]) <= 1.1):
        raise AssertionError(f"{nome}: equity deve comecar ~1, veio {eq.iloc[0]:.3f}")
    print(f"{nome:24}{eq.iloc[-1]**(N/len(r))-1:>7.1%}{r.std()*np.sqrt(N):>6.0%}"
          f"{r.mean()/r.std()*np.sqrt(N):>8.2f}{(eq/eq.cummax()-1).min():>7.0%}{eq.iloc[-1]-1:>11.0%}")

CORES = {"Rotacao v2 (freio)": "#2a78d6", "v2 sem freio": "#1baf7a",
         "Dual Momentum (livro)": "#eda100", "Buy & Hold 1/3": "#8a8a85",
         "estrategia-propria": "#c0392b"}
fig, (ax_eq, ax_dd) = plt.subplots(2, 1, figsize=(13, 9), sharex=True,
                                   height_ratios=[2, 1], facecolor="#fcfcfb")
fig.suptitle(
    "Comparativo — mesma janela calendário @20 bps\n"
    "(estrategia-propria = Path B 145; demais = 3 ativos)",
    fontsize=12, weight="bold",
)
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
print(f"fig {FIGS / 'comparativo.png'}")
