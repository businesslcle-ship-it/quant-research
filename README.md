# Quant Momentum — Rotacao v2

Estrategia sistematica de momentum cross-sectional com **volatility targeting** e rebalance semanal, aplicada a ITUB3, PRIO3 e ABEV3 (desde 2008). A cada dia o sistema mede o momentum dos tres ativos em quatro janelas (6, 9, 12 e 15 meses), aloca no mais forte, **dimensiona a posicao pela volatilidade do portfolio** (mira 20% ao ano) e congela os pesos por uma semana. O capital nao investido rende 100% do CDI. Long-only, sem alavancagem, liquido de custos, sem look-ahead (`shift(1)`).

A logica tem tres camadas independentes: **direcao** (em quem — a media dos lideres das quatro janelas), **tamanho** (quanto — o vol target, uma vez, no nivel do portfolio) e **ritmo** (quando — rebalance semanal).

## Resultados (janela dos 3 ativos, regua diaria, liquido de 20 bps)

| Estrategia | Sharpe | Vol | Max Drawdown | Retorno |
|---|---|---|---|---|
| **Rotacao v2 (freio)** | **1,56** | 22% | **-24%** | +2.403% |
| v2 sem freio | 1,09 | 50% | -79% | +6.207% |
| Dual Momentum (livro, baseline) | 1,03 | 50% | -79% | +4.727% |
| Buy & Hold 1/3 | 1,17 | 27% | -52% | +1.539% |

![Comparativo](comparativo.png)

**Leitura:** o vol target ("o freio") e o que separa a v2 do resto. Sem ele, a rotacao converge para o Dual Momentum classico (mesma vol de 50%, mesmo drawdown de -79%) — ou seja, o diferencial da v2 nao esta no sinal de direcao, e sim no **controle de risco**: terceiro do risco, metade do drawdown, e o melhor retorno ajustado a risco (Sharpe) do grupo. O Dual Momentum entrega mais retorno absoluto (concentra 100% no lider), mas ao custo de um drawdown de -79%.

![Rotacao v2](rotacao.png)

## Sinais das duas estrategias

As alocacoes da Rotacao v2 (pesos fracionarios + caixa) e do Dual Momentum (tudo-ou-nada) no mesmo eixo do tempo — `python3 sinais_comparados.py` gera o grafico e exporta os CSVs de sinais:

![Sinais comparados](sinais_comparados.png)

## Dual Momentum nos 60 minutos — dois relogios

O `dual_momentum.py` aplica o nucleo do livro DIRETO nas barras de 60min, com duas melhorias de engenharia medidas em laboratorio: **histerese de 5%** na troca de lider (a fronteira de custo tem plato em 5-12%, nao pico) e **dois relogios** — a perna relativa decide a cada barra, a perna absoluta so pode mudar de estado na 1a barra do dia (o liga-desliga horario do caixa era ~80% do custo: 625 trocas contra 100).

| Versao | Sharpe | MaxDD (regua) | Retorno | Custo/ano |
|---|---|---|---|---|
| **DM 60min dois relogios** | **1,11** | **-49% (horaria)** | +3.620% | 7,7% |
| Baseline fiel mensal (`dual_momentum_mensal.py`) | 1,04 | -65% (mensal; -79% diaria) | +3.853% | ~0 |

![DM vs benchmark](dm_vs_benchmark.png)

**Leitura honesta:** a versao 60min usa o timestamp real (cada troca acontece num preco que existiu na tela), segura o drawdown na regua mais dura de todas e paga 7,7%/ano de custo por essa reatividade. Descontada a selecao de variantes testadas no laboratorio (~0,12 de barreira), o Sharpe liquido EMPATA com o baseline mensal — a escolha pela versao 60min se sustenta na regua de risco e no realismo de execucao, nao num Sharpe "maior". O baseline permanece no repo como ancora de comparacao. Contra o B&H 1/3 (Sharpe 1,13): o DM compra retorno por concentracao; eficiencia e papel do vol target da v2.

## Como rodar

```bash
pip install -r requirements.txt
python3 rotacao.py          # metricas da v2
python3 rotacao_graf.py     # v2 + grafico (3 paineis)
python3 dual_momentum.py            # DM nos 60min (dois relogios) — o apresentado
python3 dual_momentum_mensal.py     # baseline fiel ao livro (mensal)
python3 comparativo.py      # compara as 4 estrategias + grafico
python3 sinais.py           # exporta a alocacao diaria por ativo
```
Requer a pasta `dados/` com CSVs no formato `date,open,high,low,close,adjustedClose,volume`.

## Estrutura

| Arquivo | Conteudo |
|---|---|
| `rotacao.py` | Estrategia v2 (nucleo legivel, comentado) |
| `rotacao_graf.py` | v2 + grafico de 3 paineis |
| `dual_momentum.py` | Dual Momentum nos 60min — dois relogios (o apresentado) |
| `dual_momentum_mensal.py` | Baseline fiel ao livro, mensal (ancora de comparacao) |
| `dual_momentum_graf.py` | DM 60min vs baseline mensal vs B&H 1/3 vs CDI (grafico) |
| `comparativo.py` | Comparativo das 4 estrategias + grafico |
| `sinais.py` | Exporta a alocacao diaria por ativo |
| `Pseudocodigo_v2.docx` | Pseudocodigo da v2 (linha a linha) |
| `Pseudocodigo_DualMomentum.docx` | Pseudocodigo do Dual Momentum (linha a linha) |
| `dados/` | Precos ajustados dos 3 ativos |

Stack: Python, pandas, numpy, matplotlib.
