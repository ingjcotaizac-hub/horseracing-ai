"""
Módulo de Pronósticos Oficiales de Hoy (Sábado 10 de Octubre de 2026)
para los Hipódromos Clase A de USA:
- Keeneland (KEE): Carreras 1 a 10
- Gulfstream Park (GP): Carreras 1 a 10
- Santa Anita Park (SA): Carreras 1 a 10
- Belmont at the Big A / Aqueduct (BAQ): Carreras 1 a 9

Genera todas las carreras de la jornada completa (Full Cards, 39 carreras en total)
y guarda las predicciones en la tabla 'predictions_audit' para evaluación y aprendizaje futuro.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingest_real_cards import ingest_real_cards


def populate_and_predict_today():
    """Genera y pronostica la cartelera completa con los caballos REALES de todos los hipódromos Clase A."""
    return ingest_real_cards()


if __name__ == "__main__":
    races = populate_and_predict_today()
    print(f"Predicciones completadas para {len(races)} carreras Clase A de hoy.")
