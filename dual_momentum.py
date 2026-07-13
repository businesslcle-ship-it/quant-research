# -*- coding: utf-8 -*-
"""
Dual Momentum nos 60 minutos — FIEL AO LIVRO (12 meses por calendario) + histerese
  Nucleo do livro (Antonacci), intacto:
    RELATIVO : lider pelo retorno de 12 MESES por CALENDARIO (nunca contagem de barras — E25)
    ABSOLUTO : so investe se o lider superar o CDI acumulado dos MESMOS 12 meses
    ALOCACAO : 100% no lider, ou 100% em caixa a CDI
  Avaliado a cada barra de 60min (o timestamp real do mentor), com UMA concessao:
    HISTERESE de 5% na troca de lider. O rebal mensal do livro ja e uma histerese
    de TEMPO; avaliando por barra, o amortecedor vira PRECO — sem ele o lider
    pisca nos cruzamentos e o custo mata (455 trocas, 22%/ano — E36a).
  Sinal da barra t paga na barra t+1. Custos: 20 bps por perna.
Requer dados/base_plana.csv (gerada pelo montar_base.py).
"""
import pandas as pd
import numpy as np

CUSTO  = 0.0020
BUFFER = 0.05                          # vantagem minima de momentum para trocar de lider
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

# %% 2) As duas pernas do livro, por CALENDARIO: 12 meses atras = a barra mais proxima <= T-365d
um_ano_atras = fech.index.searchsorted(fech.index - pd.Timedelta(days=365), side='right') - 1
tem_historico = um_ano_atras >= 0
precos = fech.values
momentum = np.full_like(precos, np.nan, dtype=float)
momentum[tem_historico] = precos[tem_historico] / precos[um_ano_atras[tem_historico]] - 1

cdi_log_acum = np.log1p(cdi_hora.values).cumsum()                 # CDI acumulado entre as MESMAS datas
barreira = np.full(len(fech), np.nan)
barreira[tem_historico] = np.expm1(cdi_log_acum[tem_historico] - cdi_log_acum[um_ano_atras[tem_historico]])

# %% 3) Barra a barra: o livro decide, a histerese amortece
M, R, CDI = momentum, retorno.values, cdi_hora.values
posicao = -1                                                       # -1 = caixa
ret_barra = np.zeros(len(fech))
trocas_lider = trocas_caixa = 0
custo_pago = 0.0

for t in range(len(fech) - 1):
    m = M[t]
    if np.isnan(m).all() or np.isnan(barreira[t]):
        continue
    lider = int(np.nanargmax(m))
    investe = m[lider] > barreira[t]                               # perna absoluta do livro
    alvo = posicao
    if not investe:                                                # lider abaixo do CDI: caixa
        alvo = -1
    elif posicao == -1:                                            # saindo do caixa: entra no lider
        alvo = lider
    elif lider != posicao and m[lider] - m[posicao] > BUFFER:      # troca so com vantagem real
        alvo = lider
    pernas = 0
    if alvo != posicao:
        pernas = (posicao != -1) + (alvo != -1)                    # vender um e/ou comprar outro
        if alvo == -1 or posicao == -1:
            trocas_caixa += 1
        else:
            trocas_lider += 1
        custo_pago += pernas * CUSTO
    posicao = alvo
    ganho = R[t + 1, posicao] if posicao != -1 else CDI[t + 1]
    ret_barra[t + 1] = (0.0 if np.isnan(ganho) else ganho) - pernas * CUSTO

# %% 4) Resultados NOMEADOS
ret_estrategia = pd.Series(ret_barra, index=fech.index)
ret_estrategia = ret_estrategia.loc[ret_estrategia.ne(0).idxmax():]   # comeca no 1o retorno
patrimonio    = (1 + ret_estrategia).cumprod()
anos          = len(ret_estrategia) / HORAS_POR_ANO
sharpe        = ret_estrategia.mean() / ret_estrategia.std() * np.sqrt(HORAS_POR_ANO)
drawdown_max  = (patrimonio / patrimonio.cummax() - 1).min()
retorno_total = patrimonio.iloc[-1] - 1
custo_ano     = custo_pago / anos
posicao_hoje  = ATIVOS[posicao] if posicao != -1 else 'CAIXA'

blocos = {}
for inicio, fim in [(2017, 2019), (2020, 2022), (2023, 2026)]:
    r = ret_estrategia.loc[str(inicio):str(fim)]
    blocos[f'{inicio}-{fim}'] = r.mean() / r.std() * np.sqrt(HORAS_POR_ANO)

print('=== Dual Momentum 60min — fiel ao livro (12m por calendario) + histerese 5% ===')
print(f'Periodo: {ret_estrategia.index[0]:%Y-%m} a {ret_estrategia.index[-1]:%Y-%m} | decisao a cada barra de 60min')
print(f'Sharpe {sharpe:.2f} | MaxDD {drawdown_max:.0%} (regua HORARIA, a mais dura) | retorno {retorno_total:.0%}')
print(f'Trocas: {trocas_lider} de lider + {trocas_caixa} do caixa | custo {custo_ano:.1%}/ano | posicao hoje: {posicao_hoje}')
print('Sharpe por bloco: ' + ' | '.join(f'{nome}: {s:.2f}' for nome, s in blocos.items()))
print('Baseline fiel mensal (dual_momentum_mensal.py): Sharpe 1.04 | MaxDD -65% mensal | +3853%')
