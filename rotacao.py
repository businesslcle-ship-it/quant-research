"""Atalho na raiz — a logica vive em src/. Uso: python3 rotacao.py"""
import sys
import runpy
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
runpy.run_path(str(ROOT / "src" / "rotacao.py"), run_name="__main__")
