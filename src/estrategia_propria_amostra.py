# -*- coding: utf-8 -*-
"""
estratégia-própria — base de amostra Path B (lab E54) no repo público.

NÃO é o motor de ranking (fica no lab). Aqui só:
  - carrega a série exportada
  - imprime a tabela de filme (E49–E54)
  - imprime o resumo do schema E55
  - deixa explícito: meta-treino = com o mentor

Rodar na raiz do repo:
  python3 src/estrategia_propria_amostra.py
  # ou: python3 estrategia_propria_amostra.py  (atalho na raiz)
"""
from pathlib import Path
import sys

import pandas as pd

_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from _paths import DADOS, ROOT  # noqa: E402

print("=" * 72)
print("estratégia-própria = BASE DE AMOSTRA (lab E54: mom 1m, semanal)")
print("Norte: sinal → ML | Meta-treino: COM O GUILHERME (não neste repo)")
print("=" * 72)

serie = DADOS / "estrategia_propria_diario.csv"
horiz = DADOS / "comparativo_horizontes_filme.csv"
schema = DADOS / "e55_schema_resumo.csv"
part = DADOS / "e55_schema_particoes.csv"

for p in (serie, horiz, schema, part):
    assert p.exists(), f"Falta {p} — repo desatualizado ou clone incompleto"

ep = pd.read_csv(serie, parse_dates=["dia"]).set_index("dia")
ret = ep["retorno_liquido"]
eq = (1 + ret).cumprod()
sharpe = ret.mean() / ret.std(ddof=1) * (252 ** 0.5)
dd = (eq / eq.cummax() - 1).min()
print(f"\nSérie {serie.name}: {ret.index.min().date()} → {ret.index.max().date()}")
print(f"  dias={len(ret)} | ret_acum={eq.iloc[-1]-1:+.2%} | "
      f"Sharpe*={sharpe:.2f} | MaxDD*={dd:.2%}")
print("  (*secundário — norte é filme/amostra, não placar)")

print("\n--- Comparativo de filme (Path B, stdout lab) ---")
h = pd.read_csv(horiz)
cols = ["experimento", "horizonte", "frequencia", "n_ordens", "n_rebalances",
        "custo_20bps", "retorno_liquido", "sharpe_zero_secundario", "papel"]
print(h[cols].to_string(index=False))

print("\n--- Schema E55 (labels; SEM treino) ---")
s = pd.read_csv(schema).iloc[0]
print(f"  N labels={int(s['n_labels'])} | taxa y=1={float(s['taxa_y1']):.1%}")
print(f"  train/test/holdout = "
      f"{int(s['n_train_ate_2019'])}/"
      f"{int(s['n_test_2020_2022'])}/"
      f"{int(s['n_holdout_desde_2023'])}")
print(f"  veredito={s['veredito_lab']}")
print(f"  meta_treino={s['meta_treino']}")
print("\nPartições × lado:")
print(pd.read_csv(part).to_string(index=False))

print("\n--- Onde ler no GitHub ---")
print(f"  {ROOT / 'ESTRATEGIA_PROPRIA.md'}")
print(f"  {ROOT / 'docs' / 'LINHA_RACIOCINIO.md'}")
print(f"  {ROOT / 'docs' / 'pseudocodigo' / 'base_amostra_e54.md'}")
print("=" * 72)
