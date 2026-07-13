"""Atalho na raiz — a logica vive em src/. Uso: python3 rotacao_graf.py"""
import sys
import runpy
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
runpy.run_path(str(ROOT / "src" / "rotacao_graf.py"), run_name="__main__")
