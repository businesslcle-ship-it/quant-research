# -*- coding: utf-8 -*-
"""
Dual Momentum nos 60 minutos — DOIS RELOGIOS (nucleo do livro + engenharia medida)
  Nucleo do livro (Antonacci):
    RELATIVO : fica no lider por momentum;  ABSOLUTO : so investe se o lider
    superar o CDI acumulado do mesmo periodo; senao, 100% caixa a CDI.
  Duas melhorias de engenharia, medidas em laboratorio (diario E30/E32/E33):
    1. HISTERESE  : so troca de lider se o desafiante vencer por >5%
       (a fronteira de custo tem PLATO em 5-12%, nao pico — E32)
    2. DOIS RELOGIOS: a perna relativa decide a cada barra de 60min; a perna
       absoluta so pode mudar de estado na 1a barra do dia — o liga-desliga
       horario do caixa era o monstro do custo (625 trocas vs 100 — E32)
  Sinal da barra t paga na barra t+1. Custos: 20 bps por perna.
Requer dados/base_plana.csv (gerada pelo montar_base.py).
"""
import pandas as pd
import numpy as np

CUSTO    = 0.0020
BUFFER   = 0.05                       # vantagem minima para trocar de lider
LOOKBACK = 140                        # ~20 dias uteis em barras de 60min
HORAS_POR_ANO = 252 * 7
ATIVOS = ['PRIO3', 'ITUB3', 'ABEV3']
CDI_POR_ANO = {2016: 0.1400, 2017: 0.0993, 2018: 0.0642, 2019: 0.0596, 2020: 0.0276,
               2021: 0.0442, 2022: 0.1239, 2023: 0.1304, 2024: 0.1088, 2025: 0.1350,
               2026: 0.1500}

# %% 1) Barras de 60min com o timestamp real (exclui a linha 'dia')
base = pd.read_csv('dados/base_plana.csv', parse_dates=['data'])
df = base[base['hora'] != 'dia'].copy()
df['timestamp'] = pd.to_datetime(df['data'].dt.strftime('%Y-%m-%d') + ' ' + df['hora'])
fech = df.sort_values('timestamp').set_index('timestamp')[[f'{a}_fechamento' for a in ATIVOS]]
fech.columns = ATIVOS
retorno = fech.pct_change()

cdi_hora = pd.Series((1 + fech.index.year.map(CDI_POR_ANO)) ** (1/HORAS_POR_ANO) - 1, index=fech.index)
cdi_acum = (1 + cdi_hora).rolling(LOOKBACK).apply(np.prod, raw=True) - 1
momentum = fech.pct_change(LOOKBACK)

# %% 2) A maquina de estados: dois relogios + histerese, barra a barra
M, C, R, CDI = momentum.values, cdi_acum.values, retorno.values, cdi_hora.values
novo_dia = np.r_[True, fech.index.normalize()[1:] != fech.index.normalize()[:-1]]

posicao, investe = -1, False                       # -1 = caixa
ret_barra = np.zeros(len(fech))
trocas_relativas = trocas_absolutas = 0
custo_pago = 0.0

for t in range(LOOKBACK + 1, len(fech) - 1):
    m = M[t]
    if np.isnan(m).all() or np.isnan(C[t]):
        continue
    lider = int(np.nanargmax(m))
    if novo_dia[t]:                                # relogio LENTO: absoluto decide 1x por dia
        investe = m[lider] > C[t]
    alvo = posicao
    if not investe:                                # perna absoluta manda pro caixa
        alvo = -1
    elif posicao == -1:                            # saindo do caixa: entra no lider
        alvo = lider
    elif lider != posicao and m[lider] - m[posicao] > BUFFER:   # histerese na troca
        alvo = lider
    pernas = 0
    if alvo != posicao:
        pernas = (posicao != -1) + (alvo != -1)    # vender um e/ou comprar outro
        if alvo == -1 or posicao == -1:
            trocas_absolutas += 1
        else:
            trocas_relativas += 1
        custo_pago += pernas * CUSTO
    posicao = alvo
    ganho = R[t + 1, posicao] if posicao != -1 else CDI[t + 1]
    ret_barra[t + 1] = (0.0 if np.isnan(ganho) else ganho) - pernas * CUSTO

# %% 3) Resultados NOMEADOS
ret_estrategia = pd.Series(ret_barra, index=fech.index).iloc[LOOKBACK + 2:]
patrimonio    = (1 + ret_estrategia).cumprod()
anos          = len(ret_estrategia) / HORAS_POR_ANO
sharpe        = ret_estrategia.mean() / ret_estrategia.std() * np.sqrt(HORAS_POR_ANO)
drawdown_max  = (patrimonio / patrimonio.cummax() - 1).min()
retorno_total = patrimonio.iloc[-1] - 1
custo_ano     = custo_pago / anos
posicao_hoje  = ATIVOS[posicao] if posicao != -1 else 'CAIXA'

blocos = {}
for inicio, fim in [(2016, 2019), (2020, 2022), (2023, 2026)]:
    r = ret_estrategia.loc[str(inicio):str(fim)]
    blocos[f'{inicio}-{fim}'] = r.mean() / r.std() * np.sqrt(HORAS_POR_ANO)

print('=== Dual Momentum 60min — dois relogios (nucleo do livro + histerese 5%) ===')
print(f'Periodo: {ret_estrategia.index[0]:%Y-%m} a {ret_estrategia.index[-1]:%Y-%m} | decisao a cada barra de 60min')
print(f'Sharpe {sharpe:.2f} | MaxDD {drawdown_max:.0%} (regua HORARIA, a mais dura) | retorno {retorno_total:.0%}')
print(f'Trocas: {trocas_relativas} de lider + {trocas_absolutas} do caixa | custo {custo_ano:.1%}/ano | posicao hoje: {posicao_hoje}')
print('Sharpe por bloco: ' + ' | '.join(f'{nome}: {s:.2f}' for nome, s in blocos.items()))
print('Baseline fiel mensal (dual_momentum_mensal.py): Sharpe 1.04 | MaxDD -65% mensal | +3853%')
