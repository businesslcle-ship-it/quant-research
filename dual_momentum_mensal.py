"""Atalho na raiz — a logica vive em src/. Uso: python3 dual_momentum_mensal.py"""
import sys
import runpy
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
runpy.run_path(str(ROOT / "src" / "dual_momentum_mensal.py"), run_name="__main__")
