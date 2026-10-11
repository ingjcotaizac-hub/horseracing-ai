"""
Módulo de Pronósticos Oficiales de Hoy (Domingo 11 de Octubre de 2026)
para los Hipódromos Clase A de USA:
- Keeneland (KEE): Carreras 1 a 9 (con G2 Franklin Stakes)
- Gulfstream Park (GP): Carreras 1 a 9
- Santa Anita Park (SA): Carreras 1 a 9 (con California Distaff Hcp)
- Belmont at the Big A (BAQ): Carreras 1 a 9 (con Carle Place Stakes)

Genera todas las carreras de la jornada completa (Full Cards, 36 carreras en total)
y guarda las predicciones en la tabla 'predictions_audit' para evaluación y aprendizaje futuro.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingest_oct11 import ingest_today_oct11


def populate_and_predict_today():
    """Genera y pronostica la cartelera completa con los caballos REALES de todos los hipódromos Clase A."""
    return ingest_today_oct11()


if __name__ == "__main__":
    races = populate_and_predict_today()
    print(f"Predicciones completadas para {len(races)} carreras Clase A del Domingo 11 de Octubre.")
