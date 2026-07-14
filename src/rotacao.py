"""
Rotacao Momentum v2 — vol target no PORTFOLIO + rebalance SEMANAL
------------------------------------------------------------------
Evolucao da v1 aprovada no walk-forward (diario de pesquisa, F4):
  1. DIRECAO igual a v1: media dos lideres de 4 janelas de momentum.
  2. TAMANHO: vol target aplicado UMA vez, no portfolio (v1 aplicava
     dentro de cada janela e a media suprimia a vol DUAS vezes).
  3. RITMO: pesos congelados por semana (v1 negociava todo dia;
     semanal corta o giro pela metade sem perder a defesa do vol target).
Caixa rende CDI (serie diaria BCB quando disponivel). Long-only, sem
alavancagem, shift(1). Regua oficial: 20 bps/perna; 5 bps = so referencia.
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from _paths import DADOS
from _cdi import cdi_diario

# ============================ PARAMETROS ============================
CUSTO_OFICIAL   = 0.0020                  # 20 bps/perna — regua do lab / README / promocao
CUSTO_TABELA    = 0.0005                  # 0,05% — corretagem tabela; so linha secundaria
VOL_ALVO        = 0.20                    # volatilidade-alvo anual do PORTFOLIO
JANELA_VOL      = 20                      # dias para medir a volatilidade recente
LOOKBACKS       = [126, 189, 252, 315]   # janelas de momentum (media evita depender de uma)
DIAS_NO_ANO     = 252
ATIVOS          = ["PRIO3", "ITUB3", "ABEV3"]

# ============================ 1) DADOS ============================
# Historia completa para o lookback; metricas so a partir de 2008 (E37).
precos = pd.concat(
    {a: pd.read_csv(DADOS / f"{a}.csv", parse_dates=["date"]).set_index("date")["adjustedClose"]
     for a in ATIVOS}, axis=1, sort=True)
retorno_diario = precos.pct_change(fill_method=None)
cdi_diario_s   = cdi_diario(precos.index)
AVALIAR_DESDE  = "2008"

# ============================ 2) DIRECAO ============================
def lider_da_janela(L):
    momentum   = precos.pct_change(L, fill_method=None)
    ranking    = momentum.rank(axis=1)
    eh_lider   = ranking.eq(ranking.max(axis=1), axis=0)
    peso_lider = eh_lider.astype(float)
    return peso_lider.div(peso_lider.sum(axis=1), axis=0)

direcao = sum(lider_da_janela(L) for L in LOOKBACKS) / len(LOOKBACKS)

# ============================ 3) TAMANHO ============================
retorno_direcao = (direcao.shift(1) * retorno_diario).sum(axis=1)
vol_portfolio   = retorno_direcao.rolling(JANELA_VOL).std() * np.sqrt(DIAS_NO_ANO)
fator_vol       = (VOL_ALVO / vol_portfolio).clip(0, 1)
peso_diario     = direcao.mul(fator_vol, axis=0).fillna(0)

# ============================ 4) RITMO ============================
peso      = peso_diario.resample("W-FRI").last().reindex(peso_diario.index, method="ffill")
exposicao = peso.sum(axis=1)
caixa     = 1 - exposicao

# ============================ 5) RETORNO ============================
ret_invest = (peso.shift(1) * retorno_diario).sum(axis=1)
ret_caixa  = caixa.shift(1) * cdi_diario_s
giro       = peso.diff().abs().sum(axis=1)
retorno_estrategia = (ret_invest + ret_caixa - giro * CUSTO_OFICIAL).dropna().loc[AVALIAR_DESDE:]
ret_tabela         = (ret_invest + ret_caixa - giro * CUSTO_TABELA).dropna().loc[AVALIAR_DESDE:]
peso = peso.loc[AVALIAR_DESDE:]
exposicao = peso.sum(axis=1)
giro = giro.reindex(retorno_estrategia.index)

# ============================ 6) RESULTADOS ============================
patrimonio   = (1 + retorno_estrategia).cumprod()
excesso_cdi  = retorno_estrategia - cdi_diario_s.reindex(retorno_estrategia.index)
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
