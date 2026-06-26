"""
Rotacao Momentum + Volatility Targeting (versao legivel, com grafico)
O caixa nao investido rende 100% do CDI do ano. Long-only, sem alavancagem.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================ PARAMETROS ============================
CUSTO_POR_ORDEM = 0.0005
VOL_ALVO        = 0.20
JANELA_VOL      = 20
LOOKBACKS       = [126, 189, 252, 315]
DIAS_NO_ANO     = 252
ATIVOS          = ["PRIO3", "ITUB3", "ABEV3"]
CORES           = {"PRIO3": "tab:orange", "ITUB3": "tab:blue", "ABEV3": "tab:green"}
CDI_POR_ANO = {2008:0.1238, 2009:0.0988, 2010:0.0975, 2011:0.1160, 2012:0.0841,
               2013:0.0806, 2014:0.1081, 2015:0.1324, 2016:0.1400, 2017:0.0993,
               2018:0.0642, 2019:0.0596, 2020:0.0276, 2021:0.0442, 2022:0.1239,
               2023:0.1304, 2024:0.1088, 2025:0.1350, 2026:0.1500}

# ============================ 1) DADOS ============================
precos = pd.concat(
    {a: pd.read_csv(f"dados/{a}.csv", parse_dates=["date"]).set_index("date")["adjustedClose"]
     for a in ATIVOS}, axis=1, sort=True).loc["2008":]
retorno_diario = precos.pct_change()
cdi_anual  = pd.Series(precos.index.year, index=precos.index).map(CDI_POR_ANO)
cdi_diario = (1 + cdi_anual) ** (1 / DIAS_NO_ANO) - 1

# ============================ 2) ALOCACAO PARA UMA JANELA ============================
def alocacao_para_lookback(L):
    momentum   = precos.pct_change(L)
    eh_lider   = momentum.rank(axis=1).eq(momentum.rank(axis=1).max(axis=1), axis=0)
    peso_lider = eh_lider.astype(float)
    peso_lider = peso_lider.div(peso_lider.sum(axis=1), axis=0)
    vol_lider  = (peso_lider * retorno_diario.rolling(JANELA_VOL).std() * np.sqrt(DIAS_NO_ANO)).sum(axis=1)
    fator_vol  = (VOL_ALVO / vol_lider).clip(0, 1)
    return peso_lider.mul(fator_vol, axis=0).fillna(0)

# ============================ 3) ALOCACAO FINAL ============================
peso      = sum(alocacao_para_lookback(L) for L in LOOKBACKS) / len(LOOKBACKS)
exposicao = peso.sum(axis=1)
caixa     = 1 - exposicao

# ============================ 4) RETORNO ============================
ret_invest = (peso.shift(1) * retorno_diario).sum(axis=1)
ret_caixa  = caixa.shift(1) * cdi_diario
custo      = peso.diff().abs().sum(axis=1) * CUSTO_POR_ORDEM
retorno_estrategia = (ret_invest + ret_caixa - custo).dropna()

# ============================ 5) RESULTADOS ============================
excesso      = retorno_estrategia - cdi_diario.reindex(retorno_estrategia.index)
patrimonio   = (1 + retorno_estrategia).cumprod()
buy_hold     = (1 + retorno_diario.mean(axis=1)).cumprod()
drawdown     = (patrimonio / patrimonio.cummax() - 1) * 100
sharpe_cdi   = excesso.mean() / retorno_estrategia.std() * np.sqrt(DIAS_NO_ANO)
sortino_cdi  = excesso.mean() / retorno_estrategia[retorno_estrategia < 0].std() * np.sqrt(DIAS_NO_ANO)
print(f"Sharpe (vs CDI)={sharpe_cdi:.2f}  Sortino={sortino_cdi:.2f}  MaxDD={drawdown.min():.0f}%  ret={patrimonio.iloc[-1]-1:.0%}")

# ============================ 6) GRAFICO (3 paineis) ============================
fig, (ax_patr, ax_dd, ax_aloc) = plt.subplots(3, 1, figsize=(13, 10), sharex=True, height_ratios=[2, 1, 1])

patrimonio.plot(ax=ax_patr, color="green", label="Rotacao (com CDI no caixa)")
buy_hold.plot(ax=ax_patr, color="gray", lw=0.9, label="Buy & Hold")
ax_patr.set_yscale("log"); ax_patr.set_title("Patrimonio acumulado (escala log)")
ax_patr.legend(loc="upper left"); ax_patr.grid(alpha=0.3)

ax_dd.fill_between(drawdown.index, drawdown.values, 0, color="red", alpha=0.35, label="Estrategia")
for ativo in ATIVOS:
    eq = (1 + retorno_diario[ativo]).cumprod()
    ax_dd.plot(eq.index, (eq / eq.cummax() - 1) * 100, color=CORES[ativo], lw=0.7, alpha=0.8, label=ativo)
ax_dd.set_title("Drawdown (%): estrategia vs cada ativo")
ax_dd.legend(loc="lower left", ncol=4, fontsize=8); ax_dd.grid(alpha=0.3)

peso.plot.area(ax=ax_aloc, color=[CORES[a] for a in ATIVOS], linewidth=0, alpha=0.8)
ax_aloc.set_title("Alocacao (qual ativo e quanto; o vazio ate 1 e o caixa em CDI)")
ax_aloc.legend(loc="upper left"); ax_aloc.set_ylim(0, 1)

fig.tight_layout(); fig.savefig("rotacao.png", dpi=130); plt.show()
