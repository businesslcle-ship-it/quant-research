"""Caminhos do repo — todos os scripts em src/ importam daqui."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DADOS = ROOT / "dados"
FIGS = ROOT / "figures"
OUT = ROOT / "out"
DOCS = ROOT / "docs"

FIGS.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)
