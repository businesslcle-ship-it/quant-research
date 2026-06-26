"""
Rotacao Momentum + Volatility Targeting (versao legivel)
--------------------------------------------------------
A cada dia: aloca no ativo de maior momentum, dimensionado pela volatilidade.
O capital nao investido rende 100% do CDI do ano. Long-only, sem alavancagem.
"""
import pandas as pd
import numpy as np

# ============================ PARAMETROS ============================
CUSTO_POR_ORDEM = 0.0005                  # 0,05% por ordem (tabela B3 com 90% de desconto)
VOL_ALVO        = 0.20                    # volatilidade-alvo anual = o nivel de risco que a estrategia mira
JANELA_VOL      = 20                      # dias para medir a volatilidade recente
LOOKBACKS       = [126, 189, 252, 315]   # janelas de momentum; a media evita depender de uma so
DIAS_NO_ANO     = 252
ATIVOS          = ["PRIO3", "ITUB3", "ABEV3"]

# CDI acumulado de cada ano (100% do CDI). Valores historicos; recentes (2024-2026) sao estimativas
# a substituir pela serie oficial do Banco Central. O caixa parado rende esta taxa.
CDI_POR_ANO = {
    2008: 0.1238, 2009: 0.0988, 2010: 0.0975, 2011: 0.1160, 2012: 0.0841,
    2013: 0.0806, 2014: 0.1081, 2015: 0.1324, 2016: 0.1400, 2017: 0.0993,
    2018: 0.0642, 2019: 0.0596, 2020: 0.0276, 2021: 0.0442, 2022: 0.1239,
    2023: 0.1304, 2024: 0.1088, 2025: 0.1350, 2026: 0.1500,
}

# ============================ 1) DADOS ============================
# Le o preco ajustado (ja com dividendos) de cada ativo e junta numa tabela, desde 2008.
precos = pd.concat(
    {a: pd.read_csv(f"dados/{a}.csv", parse_dates=["date"]).set_index("date")["adjustedClose"]
     for a in ATIVOS},
    axis=1, sort=True
).loc["2008":]
retorno_diario = precos.pct_change()       # retorno de cada ativo, dia a dia

# CDI diario: pega o CDI anual do ano de cada data e converte para taxa diaria.
cdi_anual  = pd.Series(precos.index.year, index=precos.index).map(CDI_POR_ANO)
cdi_diario = (1 + cdi_anual) ** (1 / DIAS_NO_ANO) - 1

# ============================ 2) ALOCACAO PARA UMA JANELA ============================
def alocacao_para_lookback(L):
    momentum   = precos.pct_change(L)                          # retorno dos ultimos L dias
    ranking    = momentum.rank(axis=1)                         # posicao de cada ativo no dia
    eh_lider   = ranking.eq(ranking.max(axis=1), axis=0)       # True para o ativo mais forte
    peso_lider = eh_lider.astype(float)
    peso_lider = peso_lider.div(peso_lider.sum(axis=1), axis=0)  # 100% no lider

    vol_lider  = (peso_lider * retorno_diario.rolling(JANELA_VOL).std() * np.sqrt(DIAS_NO_ANO)).sum(axis=1)
    fator_vol  = (VOL_ALVO / vol_lider).clip(0, 1)             # vol targeting: cap em 1 = sem alavancagem
    return peso_lider.mul(fator_vol, axis=0).fillna(0)         # peso final desta janela

# ============================ 3) ALOCACAO FINAL = MEDIA DAS 4 JANELAS ============================
peso      = sum(alocacao_para_lookback(L) for L in LOOKBACKS) / len(LOOKBACKS)
exposicao = peso.sum(axis=1)               # quanto do capital esta investido (0 a 1)
caixa     = 1 - exposicao                  # o resto fica em caixa (rende CDI)

# ============================ 4) RETORNO DA ESTRATEGIA ============================
# Regra de ouro: uso a alocacao de ONTEM (shift) para nao usar informacao do futuro.
ret_invest = (peso.shift(1) * retorno_diario).sum(axis=1)         # ganho da parte investida
ret_caixa  = caixa.shift(1) * cdi_diario                          # 100% do CDI sobre o caixa parado
custo      = peso.diff().abs().sum(axis=1) * CUSTO_POR_ORDEM      # custo a cada troca/ajuste
retorno_estrategia = (ret_invest + ret_caixa - custo).dropna()

# ============================ 5) RESULTADOS (em sequencia) ============================
# Sharpe/Sortino medem HABILIDADE -> usam o retorno ACIMA do CDI (CDI nao e alfa, e o piso).
# Ja o patrimonio/retorno total mostram o dinheiro REAL (com o CDI do caixa incluido).
excesso         = retorno_estrategia - cdi_diario.reindex(retorno_estrategia.index)
patrimonio      = (1 + retorno_estrategia).cumprod()
sharpe          = excesso.mean() / retorno_estrategia.std() * np.sqrt(DIAS_NO_ANO)
sortino         = excesso.mean() / retorno_estrategia[retorno_estrategia < 0].std() * np.sqrt(DIAS_NO_ANO)
max_drawdown    = (patrimonio / patrimonio.cummax() - 1).min()
retorno_total   = patrimonio.iloc[-1] - 1
exposicao_media = exposicao.mean()

print("=== Rotacao Momentum + Vol Targeting (caixa rende 100% do CDI do ano) ===")
print(f"Periodo:          {retorno_estrategia.index[0].date()} a {retorno_estrategia.index[-1].date()}")
print(f"Sharpe (vs CDI):  {sharpe:.2f}")
print(f"Sortino (vs CDI): {sortino:.2f}")
print(f"Max Drawdown:     {max_drawdown:.0%}")
print(f"Retorno total:    {retorno_total:.0%}")
print(f"Exposicao media:  {exposicao_media:.0%}  (o resto, {1-exposicao_media:.0%}, em caixa rendendo CDI)")
print(f"Alocacao de hoje: " + ", ".join(f"{a}={peso[a].iloc[-1]:.0%}" for a in ATIVOS))
