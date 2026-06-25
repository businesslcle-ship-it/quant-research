# Roteiro de Apresentação — Sistema de Quant Trading (Rotação Dinâmica)

Sistema final: **rotação cross-sectional + volatility targeting + média de parâmetros** em ITUB3, PRIO3, ABEV3 (desde 2008).
Código central: `rotacao_graf.py` (estratégia + gráfico) | Núcleo: `rotacao.py` (16 linhas).
Apoio: `CONCEITOS.md` (glossário) · `DEFESA.md` (perguntas + críticas dos estudiosos).

---

## PARTE 0 — COMO RODAR AO VIVO

1. Abra o **Terminal** do Mac.
2. Entre na pasta:
   ```
   cd "/Users/laurochristakou/Desktop/pipeline crédito"
   ```
3. Rode:
   ```
   python3 rotacao_graf.py
   ```
4. Acontece: imprime `Sharpe=1.09 Sortino=1.58 MaxDD=-26% ret=3257%` e abre o gráfico de 3 painéis (patrimônio / drawdown / alocação). Também salva `rotacao.png`.

> REGRA DE OURO: o código é um ARQUIVO; o terminal só o EXECUTA com `python3 rotacao_graf.py`. Nunca cole Python direto no terminal (dá `parse error`).
> Plano B: se a janela não abrir, mostre o `rotacao.png` já salvo.

---

## PARTE 1 — A IDEIA EM UMA FRASE

> "É um sistema que, todo dia, ranqueia os três ativos pelo retorno dos últimos meses, aloca o capital no mais forte e dimensiona a posição pela volatilidade — trocando de ativo quando outro assume a liderança. Para não depender de um único prazo, ele faz isso com quatro janelas de momentum ao mesmo tempo. Resultado: Sharpe 1,09 desde 2008, com drawdown de −26% (vs −79% de segurar a PRIO)."

---

## PARTE 2 — A JORNADA (por que cheguei na rotação)

Não comecei na rotação — cheguei nela testando e descartando. Esse caminho é parte da defesa:

1. **Golden cross (MM50/200)** — a tendência mais clássica. Só funcionou na PRIO; nos laterais (ITUB/ABEV) deu whipsaw e perdeu para simplesmente segurar.
2. **Diagnóstico (Hurst)** — descobri *por quê*: só a PRIO tem tendência (Hurst 0,53); ITUB/ABEV são laterais (~0,49). Levar trend a elas é "surfar num lago sem ondas".
3. **Volatility targeting** — dimensionar pela vol cortou o drawdown da PRIO de −79% para −24% e subiu o Sharpe.
4. **Rotação dinâmica + média de parâmetros (a final)** — ranquear os três e ficar no mais forte, com 4 janelas de momentum ao mesmo tempo. Resolveu o "só PRIO" e superou tudo.

Mensagem: "Testei o simples, entendi por que falha, e evoluí com base nos dados — não em achismo."

---

## PARTE 3 — A ESTRATÉGIA FINAL: COMO A ROTAÇÃO FUNCIONA

**O número que ela lê:** o retorno passado de cada ativo. Compara os três e fica no MAIOR (o mais forte).

**Placar em datas reais (retorno 12m, e o escolhido):**
| Data | PRIO3 | ITUB3 | ABEV3 | → Escolhe |
|---|---|---|---|---|
| 2012 | — | −7% | **+47%** | ABEV3 |
| 2017 | **+143%** | +51% | 0% | PRIO3 |
| 2021 | **+169%** | +13% | +35% | PRIO3 |
| 2024 | **+27%** | +25% | −22% | PRIO3 |
| 2025 | +3% | **+43%** | +28% | ITUB3 |

**Como troca de ativo:** quando o ranking vira (outro ultrapassa no retorno passado). Ex.: em 2025 o momentum da PRIO secou (+3%) e a ITUB subiu (+43%) → migra para ITUB.

**A média de parâmetros (por que não fica sempre num ativo só):** em vez de escolher UMA janela de momentum (ex.: 252 dias), rodo QUATRO ao mesmo tempo (126/189/252/315) e faço a média. Na maioria dos dias as 4 concordam → fica num ativo. Quando discordam (a de 6m diz ITUB, a de 12m diz PRIO) → a alocação vira uma MISTURA. Essa mistura é diversificação extra — foi o que cortou o drawdown de −43% para −26%. (No gráfico, aparece como faixas de cor empilhadas.)

**Quanto aloca:** NÃO é sempre 100%. O tamanho = `vol-alvo (20%) ÷ vol-atual`, limitado a 1 (sem alavancagem). Ativo volátil (PRIO, vol 59%) → posição menor, resto em caixa.

