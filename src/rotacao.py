"""
Rotacao Momentum v2 — vol target no PORTFOLIO + rebalance SEMANAL
------------------------------------------------------------------
Evolucao da v1 aprovada no walk-forward (diario de pesquisa, F4):
  1. DIRECAO igual a v1: media dos lideres de 4 janelas de momentum.
  2. TAMANHO: vol target aplicado UMA vez, no portfolio (v1 aplicava
     dentro de cada janela e a media suprimia a vol DUAS vezes).
  3. RITMO: pesos congelados por semana (v1 negociava todo dia;
     semanal corta o giro pela metade sem perder a defesa do vol target).
Caixa rende 100% do CDI do ano. Long-only, sem alavancagem, shift(1).
Regua oficial de medicao: 20 bps por perna (lab). 5 bps = custo tabela, so referencia.
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from _paths import DADOS

# ============================ PARAMETROS ============================
CUSTO_OFICIAL   = 0.0020                  # 20 bps/perna — regua do lab / README / promocao
CUSTO_TABELA    = 0.0005                  # 0,05% — corretagem tabela; so linha secundaria
VOL_ALVO        = 0.20                    # volatilidade-alvo anual do PORTFOLIO
JANELA_VOL      = 20                      # dias para medir a volatilidade recente
LOOKBACKS       = [126, 189, 252, 315]   # janelas de momentum (media evita depender de uma)
DIAS_NO_ANO     = 252
ATIVOS          = ["PRIO3", "ITUB3", "ABEV3"]
CDI_POR_ANO = {2008: 0.1238, 2009: 0.0988, 2010: 0.0975, 2011: 0.1160, 2012: 0.0841,
               2013: 0.0806, 2014: 0.1081, 2015: 0.1324, 2016: 0.1400, 2017: 0.0993,
               2018: 0.0642, 2019: 0.0596, 2020: 0.0276, 2021: 0.0442, 2022: 0.1239,
               2023: 0.1304, 2024: 0.1088, 2025: 0.1350, 2026: 0.1500}

# ============================ 1) DADOS ============================
# Historia completa para o lookback; metricas so a partir de 2008 (E37: cortar antes apaga o warm-up).
precos_full = pd.concat(
    {a: pd.read_csv(DADOS / f"{a}.csv", parse_dates=["date"]).set_index("date")["adjustedClose"]
     for a in ATIVOS}, axis=1, sort=True)
precos = precos_full  # lookbacks usam o que existir antes de 2008 (ABEV etc.)
retorno_diario = precos.pct_change()
cdi_anual  = pd.Series(precos.index.year, index=precos.index).map(CDI_POR_ANO)
cdi_diario = (1 + cdi_anual) ** (1 / DIAS_NO_ANO) - 1
AVALIAR_DESDE = "2008"

# ============================ 2) DIRECAO: quem lidera em cada janela ============================
def lider_da_janela(L):
    momentum   = precos.pct_change(L)                          # retorno dos ultimos L dias
    ranking    = momentum.rank(axis=1)
    eh_lider   = ranking.eq(ranking.max(axis=1), axis=0)       # True no ativo mais forte
    peso_lider = eh_lider.astype(float)
    return peso_lider.div(peso_lider.sum(axis=1), axis=0)      # 100% no lider da janela

direcao = sum(lider_da_janela(L) for L in LOOKBACKS) / len(LOOKBACKS)   # media dos 4 votos

# ============================ 3) TAMANHO: vol target UMA vez, no portfolio ============================
retorno_direcao = (direcao.shift(1) * retorno_diario).sum(axis=1)       # retorno da direcao pura
vol_portfolio   = retorno_direcao.rolling(JANELA_VOL).std() * np.sqrt(DIAS_NO_ANO)
fator_vol       = (VOL_ALVO / vol_portfolio).clip(0, 1)                 # cap 1 = sem alavancagem
peso_diario     = direcao.mul(fator_vol, axis=0).fillna(0)

# ============================ 4) RITMO: congela os pesos por semana ============================
peso      = peso_diario.resample("W-FRI").last().reindex(peso_diario.index, method="ffill")
exposicao = peso.sum(axis=1)
caixa     = 1 - exposicao

# ============================ 5) RETORNO (shift(1): sem look-ahead) ============================
ret_invest = (peso.shift(1) * retorno_diario).sum(axis=1)
ret_caixa  = caixa.shift(1) * cdi_diario
giro       = peso.diff().abs().sum(axis=1)
retorno_estrategia = (ret_invest + ret_caixa - giro * CUSTO_OFICIAL).dropna().loc[AVALIAR_DESDE:]
ret_tabela         = (ret_invest + ret_caixa - giro * CUSTO_TABELA).dropna().loc[AVALIAR_DESDE:]
peso = peso.loc[AVALIAR_DESDE:]
exposicao = peso.sum(axis=1)
giro = giro.reindex(retorno_estrategia.index)

# ============================ 6) RESULTADOS (headline = 20 bps; vs zero, igual ao B&H) ============================
patrimonio   = (1 + retorno_estrategia).cumprod()
excesso_cdi  = retorno_estrategia - cdi_diario.reindex(retorno_estrategia.index)
sharpe       = retorno_estrategia.mean() / retorno_estrategia.std() * np.sqrt(DIAS_NO_ANO)
sortino      = retorno_estrategia.mean() / retorno_estrategia[retorno_estrategia < 0].std() * np.sqrt(DIAS_NO_ANO)
sharpe_cdi   = excesso_cdi.mean() / retorno_estrategia.std() * np.sqrt(DIAS_NO_ANO)
max_drawdown = (patrimonio / patrimonio.cummax() - 1).min()
sharpe_5bp   = ret_tabela.mean() / ret_tabela.std() * np.sqrt(DIAS_NO_ANO)

print("=== Rotacao v2: vol target no portfolio + rebalance semanal (20 bps) ===")
print(f"Periodo:          {retorno_estrategia.index[0].date()} a {retorno_estrategia.index[-1].date()}")
print(f"Sharpe (vs zero): {sharpe:.2f}   (liquido do CDI: {sharpe_cdi:.2f};  a 5 bps tabela: {sharpe_5bp:.2f})")
print(f"Sortino (vs zero):{sortino:.2f}")
print(f"Max Drawdown:     {max_drawdown:.0%}")
print(f"Retorno total:    {patrimonio.iloc[-1] - 1:.0%}")
print(f"Giro anual:       {giro.mean() * DIAS_NO_ANO:.0%}  (v1 era ~1.361%)")
print(f"Exposicao media:  {exposicao.mean():.0%}  (resto em caixa a CDI)")
print(f"Alocacao de hoje: " + ", ".join(f"{a}={peso[a].iloc[-1]:.0%}" for a in ATIVOS))
