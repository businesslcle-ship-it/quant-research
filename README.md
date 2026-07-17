# Quant Research

> **Path B / estratégia-própria atualizada:** abra [`ESTRATEGIA_PROPRIA.md`](ESTRATEGIA_PROPRIA.md)  
> (se você só olhar `src/`, verá o código dos **3 ativos** — a evidência Path B está em `docs/` + `dados/` + `src/estrategia_propria_amostra.py`).

Rotacao Momentum v2 — estrategia sistematica de momentum cross-sectional com **volatility targeting** e rebalance semanal, aplicada a ITUB3, PRIO3 e ABEV3. A cada dia o sistema mede o momentum dos tres ativos em quatro janelas (6, 9, 12 e 15 meses), aloca no mais forte, **dimensiona a posicao pela volatilidade do portfolio** (mira 20% ao ano) e congela os pesos por uma semana. O capital nao investido rende 100% do CDI. Long-only, sem alavancagem, liquido de **20 bps por ordem**, sem look-ahead (`shift(1)`).

A logica tem tres camadas independentes: **direcao** (em quem — a media dos lideres das quatro janelas), **tamanho** (quanto — o vol target, uma vez, no nivel do portfolio) e **ritmo** (quando — rebalance semanal).

---

## Norte de pesquisa (Path B / mentor) — leia isto antes do placar

Com o mentor (**Guilherme**), o objetivo da linha Path B **nao** e o Sharpe maximo de carteira.

Objetivo: **sinal/alfa que ML possa explorar** — muitas movimentacoes, base so **minimamente boa**, interesse do sinal.  
**Metalabeling** sera feito **junto com o Guilherme** — este repo **nao** treina o meta.

Linha completa + motivos: **[docs/LINHA_RACIOCINIO.md](docs/LINHA_RACIOCINIO.md)**  
Auditoria do que o repo prova: **[docs/AUDITORIA_EVIDENCIA.md](docs/AUDITORIA_EVIDENCIA.md)**

**Base publica atual (`estratégia-própria` no grafico):** lab **E54** — momentum **1 mes**, rebalance **semanal**, Path B 145, +100% Top20 / −30% Bottom10 / +30% CDI, 20 bps.  
Serie: `dados/estrategia_propria_diario.csv`. Pseudocodigo: [docs/pseudocodigo/base_amostra_e54.md](docs/pseudocodigo/base_amostra_e54.md).

**Por que 1m semanal (resumo):** na paisagem E49–E53 o **1m** gera mais filme que 2m/3m; a frequencia semanal (E54) multiplica decisoes vs mensal (E53). Combo E48 foi desvio de portfolio — nao e a base.

**Schema de labels (E55, sem treino):** unidade = ativo × sinal × lado; y = perna > CDI ate o proximo sinal. N=**15 522**, y≈50%. Resumos: `dados/e55_schema_*.csv`. Docs: [schema_labels_e55.md](docs/pseudocodigo/schema_labels_e55.md).

### Comparativo de filme (Path B) — ordens importam mais que Sharpe*

| Exp | Horizonte | Freq | Ordens | Rebalances | Custo | Ret liq* | Sharpe* |
|---|---|---|---:|---:|---:|---:|---:|
| E53 | 1m | mensal | 5 381 | 120 | 50% | +458% | 0,96 |
| **E54** | **1m** | **semanal** | **12 480** | **519** | **107%** | **+152%** | **0,56** |
| E52 | 2m | mensal | 4 017 | 119 | 35% | +755% | 1,17 |
| E49 | 3m | mensal | 3 354 | 118 | 29% | +471% | 0,97 |
| E50 | 6m | mensal | 2 281 | 115 | 20% | +967% | 1,28 |
| E51 | 12m | mensal | 1 599 | 109 | 14% | +730% | 1,19 |

\*Retorno/Sharpe = **secundarios** (norte = amostra). CSV: `dados/comparativo_horizontes_filme.csv`.

---

## Resultados — linha 3 ativos (mesma regua diaria, 20 bps)

**Lab / `rotacao.py` (amostra desde 2008, warm-up honesto — E37):** Sharpe **1,18** | MaxDD **−28%** | retorno +6.740%.  
(Antes do E37 o código cortava a história em 2008 e reportava 1,30/−25% com 2008 inteiro em CDI por artefato. PRIO só entra em meados de 2015; ITUB em 2009. CDI do caixa: série diária BCB.)

