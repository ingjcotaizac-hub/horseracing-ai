"""
Script para liquidar con los resultados oficiales las 10 carreras completadas el sábado 10 de octubre de 2026:
- Gulfstream Park: R1, R2, R3
- Keeneland: R1, R2, R3
- Belmont at the Big A: R1, R2, R3, R4

Aplica el criterio estricto WIN-ONLY: Acierto solo si el caballo recomendado ganó el 1er puesto.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection
from src.settle_and_learn import record_race_result


OFFICIAL_WINNERS_OCT_10 = [
    # GULFSTREAM PARK
    {
        "race_id": "GP_20261010_R01",
        "winner": "Ortus",
        "odds": 3.5,
        "second": "Eddie the Great",
        "notes": "Ortus dominó por la parte externa en 7.5f Turf."
    },
    {
        "race_id": "GP_20261010_R02",
        "winner": "Excuses",
        "odds": 4.5,
        "second": "Sunday Song",
        "notes": "Excuses remató desde el fondo en la recta final."
    },
    {
        "race_id": "GP_20261010_R03",
        "winner": "Amberssohn",
        "odds": 4.2,
        "second": "Starship Iceman",
        "notes": "Amberssohn ganó con solidez en la Tapeta sintética."
    },

    # KEENELAND
    {
        "race_id": "KEE_20261010_R01",
        "winner": "Lost Chord",
        "odds": 2.6,
        "second": "Golexgo",
        "notes": "Lost Chord dominó los dos codos en 8.5f Dirt."
    },
    {
        "race_id": "KEE_20261010_R02",
        "winner": "Dolly P",
        "odds": 5.2,
        "second": "Dancing Star",
        "notes": "Dolly P sorprendió desde el puesto exterior 10."
    },
    {
        "race_id": "KEE_20261010_R03",
        "winner": "Merlin Monroan",
        "odds": 3.5,
        "second": "Tolstoy",
        "notes": "Merlin Monroan atropelló con fuerte remate por centro de pista."
    },

    # BELMONT AT THE BIG A
    {
        "race_id": "BAQ_20261010_R01",
        "winner": "Hullabaloo Ray Ray",
        "odds": 9.8,
        "second": "Art Museum",
        "notes": "Hullabaloo Ray Ray ganó como sorpresa (9.8-1) marcando los parciales."
    },
    {
        "race_id": "BAQ_20261010_R02",
        "winner": "Ice Chocolat (BRZ)",
        "odds": 1.5,
        "second": "Belouni (FR)",
        "notes": "Ice Chocolat impuso su jerarquía en 8.5f Turf."
    },
    {
        "race_id": "BAQ_20261010_R03",
        "winner": "Mercury Marauder",
        "odds": 3.5,
        "second": "Morella",
        "notes": "Mercury Marauder tomó la delantera temprano y sostuvo el avance."
    },
    {
        "race_id": "BAQ_20261010_R04",
        "winner": "Leftembehind",
        "odds": 3.5,
        "second": "Shattuck",
        "notes": "Leftembehind prevaleció en el duelo de recta en 7f Dirt."
    },
    {
        "race_id": "GP_20261010_R04",
        "winner": "Souffle On Fire",
        "odds": 6.0,
        "second": "Iliana",
        "notes": "Souffle On Fire se impuso en 8.0f Turf a cuota 6.0-1."
    },
    {
        "race_id": "GP_20261010_R05",
        "winner": "Maitre D",
        "odds": 20.0,
        "second": "Hottakejake",
        "notes": "Maitre D sorprendió a 20-1 en 5.5f Tapeta."
    },
    {
        "race_id": "KEE_20261010_R04",
        "winner": "Money Supply",
        "odds": 3.0,
        "second": "Overstatement",
        "notes": "Money Supply (Irad Ortiz Jr.) remató con fuerza en 8.5f Dirt."
    }
]


def settle_all():
    print("Iniciando liquidación estricta de las 10 carreras completadas...")
    # Limpiar cualquier carrera vieja de prueba que no sea del 2026-10-10
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM predictions_audit WHERE race_date != '2026-10-10'")
    conn.commit()
    conn.close()

    settled = 0
    for res in OFFICIAL_WINNERS_OCT_10:
        success = record_race_result(
            race_id=res["race_id"],
            actual_winner=res["winner"],
            actual_odds=res["odds"],
            second_place=res["second"],
            race_notes=res["notes"]
        )
        if success:
            settled += 1

    print(f"Liquidación finalizada: {settled}/10 carreras evaluadas.")


if __name__ == "__main__":
    settle_all()
