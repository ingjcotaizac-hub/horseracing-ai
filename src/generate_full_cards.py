"""
Módulo de generación de carteleras completas.
Redirige directamente al ingestor oficial de carteleras reales: src.ingest_real_cards.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingest_real_cards import ingest_real_cards


def generate_full_cards():
    """Genera e ingesta las carteleras reales para la jornada completa."""
    return ingest_real_cards()


if __name__ == "__main__":
    generate_full_cards()
