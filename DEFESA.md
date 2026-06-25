# Defesa e Críticas — Sistema de Quant Trading (Rotação)

Três blocos: (A) as 5 perguntas do comitê com a resposta-modelo; (B) o que cada grande
estudioso criticaria e a lacuna que isso expõe; (C) perguntas sobre os gráficos.

---

## BLOCO A — As 5 perguntas do chefe e como responder

### 1. "Por que momentum deveria funcionar? Qual a razão econômica?"
Momentum NÃO depende de gap de informação (isso é HFT; info pública é precificada em minutos).
Ele vive na escala de MESES, por três razões:
- **Subreação em magnitude:** o preço reage à notícia, mas de menos, e ajusta devagar conforme as crenças se atualizam (post-earnings drift).
- **Fluxo institucional lento:** fundos grandes montam posição em semanas → pressão persistente.
- **Possível prêmio de risco:** momentum quebra forte nas reversões — não é almoço grátis.
É o efeito mais documentado das finanças (séculos, 100+ mercados). Eu o exploro sem alegar saber a causa definitiva.

### 2. "Só 3 ativos. Como defende que é significativo e não sorte?"
Não afirmo certeza estatística com 3 ativos — a breadth é baixa e sou honesto. A confiança vem
de FORA da amostra (momentum comprovado em centenas de mercados) e da REDUÇÃO DE RISCO
(drawdown −79% → −26%), que é estrutural. Para cravar o retorno, precisaria de universo maior.

### 3. "Por que o Sharpe da estratégia (1,09) ≠ segurar a PRIO (0,91)?"
A estratégia não muda as ações — muda QUANDO e QUANTO fico exposto. Rotaciona para o mais forte
(evita o pior) e corta o tamanho quando a vol dispara (escapa dos crashes). Capturo a alta, evito
os tombos → mais retorno por unidade de risco.

### 4. "Não é robusta só porque a PRIO entrou em 2015 e foi um foguete?"
Em parte sim — o universo melhorou com a PRIO. Mas a habilidade aparece no timing: concentrou na
PRIO nos anos fortes E saiu para a ITUB quando ela murchou (2025). Para separar 100% mérito de
sorte, precisaria de mais ativos e história. Não alego que o número recente é puro mérito.

### 5. "Isso é só 'comprar o que sobe'. Faço no Excel. Onde está o valor?"
O sinal é simples de propósito (simples sobrevive). O valor está no vol targeting + média de
parâmetros (corta drawdown −81% → −26%) e na disciplina sistemática (tira a emoção). Comprar o líder
você faz no Excel; o controle de risco e a validação honesta são o produto.

> Padrão de toda resposta forte: CONCEDE a fraqueza primeiro, depois redireciona para o que é sólido.

---

## BLOCO B — O que cada estudioso criticaria (e a lacuna)

### Marcos López de Prado — backtest overfitting / Deflated Sharpe Ratio
"Quantas estratégias vocês testaram antes de escolher essa? Golden cross, reversão, breakout,
Donchian, momentum 63/126/252, ensemble... O Sharpe está INFLADO pelo número de tentativas.
Apliquem o Sharpe deflacionado."
**Resposta (atenua a crítica):** a análise de sensibilidade mostra que o Sharpe é um PLATÔ
(lookbacks de 189–378d dão 1,05–1,18; janela de vol e vol-alvo quase não mexem) — não um pico
isolado, logo não é um parâmetro "garimpado". E, em vez de escolher um lookback, uso a MÉDIA de
quatro (126/189/252/315). Mesmo assim, CONCEDO que testamos várias famílias de estratégia —
o teste múltiplo existe e o número honesto seria um Sharpe deflacionado.

### Campbell Harvey — multiple testing / t > 3
"t = 2,15 reprova. Num mundo de mineração de dados, o limiar honesto é t > 3, não 2."
**Lacuna:** nossos t-stats (2,15; 2,26) não passam na régua honesta.

### Eugene Fama — Hipótese dos Mercados Eficientes
"Isso não é alfa (habilidade) — é exposição a um FATOR DE RISCO conhecido (momentum). Vocês não
descobriram nada; estão captando um prêmio que já está nos livros."
**Lacuna:** confundir beta de fator com alfa.

### Cliff Asness / AQR — momentum é real, mas...
"Momentum funciona, mas é um fator LOTADO, QUEBRA nas reversões, e em 3 ativos você não tem
diversificação do fator — tem ruído. Precisa de dezenas de mercados."
**Lacuna:** breadth + ignorar o risco de crash do momentum.