**Comparativo (janela calendário ~2016-06+, `comparativo.py`, ativas @20 bps):**

| Estrategia | Universo | Sharpe* | Vol | Max Drawdown | Retorno* |
|---|---|---|---|---|---|
| **Rotacao v2 (freio)** | 3 ativos | **1,56** | 22% | **-24%** | +2.411% |
| v2 sem freio | 3 ativos | 1,09 | 50% | -79% | +6.207% |
| Dual Momentum mensal (livro, no comparativo) | 3 ativos | 1,03 | 50% | -79% | +4.731% |
| Buy & Hold 1/3 | 3 ativos | 1,17 | 27% | -52% | +1.539% |
| **estratégia-própria (= E54 amostra)** | Path B 145 | **0,56** | 21% | **−58%** | **+152%** |

\*Na propria, Sharpe/retorno sao **veiculo de amostra**, nao ranking de vitoria. Numeros do `comparativo.py` na janela alinhada (~2016-06+).

![Comparativo](figures/comparativo.png)

**Leitura (linha 3 ativos):** o vol target ("o freio") e o que separa a v2 do resto. Sem ele, a rotacao converge para o Dual Momentum classico. **Nao confundir** o 1,56 (janela 2016+) com o 1,18 (amostra 2008+ apos E37). **Nao confundir** v2 com a propria Path B (universos distintos).

![Rotacao v2](figures/rotacao.png)

## Sinais das duas estrategias (3 ativos)

As alocacoes da Rotacao v2 e do Dual Momentum baseline mensal — `python3 src/sinais_comparados.py`:

![Sinais comparados](figures/sinais_comparados.png)

## Dual Momentum (apresentado)

O `dual_momentum.py` e **o** Dual Momentum deste repo: nucleo do livro INTACTO (momentum de **12 meses por calendario** + barreira do CDI dos mesmos 12 meses), avaliado a cada **barra de 60min**, com UMA concessao — **histerese de 5%** na troca de lider.

| Versao | Sharpe | MaxDD (regua) | Retorno | Custo/ano | Sinais / execucao |
|---|---|---|---|---|---|
| **Dual Momentum** (`dual_momentum.py`, barras 60min) | **1,13** | -64% (horaria) | **+4.931%** | **3,6%** | **147 rebalances em 9 anos; 167 ordens** |
| Dual Momentum mensal (`dual_momentum_mensal.py`, baseline) | 1,04 | -65% (mensal; -79% diaria) | +3.858% | 6,0% total (30 ordens) | 18 meses com mudanca de peso; 30 ordens |

![DM vs benchmark](figures/dm_vs_benchmark.png)

## Pseudocodigos e docs

- [Rotacao v2](docs/pseudocodigo/rotacao_v2.md) · [Dual Momentum](docs/pseudocodigo/dual_momentum.md)
- [Base amostra E54](docs/pseudocodigo/base_amostra_e54.md) · [Schema labels E55](docs/pseudocodigo/schema_labels_e55.md)
- [Linha de raciocinio](docs/LINHA_RACIOCINIO.md) · [Auditoria](docs/AUDITORIA_EVIDENCIA.md)
- Indice: [docs/pseudocodigo/](docs/pseudocodigo/)

## Como rodar

```bash
pip install -r requirements.txt
python3 rotacao.py
python3 dual_momentum.py
python3 dual_momentum_mensal.py
python3 comparativo.py
python3 estrategia_propria_amostra.py   # imprime E54 + tabela filme + schema E55
python3 rotacao_graf.py
python3 src/sinais_comparados.py
```

Requer a pasta `dados/` (CSVs dos 3 ativos + `base_plana.csv` + serie propria + tabelas Path B).

## Estrutura

```
├── ESTRATEGIA_PROPRIA.md              # ← COMECE AQUI (Path B / E54)
├── README.md
├── docs/
│   ├── LINHA_RACIOCINIO.md
│   ├── AUDITORIA_EVIDENCIA.md
│   └── pseudocodigo/
├── dados/
│   ├── estrategia_propria_diario.csv      # E54
│   ├── comparativo_horizontes_filme.csv
│   ├── e55_schema_resumo.csv
│   └── e55_schema_particoes.csv
├── src/
│   ├── estrategia_propria_amostra.py      # imprime evidência Path B
│   ├── rotacao.py / dual_momentum.py …  # linha 3 ativos
│   └── comparativo.py
└── figures/
```

Stack: Python, pandas, numpy, matplotlib.