**Por que uma regra única em ativos que sozinhos não funcionam é inteligente:** a inteligência está na SELEÇÃO (estar sempre no líder), não no ativo. Regra agnóstica = sem overfitting. Funciona porque os três são pouco correlacionados (0,22–0,45) e se revezam.

---

## PARTE 4 — O CÓDIGO (rotacao.py), linha a linha

| Trecho | O que faz | Premissa |
|---|---|---|
| `C, A, N = 0.0005, 0.20, 252` | custo/ordem (tabela Bovespa, 90% desc.), vol-alvo 20%, dias/ano | constantes num lugar só |
| `LOOKBACKS = [126,189,252,315]` | as 4 janelas de momentum | média de parâmetros — não escolho uma |
| `px = pd.concat({...}).loc["2008":]` | lê o `adjustedClose` dos 3, desde 2008 | preço ajustado = retorno total; universo expansível (PRIO entra em 2015) |
| `def pesos(L):` | calcula a alocação para UM lookback | ranqueia, pega o líder, dimensiona pela vol |
| dentro: `rank.eq(rank.max())` | 1 no mais forte (ignora NaN) | seleção do líder |
| dentro: `(A/vol).clip(0,1)` | tamanho = vol-alvo/vol, sem alavancagem | vol targeting |
| `w = sum(pesos(L) for L in LOOKBACKS)/4` | MÉDIA dos pesos das 4 janelas | diversifica o prazo do momentum |
| `r = (w.shift(1)*ret).sum() - w.diff().abs().sum()*C` | retorno líquido | `shift(1)` = SEM look-ahead; custo na troca |

---

## PARTE 5 — RESULTADOS

### Comparativo das estratégias (desde 2008, portfólio 1/3 onde aplicável)
| Estratégia | Sharpe | Sortino | MaxDD | Retorno |
|---|---|---|---|---|
| Golden cross | 0,82 | 1,05 | −45% | +1.012% |
| Roteador estático | 0,76 | 1,06 | −46% | +1.149% |
| **Rotação (FINAL, 4 lookbacks)** | **1,09** | **1,58** | **−26%** | **+3.257%** |
| Buy & Hold 1/3 | 0,83 | 1,15 | −52% | +3.017% |
Só a rotação supera o buy&hold em TODOS os eixos. As outras duas foram etapas.

### Comparativo dos ATIVOS vs a estratégia (período comum 2015–2026)
| | CAGR | Vol | Sharpe | Sortino | MaxDD |
|---|---|---|---|---|---|
| PRIO3 | 44% | 59% | 0,91 | 1,33 | −79% |
| ITUB3 | 18% | 27% | 0,75 | 1,09 | −37% |
| ABEV3 | 3% | 26% | 0,23 | 0,33 | −52% |
| **ROTAÇÃO** | — | **~21%** | **1,20** | **1,73** | **−24%** |
A rotação tem MENOS vol e MENOS drawdown que qualquer ativo isolado, e o maior Sharpe. O todo é melhor que a melhor das partes.

---

## PARTE 6 — O GRÁFICO (3 painéis)

1. **Patrimônio (log):** verde (rotação) cresce mais reto que cinza (buy&hold). Escala log porque mede crescimento em % — o jeito honesto de ver juros compostos ao longo de 18 anos.
2. **Drawdown:** vermelho (estratégia) é mais raso que as linhas dos ativos (PRIO mergulha a −79%; a estratégia, só −26%). Base = pico anterior da própria estratégia; mede a queda desde o melhor momento já atingido (janela expansível, sem usar o futuro).
3. **Alocação:** cor = qual ativo; altura (0–1) = quanto do capital (vol targeting). Faixas empilhadas = as 4 janelas discordando (mistura/diversificação); cor única = as 4 concordando.

---

## PARTE 7 — VALIDAÇÃO (checklist de Ernie Chan)

1. **Supera benchmark?** ✅ Rotação 1,09 vs Buy&Hold 0,83; drawdown −26% vs −52%.
2. **Sharpe alto?** 1,09 desde 2008 (1,20 no período 2015+). Acima de 1.
3. **Drawdown curto?** −26% de profundidade (vol targeting + média de lookbacks). Duração ainda é ponto a monitorar.
4. **Viés de sobrevivência?** ⚠️ Sim — os 3 foram escolhidos sabendo que sobreviveram; a PRIO é vencedora conhecida. Conceder isso.
5. **Perde fôlego?** Walk-forward: treino 0,95 → prova 1,21 → desde 2021 0,96. Não desaba — diversifica o edge entre os 3 (quando PRIO secou, migrou para ITUB). Parte da força recente é o universo melhorar com a PRIO em 2015 — conceder.

