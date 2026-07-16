# Pseudocódigo — estrategia-propria

Nome oficial: **estratégia-própria**.  
Versão oficial de sinal: **E48** — combinação de horizontes {3, 6, 9, 12} meses.  
Arquivo histórico: E45 = momentum único de 365 dias (substituído na promoção E48).

Universo **distinto** da Rotação v2 / Dual Momentum (3 ativos): Path B 145.

## Contrato

- Universo operacional Path B (145 vivos com cobertura completa 2021–2022; survivorship declarado).
- Em cada último pregão do mês `t`, para cada ativo com preço em `t` e nos quatro horizontes:
  - `mom_h = P(t)/P(ref_h) − 1` com `ref_h` = último preço ≤ `t − h` meses (`h ∈ {3,6,9,12}`).
  - percentil cross-sectional de `mom_h` entre os elegíveis daquele `h`.
  - **score** = média igual dos quatro percentis.
- Só entram no ranking ativos com os **quatro** horizontes observados.
- Carteira: **+100% Top20 EW**, **−30% Bottom10 EW**, **+30% CDI**.
- CDI +30% = alocação da parcela curta — **não** é borrow/locate.
- Execução: sinal `t` → PnL a partir de `t+1`; custo 20 bps/ordem.
- **1 mês excluído** do combo (churn / instabilidade — lab A27/E41).

## Pseudocódigo (narração)

```text
para cada mês t (último pregão):
  para cada horizonte h em {3,6,9,12}:
    mom_h[i] ← retorno de calendário h meses
    pct_h[i] ← percentil de mom_h entre elegíveis de h
  elegíveis ← interseção dos que têm mom nos 4 horizontes
  score[i] ← média(pct_3, pct_6, pct_9, pct_12)
  Top20 ← 20 maiores score; Bottom10 ← 10 menores
  pesos_alvo: +1/20 nos Top20; −0,03 nos Bottom10; CDI +0,30
pesos_executados(d) ← pesos_alvo(d−1)
retorno_liquido ← long + contrib_short + 0,30×cdi − custo_20bps
```

## Números (stdout E48, lab)

| Métrica | Valor |
|---|---|
| Líquido / Sharpe / MaxDD | +873% / 1,31 / −44,5% |
| Rebalances / ordens | 109 / 2.101 |
| Turnover / custo | 89,38x / 17,88% |
| Overlap Top20 vs E45 (365d) | 71,2% |

## Série no repo

`dados/estrategia_propria_diario.csv` — retorno líquido diário exportado do lab E48.

## Limites

Não investível sem borrow real. Path B ≠ painel pontual sem mortos. Combinação ≠ quatro samples independentes (horizontes correlacionados). Comparativo com v2/DM alinha calendário, não o universo.
