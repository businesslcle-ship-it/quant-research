# -*- coding: utf-8 -*-
"""
Dual Momentum nos 60 minutos — FIEL AO LIVRO (12 meses por calendario) + histerese
-----------------------------------------------------------------------------------
As duas pernas do livro (Antonacci), intactas, avaliadas a cada barra de 60min:
  RELATIVO : fica no ativo de maior retorno de 12 MESES por CALENDARIO.
  ABSOLUTO : so investe se esse lider superar o CDI acumulado dos MESMOS 12 meses;
             senao, 100% em caixa rendendo CDI.
Uma unica concessao para nao ser vaporizado por custo na frequencia horaria:
  HISTERESE de 5% -> so troca de lider se o desafiante ganhar por mais de 5%.
  (O rebal mensal do livro ja e uma histerese de TEMPO; avaliando barra a barra,
   o amortecedor vira PRECO. Sem ele o lider pisca nos cruzamentos: 455 trocas e
   22%/ano de custo -> ver E36a no diario.)
Sem look-ahead: o sinal da barra t paga na barra t+1. Custo: 20 bps por perna.
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
CUSTO         = 0.0020                     # 0,20% por perna (trocar de ativo = 2 pernas)
BUFFER        = 0.05                        # so troca de lider se ganhar por +5% de momentum
HORAS_POR_ANO = 252 * 7                     # ~1.764 barras de 60min num ano de pregao
ATIVOS        = ['PRIO3', 'ITUB3', 'ABEV3']
CDI_POR_ANO   = {2016: 0.1400, 2017: 0.0993, 2018: 0.0642, 2019: 0.0596, 2020: 0.0276,
                 2021: 0.0442, 2022: 0.1239, 2023: 0.1304, 2024: 0.1088, 2025: 0.1350,
                 2026: 0.1500}

# ============================ 1) DADOS: as barras de 60 minutos ============================
# Da base plana pego so as barras horarias (descarto a linha-resumo 'dia') e remonto o relogio real.
base = pd.read_csv(DADOS / 'base_plana.csv', parse_dates=['data'])
barras = base[base['hora'] != 'dia'].copy()
barras['timestamp'] = pd.to_datetime(barras['data'].dt.strftime('%Y-%m-%d') + ' ' + barras['hora'])
preco = (barras.sort_values('timestamp').set_index('timestamp')[[f'{a}_fechamento' for a in ATIVOS]])
preco.columns = ATIVOS
retorno_ativo = preco.pct_change()                                   # retorno de cada ativo, barra a barra
cdi_barra = pd.Series((1 + preco.index.year.map(CDI_POR_ANO)) ** (1/HORAS_POR_ANO) - 1, index=preco.index)

# ============================ 2) AS DUAS PERNAS, POR CALENDARIO ============================
# 12 meses "de verdade": para cada barra acho a barra mais proxima de 365 dias CORRIDOS atras
# (contar barras esticaria o ano e perderia Sharpe -> E25). searchsorted faz isso vetorizado.
ha_um_ano = preco.index.searchsorted(preco.index - pd.Timedelta(days=365), side='right') - 1
tem_12m   = ha_um_ano >= 0                                            # False no 1o ano (sem historico)

momento = np.full(preco.shape, np.nan)                               # perna RELATIVA: retorno de 12m de cada ativo
momento[tem_12m] = preco.values[tem_12m] / preco.values[ha_um_ano[tem_12m]] - 1

cdi_acum = np.log1p(cdi_barra.values).cumsum()                       # truque do log: soma vira produto
barreira = np.full(len(preco), np.nan)                               # perna ABSOLUTA: CDI acumulado nos MESMOS 12m
barreira[tem_12m] = np.expm1(cdi_acum[tem_12m] - cdi_acum[ha_um_ano[tem_12m]])

# ============================ 3) A REGRA DO LIVRO PARA UMA BARRA ============================
def onde_ficar(momento_barra, barreira_barra, posicao_atual):
    """Onde a carteira fica nesta barra: indice do ativo (0,1,2) ou -1 = caixa.
    As duas pernas do livro + a histerese, na ordem em que o livro decide."""
    lider = int(np.nanargmax(momento_barra))                          # o mais forte em 12 meses
    if momento_barra[lider] <= barreira_barra:                        # ABSOLUTA: nem o lider bate o CDI -> caixa
        return -1
    if posicao_atual == -1:                                           # estava em caixa e agora pode investir -> entra
        return lider
    if lider != posicao_atual and momento_barra[lider] - momento_barra[posicao_atual] > BUFFER:
        return lider                                                  # RELATIVA com histerese: troca so por +5%
    return posicao_atual                                             # vantagem pequena -> fica onde esta

# ============================ 4) PASSA BARRA A BARRA (a histerese exige memoria do passado) ============================
posicao       = -1                                                   # comeca em caixa
retorno_bar   = np.zeros(len(preco))
trocas_lider  = 0                                                     # trocas entre ativos (perna relativa)
trocas_caixa  = 0                                                    # entradas/saidas do caixa (perna absoluta)
custo_total   = 0.0
for t in range(len(preco) - 1):
    if np.isnan(momento[t]).all() or np.isnan(barreira[t]):
        continue                                                     # ainda sem 12 meses de historico
    alvo = onde_ficar(momento[t], barreira[t], posicao)
    if alvo != posicao:                                              # houve troca: conta as pernas e o custo
        ordens = (posicao != -1) + (alvo != -1)                      # vender o antigo e/ou comprar o novo
        custo_total += ordens * CUSTO
        if posicao == -1 or alvo == -1:
            trocas_caixa += 1
        else:
            trocas_lider += 1
    else:
        ordens = 0
    posicao = alvo
    ganho = retorno_ativo.values[t + 1, posicao] if posicao != -1 else cdi_barra.values[t + 1]
    retorno_bar[t + 1] = (0.0 if np.isnan(ganho) else ganho) - ordens * CUSTO   # sinal de t paga em t+1, ja liquido

# ============================ 5) RESULTADOS ============================
retorno_estrategia = pd.Series(retorno_bar, index=preco.index)
retorno_estrategia = retorno_estrategia.loc[retorno_estrategia.ne(0).idxmax():]   # comeca no 1o retorno real
patrimonio    = (1 + retorno_estrategia).cumprod()
anos          = len(retorno_estrategia) / HORAS_POR_ANO
sharpe        = retorno_estrategia.mean() / retorno_estrategia.std() * np.sqrt(HORAS_POR_ANO)
max_drawdown  = (patrimonio / patrimonio.cummax() - 1).min()
retorno_total = patrimonio.iloc[-1] - 1
custo_ano     = custo_total / anos
posicao_hoje  = ATIVOS[posicao] if posicao != -1 else 'CAIXA'

# robustez: o Sharpe funciona em cada pedaco do tempo, ou so no agregado?
blocos = {}
for inicio, fim in [(2017, 2019), (2020, 2022), (2023, 2026)]:
    r = retorno_estrategia.loc[str(inicio):str(fim)]
    blocos[f'{inicio}-{fim}'] = r.mean() / r.std() * np.sqrt(HORAS_POR_ANO)

print('=== Dual Momentum 60min — fiel ao livro (12m por calendario) + histerese 5% ===')
print(f'Periodo: {retorno_estrategia.index[0]:%Y-%m} a {retorno_estrategia.index[-1]:%Y-%m} | decisao a cada barra de 60min')
print(f'Sharpe {sharpe:.2f} | MaxDD {max_drawdown:.0%} (regua HORARIA, a mais dura) | retorno {retorno_total:.0%}')
print(f'Trocas: {trocas_lider} de lider + {trocas_caixa} do caixa | custo {custo_ano:.1%}/ano | posicao hoje: {posicao_hoje}')
print('Sharpe por bloco: ' + ' | '.join(f'{nome}: {s:.2f}' for nome, s in blocos.items()))
print('Baseline fiel mensal (dual_momentum_mensal.py): Sharpe 1.04 | MaxDD -65% mensal | +3853%')
