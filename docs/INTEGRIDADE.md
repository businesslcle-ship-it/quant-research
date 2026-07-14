# Integridade — o que foi auditado (2026-07-14)

Checklist adversária do repo público. Se o gráfico mentir, os números do README
também precisam ser re-cruzados.

## Bugs encontrados e corrigidos

| # | Severidade | Onde | Problema | Correção |
|---|---|---|---|---|
| 1 | **Crítico** | `rotacao_graf.py` | B&H fazia `cumprod` desde o início da série (pré-2008) e só `reindex` em 2008 → começava em ~15× enquanto a v2 em ~1×. No gráfico o B&H “ganhava” sem ter ganhado no período. | Cumprod só na janela de avaliação (base ~1) + `assert` |
| 2 | Médio | CDI hardcoded | 2025 −82 bps vs BCB; 2026 +771 bps (mapa antigo vs YTD). Impacto no Sharpe headline ~0,00 (1,18). | `dados/cdi_bcb_*.csv` + `src/_cdi.py` (diário BCB) |
| 3 | Baixo | `comparativo` / `sinais*` | Cortavam preços em 2008 antes do lookback (padrão E37). Na janela 2016+ o Sharpe não mudava (delta 0), mas a higiene estava errada. | História completa no lookback |
| 5 | Médio | `pct_change` default | Pandas preenchia NaN com `pad` e inventava retorno entre buracos → DM 1,12/+4631% vs 1,13/+4931% sem pad. | `fill_method=None` em todos os scripts; README atualizado |

## O que foi verificado e está íntegro

- `rotacao.py` headline: Sharpe **1,18** / MaxDD **−28%** / +6.740% (2008+, 20 bps, E37, CDI diário BCB).
- `comparativo.py` (2016-06+): v2 **1,56** / −24% / +2411%; B&H **1,17** / −52% / +1539%.
- Dual Momentum apresentado: **1,13** / −64% / +4931%; mensal **1,04** / −65% / +3858%.
- Comparativo, rotacao_graf e DM graf: equity curves começam ~1 (rebase correto; assert no grafico da v2).
- README cruza com esses stdout (pos-auditoria).

**Nota:** os slides/entrega de 2026-07-13 citavam DM **1,12 / +4631%** (pad + CDI anual antigo). Apos a auditoria a fonte de verdade e o codigo regenerado acima.

## Fontes de dados

| Arquivo | Uso |
|---|---|
| `dados/{PRIO3,ITUB3,ABEV3}.csv` | Preços ajustados diários (v2 / comparativo) |
| `dados/base_plana.csv` | Barras 60min + linha `dia` (Dual Momentum) |
| `dados/cdi_bcb_diario.csv` | CDI oficial BCB SGS 12 (caixa da v2) |
| `dados/cdi_bcb_anual.csv` | Resumo anual (DM mensal/60min; 2026 YTD tratado como provisório no mapa) |

## Regra para não repetir

1. Benchmark no gráfico: **mesma janela + base 1**, nunca `cumprod` global + `reindex`.
2. Lookback: **nunca** cortar a história antes de calcular momentum (E37).
3. CDI: preferir série diária BCB; não inventar ano cheio a partir de YTD.
4. Depois de mudar preço/CDI/custo: re-rodar `rotacao.py`, `comparativo.py`, `*_graf.py` e conferir README.
