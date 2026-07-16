# Pseudocódigos

Cada arquivo narra o código **linha a linha** em português — a prova oral disfarçada que o mentor pede. A versão canônica no GitHub é o `.md` (sempre alinhada a `src/`). O `.docx` é a mesma narrativa, para abrir no Word / entregar impresso.

| Estratégia | Código | Markdown | Word |
|---|---|---|---|
| Rotação Momentum v2 | [`src/rotacao.py`](../../src/rotacao.py) | [rotacao_v2.md](rotacao_v2.md) | [rotacao_v2.docx](rotacao_v2.docx) |
| Dual Momentum (apresentado) | [`src/dual_momentum.py`](../../src/dual_momentum.py) | [dual_momentum.md](dual_momentum.md) | [dual_momentum.docx](dual_momentum.docx) |
| **estratégia-própria** | série `dados/estrategia_propria_diario.csv` (lab E45) | [estrategia_propria.md](estrategia_propria.md) | — |

O Dual Momentum apresentado avalia o núcleo do livro nas **barras de 60min** (com histerese de 5%). O baseline mensal (`dual_momentum_mensal.py`) é outra versão — só para comparar.

**Regra de consistência:** se o código mudar, regenerar o pseudocódigo na mesma entrega (números e linhas têm de bater).
