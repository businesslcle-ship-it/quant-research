# Glossário — Conceitos do Sistema Quant
Cada conceito em 2–3 frases, para entender e explicar.

---

## 1. Dados e preparação

**adjustedClose (preço ajustado)** — Preço corrigido por dividendos e desdobramentos. Usar ele faz o retorno medido ser o "retorno total" do investidor (preço + proventos), não só a variação de cotação.

**Timestamp diário (end-of-day)** — Cada dado é uma "foto" do preço no fechamento de cada pregão. É a granularidade de uma estratégia de swing/posição (segura por meses), não de day-trade; não enxergamos o que acontece dentro do dia.

**Recorte desde 2008** — Janela de análise definida. Pega o ciclo completo incluindo a crise de 2008, o que torna o teste mais honesto (inclui mercados ruins).

**Universo expansível** — Cada ativo entra na estratégia quando passa a existir (a PRIO só a partir de 2015). Nunca se inventa preço antes da existência do ativo — isso seria look-ahead/survivorship.

**Viés de sobrevivência / seleção** — Escolher ativos sabendo que sobreviveram (ou venceram) infla o resultado. Testar tendência numa ação que já se sabe ter feito +5.000% é montar o baralho a favor.

---

## 2. Indicadores e sinais

**Médias móveis (MM50/MM200) — golden cross** — Média curta acima da longa = tendência de alta (compra); abaixo = sai. Simples e clássico, mas dá whipsaw em ativos laterais.

**Momentum / TSMOM (retorno de 12 meses)** — Comprado se o preço de hoje está acima do de um ano atrás. Forma direta e robusta de medir tendência; é a base da rotação.

**Momentum cross-sectional (ranking)** — Em vez de olhar um ativo isolado, compara os ativos entre si e escolhe o mais forte. É o coração da rotação.

**Hurst** — Mede se a série é persistente (>0,5 = tende) ou reverte (<0,5 = mean-reverting). É o "termômetro" que diagnostica se vale a pena seguir tendência.

**KAMA, Connors RSI, MACD, ATR, Kalman, Efficiency Ratio** — Indicadores exóticos explorados no início. Descartados por complexidade ou redundância (ex.: MACD era 0,93 correlacionado com a inclinação da média).

**Reversão à média (z-score) e Donchian (breakout)** — Famílias alternativas testadas. Não funcionaram nesses ativos — a confirmação de que a tendência só serve onde há tendência.

---

## 3. Estrutura da estratégia

**Trend following** — Seguir a direção dominante do preço, em vez de prever topos/fundos.

**Sinais de entrada/saída (gatilhos)** — A regra matemática que liga/desliga a posição. No momentum: liga quando o retorno de 12m vira positivo, desliga quando vira negativo.

**Posição binária vs contínua** — Binária = 100% comprado ou 100% fora (golden cross). Contínua = o tamanho varia (vol targeting), respirando dia a dia.

**Volatility targeting** — Dimensiona a posição pelo inverso da volatilidade (vol-alvo ÷ vol-atual). Quando o ativo fica violento, reduz exposição automaticamente — foi o que cortou o drawdown da PRIO de −79% para −24%.

**Roteador de regime ("médico")** — Diagnostica cada ativo (Hurst) e aplica o tratamento certo: momentum onde tende, segurar onde não. A inteligência de saber quando NÃO operar.

**Rotação** — Migra o capital para o ativo mais forte do momento, trocando quando o ranking vira. Usa todos os ativos ativamente e gerencia o decaimento sozinha.

**Long-only vs long-short vs pairs** — Só comprado; comprado-e-vendido; ou valor relativo (spread entre dois). O long-short falhou aqui porque a perna vendida sangra num mercado que sobe.

**Buy & hold** — Comprar e segurar, sempre 100% investido. O benchmark do "não fazer nada" que toda estratégia precisa bater.

---

## 4. Mecânica do backtest

**Backtest vetorizado** — Calcula posição × retorno em toda a série de uma vez, sem loop. Rápido e limpo — eficiência vem da vetorização, não de poucas linhas.

**`pos.shift(1)` / look-ahead bias** — Defasar a posição em 1 dia: a decisão de hoje só rende amanhã. Garante que nunca se usa informação do futuro (causalidade) — a diferença entre backtest honesto e fantasia.

**Custo de transação (tabela Bovespa, 90% desconto)** — ~0,05% por ordem, descontado a cada troca de posição. Como o giro é baixo, o impacto é desprezível.

**Curva de patrimônio (cumprod)** — Multiplica os retornos diários em sequência (juros compostos). Mostra R$1 inicial crescendo ao longo do tempo.

**Período de aquecimento** — Os primeiros dias em que o indicador ainda não existe (ex.: MM200 precisa de 200 dias). A estratégia só opera depois disso.

---

## 5. Métricas de risco e performance

**Sharpe** — Retorno médio ÷ volatilidade total, anualizado. Quanto você ganha por unidade de "susto"; acima de 1 é bom.

**Sortino** — Igual ao Sharpe, mas só conta a volatilidade das quedas (não pune a alta). Maior que o Sharpe indica boa assimetria (mais ganhos que sustos ruins).