**Look-ahead:** blindado pelo `shift(1)` (o "lag" do Chan: sinal usa só dados até o fechamento anterior).

**Análise de sensibilidade (Chan):** variei os parâmetros e o Sharpe é um PLATÔ (lookbacks de 189–378d dão 1,05–1,18; janela de vol e vol-alvo quase não mexem). Não há parâmetro mágico → não é data-snooping. E, em vez de escolher um lookback, uso a MÉDIA de quatro — o que mata a crítica de overfitting.

---

## PARTE 8 — AS CRÍTICAS DOS ESTUDIOSOS (diga as rachaduras antes do chefe)

- **López de Prado (Deflated Sharpe):** testamos muitas estratégias → risco de Sharpe inflado. RESPOSTA: a análise de sensibilidade mostra platô (não pico), e uso média de parâmetros (não escolho um). Atenuada, mas ainda concedo que o teste múltiplo existe.
- **Campbell Harvey (t > 3):** t-stats (~2,2) reprovam no limiar honesto contra mineração de dados. Lacuna real.
- **Fama (EMH):** isto é exposição ao FATOR momentum (beta), não alfa puro.
- **Asness/AQR:** momentum é real, mas LOTADO, QUEBRA nas reversões, e 3 ativos é pouca diversificação do fator.
- **Andrew Lo (Adaptive Markets):** edges decaem — o da PRIO já está morrendo.
- **Taleb:** −26% é o pior VISTO, não o pior POSSÍVEL (curtose 15); + viés de sobrevivência.
- **Ernie Chan:** método ok (look-ahead, custo, out-of-sample, sensibilidade); problema é amostra pequena e capacidade.

Postura imune: "Sei que é beta de fator (não alfa), que existe risco de teste múltiplo (atenuado por sensibilidade + média de parâmetros), que momentum decai e quebra, e que 3 ativos é amostra pobre. Apresento sabendo de cada limitação — por isso foco em risco e honestidade."

---

## PARTE 9 — PREMISSAS E ESCLARECIMENTOS-CHAVE

- **adjustedClose:** preço ajustado por dividendos/splits = retorno total. O código NÃO calcula — só lê a coluna do CSV; o ajuste vem do provedor dos dados.
- **Volatilidade:** `ret.rolling(20).std() * 252**0.5` — desvio dos retornos de 20 dias, anualizado.
- **Métricas são da ESTRATÉGIA, não dos ativos:** Sharpe/MaxDD vêm dos retornos das decisões da estratégia. Os por ativo (PRIO 0,91) são buy&hold, só comparação. Por isso o DD da estratégia (−26%) < DD da PRIO (−79%).
- **Long-only, sem alavancagem, caixa rende 0** (conservador — o real seria melhor com CDI no caixa).
- **Custo incluído** (tabela Bovespa, 90% desc.); giro baixo → impacto desprezível.
- **Sem look-ahead** (`shift(1)`); 252 dias úteis, rf=0 na anualização.

---

## PARTE 10 — DEFESA: as 5 perguntas do chefe

1. **Por que momentum funciona?** Não é gap de informação (isso é HFT). É subreação em magnitude + fluxo institucional lento + possível prêmio de risco. Documentado em séculos e 100+ mercados.
2. **Só 3 ativos, é sorte?** Não afirmo certeza estatística — breadth baixa. A confiança vem do efeito ser comprovado FORA da amostra + da redução de risco (estrutural).
3. **Por que Sharpe da estratégia ≠ do ativo?** A estratégia muda QUANDO e QUANTO me exponho (rotaciona + corta na vol). Capturo a alta, evito o tombo.
4. **Robusta só porque PRIO foi foguete?** Em parte sim (o universo melhorou) — mas a habilidade está no timing (saiu da PRIO para a ITUB em 2025). Não alego puro mérito.
5. **"Faço no Excel"?** O sinal é simples de propósito. O valor está no vol targeting + média de parâmetros (DD −81% → −26%) e na disciplina sistemática.

(Detalhe completo em `DEFESA.md`, incluindo perguntas sobre os gráficos.)

---

## PARTE 11 — FRASE DE FECHAMENTO

> "Não entrego um Sharpe maquiado. Entrego um sistema que sabe onde tem edge, gerencia o decaimento sozinho rotacionando para o ativo que funciona, e é honesto sobre as próprias limitações — sinal simples, rigor no risco, exatamente como os grandes fundos operam. As rachaduras que apresento junto com o resultado são o que dá credibilidade."