### Andrew Lo — Adaptive Markets Hypothesis
"Edges não são permanentes; decaem ao serem explorados. O decaimento da PRIO (1,60 → 0,64) não é
bug, é a regra. A pergunta é quanto tempo de vida resta."
**Lacuna:** assumimos estacionariedade; o edge já está morrendo.

### Nassim Taleb — caudas e aleatoriedade
"Curtose 15 e você comemora −26%? Esse é o pior VISTO, não o pior POSSÍVEL. E escolher a PRIO
sabendo que venceu é viés de sobrevivência."
**Lacuna:** o −26% não é o piso real; seleção condicionada a um vencedor.

### Ernie Chan — pitfalls de backtest (o mais gentil)
"O processo está decente (look-ahead, custo, out-of-sample cuidados). Mas a amostra é pequena —
testem estabilidade do Sharpe em subjanelas e a capacidade (quanto capital cabe)."
**Lacuna:** menor de todas — método ok, problema é escala.

---

## As lacunas em ordem de gravidade
1. **Multiple testing / overfitting** (López de Prado + Harvey) — atenuado por sensibilidade (platô) + média de parâmetros, mas o t-stat (~2,2) ainda reprova no limiar t>3.
2. **Beta de fator ≠ alfa** (Fama) — é exposição a prêmio conhecido, não habilidade.
3. **Risco de crash + caudas** (Asness + Taleb) — momentum quebra; −26% não é o piso.
4. **Decaimento** (Lo) — o edge da PRIO já está morrendo.
5. **Breadth** (todos) — 3 ativos é amostra pobre.

## Postura imune
"Sei que isto é exposição ao fator momentum (não alfa puro), que o Sharpe precisa ser deflacionado
pelos testes, que momentum decai e quebra, e que 3 ativos é amostra pobre. Apresento sabendo de
cada limitação — por isso foco em controle de risco e honestidade, não em prometer um número."

---

## BLOCO C — Perguntas sobre os GRÁFICOS (o que um superior vai perguntar olhando a tela)

### "Esse drawdown é de quem — dos ativos ou da estratégia?"
Da ESTRATÉGIA (a linha verde). É a queda do patrimônio da rotação desde o próprio pico. As linhas
finas coloridas são os ativos (buy&hold), só para comparar — e você vê que a estratégia cai menos
(−26%) que a PRIO sozinha (−79%).

### "Em que janela esse drawdown é medido? Precisa do futuro?"
Janela EXPANSÍVEL (do início até cada dia). O `cummax` guarda o maior pico até ali — uma catraca que
só sobe. NÃO precisa do futuro: hoje você sabe seu patrimônio e seu recorde até hoje. O que só o
futuro dirá é se o tombo já acabou ou se foi o pior de todos.

### "Por que o patrimônio está em escala log?"
Porque mede crescimento em % (taxa), não em reais (tamanho). Em 18 anos de juros compostos, a escala
linear esconderia os primeiros anos; o log faz a mesma variação percentual ocupar a mesma altura.
Linha reta no log = crescimento constante.

### "O que significa a altura das barras de alocação? Ele fica 100% num ativo?"
NÃO. A cor = qual ativo; a altura (0–1) = quanto do capital está nele (vol targeting). Abaixo de 1 =
o resto está em caixa. Em ativo volátil (PRIO, vol 59%) o peso cai para ~34%. Exposição média ~53%.

### "Por que as cores mudam (e às vezes empilham)? Ele opera os 3 ao mesmo tempo?"
Na maioria do tempo fica em UM (o mais forte) — mudança de cor = rotação (vende um, compra outro).
Mas como uso 4 janelas de momentum (126/189/252/315), quando elas DISCORDAM a alocação vira uma
MISTURA (faixas empilhadas) — isso é diversificação extra e foi o que baixou o drawdown para −26%.
Não é o mesmo que segurar os 3 igual (isso é a linha cinza, buy&hold, que a estratégia supera).

### "A linha cinza é o quê?"
O benchmark: buy&hold com 1/3 em cada ativo (o "não fazer nada"). A estratégia (verde) precisa bater
essa linha — e bate, com menos drawdown.

### "Por que tem poucas setas/trocas se é diário?"
Porque o sinal (retorno de 12 meses) é lento — muda devagar. Mede todo dia, mas só TROCA de ativo
quando o líder muda de verdade (~7×/ano). Os ajustes diários de tamanho (vol) são pequenos.
