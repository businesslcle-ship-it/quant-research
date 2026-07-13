# -*- coding: utf-8 -*-
"""
Grafico da apresentacao: Dual Momentum 60min (dois relogios) vs baseline mensal,
Buy & Hold 1/3 e CDI. Mesmos numeros dos scripts dual_momentum_60min.py (curva
horaria, amostrada no fim do dia para o grafico) e dual_momentum_mensal.py.
Gera dual_momentum/dm_vs_benchmark.png. Rodar da raiz Quantitative.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CUSTO, BUFFER, LOOKBACK, HORAS_POR_ANO = 0.0020, 0.05, 140, 252 * 7
ATIVOS = ['PRIO3', 'ITUB3', 'ABEV3']
CDI_POR_ANO = {2016: 0.1400, 2017: 0.0993, 2018: 0.0642, 2019: 0.0596, 2020: 0.0276,
               2021: 0.0442, 2022: 0.1239, 2023: 0.1304, 2024: 0.1088, 2025: 0.1350,
               2026: 0.1500}

base = pd.read_csv('dados/base_plana.csv', parse_dates=['data'])

# %% 1) DM 60min — dois relogios (identico ao dual_momentum_60min.py)
df = base[base['hora'] != 'dia'].copy()
df['timestamp'] = pd.to_datetime(df['data'].dt.strftime('%Y-%m-%d') + ' ' + df['hora'])
fech_h = df.sort_values('timestamp').set_index('timestamp')[[f'{a}_fechamento' for a in ATIVOS]]
fech_h.columns = ATIVOS
ret_h = fech_h.pct_change()
cdi_hora = pd.Series((1 + fech_h.index.year.map(CDI_POR_ANO)) ** (1/HORAS_POR_ANO) - 1, index=fech_h.index)
cdi_acum = (1 + cdi_hora).rolling(LOOKBACK).apply(np.prod, raw=True) - 1
mom_h = fech_h.pct_change(LOOKBACK)

M, C, R, CDI = mom_h.values, cdi_acum.values, ret_h.values, cdi_hora.values
novo_dia = np.r_[True, fech_h.index.normalize()[1:] != fech_h.index.normalize()[:-1]]
posicao, investe = -1, False
ret_barra = np.zeros(len(fech_h))
for t in range(LOOKBACK + 1, len(fech_h) - 1):
    m = M[t]
    if np.isnan(m).all() or np.isnan(C[t]):
        continue
    lider = int(np.nanargmax(m))
    if novo_dia[t]:
        investe = m[lider] > C[t]
    alvo = posicao
    if not investe:
        alvo = -1
    elif posicao == -1:
        alvo = lider
    elif lider != posicao and m[lider] - m[posicao] > BUFFER:
        alvo = lider
    pernas = (alvo != posicao) * ((posicao != -1) + (alvo != -1))
    posicao = alvo
    ganho = R[t + 1, posicao] if posicao != -1 else CDI[t + 1]
    ret_barra[t + 1] = (0.0 if np.isnan(ganho) else ganho) - pernas * CUSTO
ret_dm60 = pd.Series(ret_barra, index=fech_h.index).iloc[LOOKBACK + 2:]
eq_dm60  = (1 + ret_dm60).cumprod()
sh_dm60  = ret_dm60.mean() / ret_dm60.std() * np.sqrt(HORAS_POR_ANO)
dd_dm60  = (eq_dm60 / eq_dm60.cummax() - 1).min()
eq_dm60_dia = eq_dm60.resample('D').last().dropna()          # amostra diaria SO para desenhar

# %% 2) Baseline mensal fiel + B&H 1/3 + CDI (identico ao dual_momentum_mensal.py)
fech_d = (base[base['hora'] == 'dia'].set_index('data')[[f'{a}_fechamento' for a in ATIVOS]])
fech_d.columns = ATIVOS
mensal = fech_d.resample('ME').last()
ret_m = mensal.pct_change()
cdi_mes = (1 + pd.Series(mensal.index.year, index=mensal.index).map(CDI_POR_ANO)) ** (1/12) - 1
cdi_12m = (1 + cdi_mes).rolling(12).apply(np.prod, raw=True) - 1
mom_m = mensal.pct_change(12)
lider_m = mom_m.dropna(how='all').idxmax(axis=1).reindex(mom_m.index)
investe_m = mom_m.max(axis=1) > cdi_12m
peso_m = pd.get_dummies(lider_m).reindex(index=mensal.index, columns=ATIVOS, fill_value=False)
peso_m = peso_m.mul(investe_m, axis=0).astype(float)
ret_gem = ((peso_m.shift(1) * ret_m).sum(axis=1) + (1 - peso_m.sum(axis=1)).shift(1) * cdi_mes
           - peso_m.diff().abs().sum(axis=1) * CUSTO).iloc[13:]
ret_bh  = ret_m.mean(axis=1).iloc[13:]

def resumo(r, periodos):
    eq = (1 + r).cumprod()
    return eq, r.mean() / r.std() * np.sqrt(periodos), (eq / eq.cummax() - 1).min()

eq_gem, sh_gem, dd_gem = resumo(ret_gem, 12)
eq_bh,  sh_bh,  dd_bh  = resumo(ret_bh, 12)
eq_cdi = (1 + cdi_mes.iloc[13:]).cumprod()

# %% 3) O grafico: patrimonio (log) + drawdown
fig, (em_cima, embaixo) = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                                       gridspec_kw={'height_ratios': [3, 1]})
em_cima.plot(eq_dm60_dia, color='#0b6e4f', lw=2,
             label=f'DM 60min dois relogios   Sharpe {sh_dm60:.2f} | MaxDD {dd_dm60:.0%} (horaria) | {eq_dm60.iloc[-1]-1:+.0%}')
em_cima.plot(eq_gem, color='#1f4e79', lw=1.6,
             label=f'Baseline fiel mensal        Sharpe {sh_gem:.2f} | MaxDD {dd_gem:.0%} (mensal) | {eq_gem.iloc[-1]-1:+.0%}')
em_cima.plot(eq_bh, color='#d17a22', lw=1.4,
             label=f'Buy & Hold 1/3               Sharpe {sh_bh:.2f} | MaxDD {dd_bh:.0%} (mensal) | {eq_bh.iloc[-1]-1:+.0%}')
em_cima.plot(eq_cdi, color='gray', lw=1.2, ls='--', label=f'CDI  {eq_cdi.iloc[-1]-1:+.0%}')
em_cima.set_yscale('log')
em_cima.set_title('Dual Momentum nos 60min (dois relogios) vs baseline mensal e benchmark — liquido de 20 bps')
em_cima.legend(loc='upper left', fontsize=9)
em_cima.grid(alpha=0.3)

embaixo.fill_between(eq_dm60_dia.index, eq_dm60_dia / eq_dm60_dia.cummax() - 1, 0, color='#0b6e4f', alpha=0.5)
embaixo.fill_between(eq_gem.index, eq_gem / eq_gem.cummax() - 1, 0, color='#1f4e79', alpha=0.35)
embaixo.set_ylabel('Drawdown')
embaixo.grid(alpha=0.3)

fig.tight_layout()
fig.savefig('dual_momentum/dm_vs_benchmark.png', dpi=150)
print(f'dm_vs_benchmark.png salvo | DM60: {sh_dm60:.2f}/{dd_dm60:.0%} | baseline: {sh_gem:.2f}/{dd_gem:.0%} | B&H: {sh_bh:.2f}/{dd_bh:.0%}')