**Max Drawdown** — A pior queda do pico ao fundo. Base = o maior valor já atingido pela estratégia (topo histórico, janela expansível); mede a dor máxima.

**Duração do drawdown** — Quanto tempo a estratégia ficou abaixo do pico anterior. Drawdown não é só profundidade — é quanto tempo dói (ABEV ficou 8 anos no buraco).

**CAGR, volatilidade, win rate, payoff, expectancy, exposição** — Métricas auxiliares: crescimento anual composto, risco, % de acertos, ganho médio/perda média, ganho esperado por trade e % do tempo investido.

---

## 6. Validação estatística

**In-sample vs out-of-sample / walk-forward** — Testar a estratégia num período que ela não "ajudou a criar". Como estudar para uma prova com questões novas — o teste real de que aprendeu, não decorou.

**t-statistic / significância** — Mede se o resultado é edge real ou sorte. Com poucos trades (n=9), até um Sharpe alto pode ser frágil.

**Breadth + Lei Fundamental (IR = IC × √apostas)** — A qualidade de um fundo vem mais de muitas apostas independentes do que de um sinal genial. Poucos ativos = baixa breadth = Sharpe frágil.

**Information Coefficient (IC)** — Correlação entre o sinal de hoje e o retorno futuro. Mede a "habilidade por aposta".

**Overfitting / curve-fitting** — Ajustar parâmetros até o passado ficar bonito. A armadilha-mãe: gera backtest lindo que falha ao vivo.

**Ortogonalidade (Spearman, mutual information, correlação)** — O quanto dois sinais são independentes. Sinais ortogonais somam valor; correlacionados (ex.: 0,93) só repetem a mesma aposta e atrapalham.

**Alpha decay** — O edge de uma estratégia decai com o tempo (crowding, maturação). A PRIO caiu de Sharpe 1,60 → 0,64 conforme amadureceu e o mercado a "descobriu".

**Análise de sensibilidade** — Girar os parâmetros (lookback, janela de vol) e ver se o resultado aguenta. Se só o valor "ótimo" presta, é overfitting; se funciona numa faixa ampla (platô), é robusto. O nosso é platô (lookbacks 189–378d dão Sharpe ~1,1) → passou.

**Média de parâmetros** — Em vez de escolher UM valor (ex.: lookback 252), usar vários ao mesmo tempo (126/189/252/315) e fazer a média. Remove a escolha arbitrária, é mais estável, e mata a crítica de data-snooping. No nosso caso subiu o Sharpe (1,05→1,09) e cortou o drawdown (−43%→−26%) pela diversificação dos prazos.

---

## 7. Perfil quantitativo dos ativos

**CAGR / vol / Sharpe por ativo** — Retorno anual, risco e eficiência de cada um. PRIO: alto retorno e alto risco; ITUB: equilibrado; ABEV: fraca no período.

**Hurst por ativo** — PRIO 0,53 (tende), ITUB/ABEV ~0,49 (laterais). A assinatura quantitativa de por que a tendência só funciona na PRIO.

**Skewness e curtose** — Assimetria e "caudas gordas". PRIO tem skew positivo (saltos de alta, bom p/ trend) e curtose 15 (eventos extremos).

**Correlação entre ativos (0,22–0,45)** — Baixa correlação entre os três. É o que permite a rotação reduzir risco abaixo do de qualquer ativo isolado.

---

## 8. Checklist do Ernie Chan

**As 5 perguntas** — Supera o benchmark? Sharpe alto o suficiente (>1)? Drawdown pequeno e curto? Tem viés de sobrevivência? Perde fôlego nos anos recentes? Um backtest sério responde todas, com honestidade.

---

## 9. Como os grandes fundos fazem

**Pods multi-manager (Citadel/Millennium/Point72)** — São coleções de dezenas de times rodando estratégias descorrelacionadas. A força vem da diversificação de apostas, não de um sinal mágico.

**Gerir o decaimento de alfa** — Aposentam sinais mortos e atualizam em janelas móveis, em vez de over-tunar um sinal moribundo. A rotação faz isso sozinha (migra do ativo morto para o vivo).

**Simplicidade no sinal, rigor no risco** — Mantêm o sinal simples (momentum) e põem a sofisticação no controle de risco e na diversificação — exatamente onde a complexidade paga.

---

## 10. Gráfico e meta-conceitos

**Escala log** — Mede crescimento em % (taxa), não em reais (tamanho). O único jeito honesto de ver juros compostos ao longo de muitos anos sem o passado sumir.

**Drawdown (underwater) chart** — Visualiza a queda abaixo do pico ao longo do tempo. Mostra a "dor" que o investidor sentiria.

**Gráfico de alocação** — Mostra a rotação: a cor = qual ativo está sendo operado; a altura (0–1) = quanto do capital (vol targeting).

**Linhas ≠ eficiência ≠ resultado** — Código curto não melhora o resultado (a matemática é a mesma) nem a velocidade (isso é vetorização). Só muda a legibilidade.

**Estratégia simples vs código simples** — A simplicidade que importa é a da lógica (menos parâmetros = menos overfitting = mais robusto), não a contagem de linhas.

**Dependência de regime** — Cada estratégia funciona num tipo de mercado. A inteligência é casar a ferramenta com o comportamento do ativo (e segurar quando nenhuma serve).
