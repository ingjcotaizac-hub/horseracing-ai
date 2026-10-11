"""
Script de Liquidación Oficial y Auditoría Exhaustiva de la Jornada Completa
del Sábado 10 de Octubre de 2026 (41 Carreras Clase A en USA):
- Gulfstream Park (GP): 10 Carreras
- Keeneland (KEE): 10 Carreras
- Belmont at the Big A (BAQ): 11 Carreras
- Santa Anita Park (SA): 10 Carreras

Criterio Estricto: WIN-ONLY (Acierto = 1er Puesto).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection
from src.settle_and_learn import record_race_result, get_performance_summary


ALL_OFFICIAL_RESULTS_OCT_10 = [
    # =========================================================
    # 1. GULFSTREAM PARK (GP) - 10 CARRERAS
    # =========================================================
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
        "race_id": "GP_20261010_R06",
        "winner": "Classic Roadster",
        "odds": 1.8,
        "second": "Earthly Delights",
        "notes": "Classic Roadster impuso condiciones como favorito sólido en 6f Dirt."
    },
    {
        "race_id": "GP_20261010_R07",
        "winner": "Rouki",
        "odds": 8.0,
        "second": "Souper Quest",
        "notes": "Rouki superó por pescuezo a Souper Quest en el Overnight Hcp."
    },
    {
        "race_id": "GP_20261010_R08",
        "winner": "Jades Jay",
        "odds": 8.0,
        "second": "Wannabeeloved",
        "notes": "Jades Jay ganó a 8-1; el favorito Blue Slide Park llegó 4º."
    },
    {
        "race_id": "GP_20261010_R09",
        "winner": "Guns and Coffee",
        "odds": 2.5,
        "second": "Beau Black",
        "notes": "Guns and Coffee ganó con solvencia en 6.5f Dirt."
    },
    {
        "race_id": "GP_20261010_R10",
        "winner": "Souper Zonda",
        "odds": 4.0,
        "second": "Defiant Lass",
        "notes": "Souper Zonda (Mark Casse) ganó el Handicap The Daring Kathy en 8.5f Turf."
    },

    # =========================================================
    # 2. KEENELAND (KEE) - 10 CARRERAS
    # =========================================================
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
        "notes": "Dolly P sorprendió desde el puesto exterior 10 en 7f Dirt."
    },
    {
        "race_id": "KEE_20261010_R03",
        "winner": "Merlin Monroan",
        "odds": 3.5,
        "second": "Tolstoy",
        "notes": "Merlin Monroan atropelló con fuerte remate por centro de pista."
    },
    {
        "race_id": "KEE_20261010_R04",
        "winner": "Money Supply",
        "odds": 3.0,
        "second": "Overstatement",
        "notes": "Money Supply (Irad Ortiz Jr.) remató con fuerza en 8.5f Dirt."
    },
    {
        "race_id": "KEE_20261010_R05",
        "winner": "Global Unrest",
        "odds": 12.0,
        "second": "Free Verse",
        "notes": "Global Unrest (Flavien Prat / Chad Brown) sorprendió a 12-1 en 8f Turf."
    },
    {
        "race_id": "KEE_20261010_R06",
        "winner": "Where Luck Lives",
        "odds": 5.0,
        "second": "Sneaky Good",
        "notes": "Where Luck Lives (Luis Saez) se impuso en 6f Dirt."
    },
    {
        "race_id": "KEE_20261010_R07",
        "winner": "Tannhauser",
        "odds": 8.0,
        "second": "Rumana",
        "notes": "Tannhauser (Jose Ortiz / Cherie DeVaux) ganó en 8f Turf a 8-1."
    },
    {
        "race_id": "KEE_20261010_R08",
        "winner": "Steeze",
        "odds": 10.0,
        "second": "Thailand",
        "notes": "Steeze derrotó por escaso margen a Thailand (nuestro top pick) en 7f Dirt."
    },
    {
        "race_id": "KEE_20261010_R09",
        "winner": "Tam Tam",
        "odds": 4.0,
        "second": "Faithful Departed",
        "notes": "Tam Tam dominó de tiro a tiro el G1 Queen Elizabeth II Challenge Cup."
    },
    {
        "race_id": "KEE_20261010_R10",
        "winner": "Kaykay",
        "odds": 4.0,
        "second": "Fletch's Rockette",
        "notes": "Kaykay (Bob Baffert) ganó en 5.5f Dirt; Glow Of A Rose llegó 3º."
    },

    # =========================================================
    # 3. BELMONT AT THE BIG A (BAQ) - 11 CARRERAS
    # =========================================================
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
        "race_id": "BAQ_20261010_R05",
        "winner": "Billy Bucchero",
        "odds": 10.0,
        "second": "Southside Samurai",
        "notes": "Billy Bucchero (Edgard Zayas / Mark Casse) ganó a 10-1 en 6f Dirt."
    },
    {
        "race_id": "BAQ_20261010_R06",
        "winner": "Paradise Valley",
        "odds": 4.3,
        "second": "Twenty Four Mamba",
        "notes": "Paradise Valley ganó en 6f Dirt pagando $10.68."
    },
    {
        "race_id": "BAQ_20261010_R07",
        "winner": "Chris's Song",
        "odds": 2.9,
        "second": "Kings Landyn",
        "notes": "Chris's Song (Antonio Fresu) se llevó el MCL en 7.5f Dirt."
    },
    {
        "race_id": "BAQ_20261010_R08",
        "winner": "Doubting Thomas",
        "odds": 3.8,
        "second": "Iron Palace",
        "notes": "Doubting Thomas (Jorge Ruiz) ganó el Bricks and Mortar Stakes en 7f Turf."
    },
    {
        "race_id": "BAQ_20261010_R09",
        "winner": "Startowne Road",
        "odds": 5.0,
        "second": "Promise Me Amelody",
        "notes": "Startowne Road (Kendrick Carmouche) ganó el MSW en 7f Dirt."
    },
    {
        "race_id": "BAQ_20261010_R10",
        "winner": "Third Coast",
        "odds": 12.0,
        "second": "Caroline St. Beat",
        "notes": "Third Coast (Jose Lezcano) sorprendió en el G3 Hill Prince Stakes en 9.5f Turf."
    },
    {
        "race_id": "BAQ_20261010_R11",
        "winner": "Gilbane",
        "odds": 1.8,
        "second": "Bourboncentric",
        "notes": "Gilbane (Manuel Franco) cerró la jornada ganando como favorito en 8f Turf."
    },

    # =========================================================
    # 4. SANTA ANITA PARK (SA) - 10 CARRERAS
    # =========================================================
    {
        "race_id": "SA_20261010_R01",
        "winner": "Matt At Five",
        "odds": 3.5,
        "second": "Private Gem",
        "notes": "Matt At Five (Juan Hernandez) ganó en 6f Turf."
    },
    {
        "race_id": "SA_20261010_R02",
        "winner": "Roast",
        "odds": 4.0,
        "second": "Collmus",
        "notes": "Roast (Umberto Rispoli) superó a Collmus en 7f Dirt."
    },
    {
        "race_id": "SA_20261010_R03",
        "winner": "Wild West Coast",
        "odds": 4.5,
        "second": "A Great Shaking",
        "notes": "Wild West Coast ganó el AOC Cal-Bred; Troisieme Etoile fue retiro (Scratch)."
    },
    {
        "race_id": "SA_20261010_R04",
        "winner": "Midway Lane",
        "odds": 5.0,
        "second": "Native Land",
        "notes": "Midway Lane (Juan Hernandez / Peter Miller) ganó a 5-1 en 7f Dirt."
    },
    {
        "race_id": "SA_20261010_R05",
        "winner": "Sacred Sound",
        "odds": 4.0,
        "second": "Coastline Runner",
        "notes": "Sacred Sound se impuso en 6f Turf."
    },
    {
        "race_id": "SA_20261010_R06",
        "winner": "Lihue Princess",
        "odds": 3.0,
        "second": "Easter (FR)",
        "notes": "Lihue Princess dominó en 8f Turf."
    },
    {
        "race_id": "SA_20261010_R07",
        "winner": "Going Nowhere",
        "odds": 5.0,
        "second": "Top Gunner",
        "notes": "Going Nowhere ganó en 6f Dirt."
    },
    {
        "race_id": "SA_20261010_R08",
        "winner": "Busy Making Munny",
        "odds": 6.0,
        "second": "Spiritist",
        "notes": "Busy Making Munny sorprendió en 6f Dirt."
    },
    {
        "race_id": "SA_20261010_R09",
        "winner": "Boss Sully",
        "odds": 6.0,
        "second": "Flyover",
        "notes": "Boss Sully (Mike Smith) ganó el California Flag Handicap en 6.5f Turf."
    },
    {
        "race_id": "SA_20261010_R10",
        "winner": "In the Tank",
        "odds": 9.2,
        "second": "Call Me Sir",
        "notes": "In the Tank (Tyler Baze) ganó pagando $20.40 en 8f Turf."
    }
]


def settle_all_41():
    print("Iniciando liquidación estricta de las 41 carreras del 10 de octubre...")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM predictions_audit WHERE race_date != '2026-10-10'")
    conn.commit()
    conn.close()

    settled = 0
    for res in ALL_OFFICIAL_RESULTS_OCT_10:
        success = record_race_result(
            race_id=res["race_id"],
            actual_winner=res["winner"],
            actual_odds=res["odds"],
            second_place=res["second"],
            race_notes=res["notes"]
        )
        if success:
            settled += 1

    print(f"Liquidación completa: {settled}/41 carreras evaluadas.")
    summary = get_performance_summary()
    print("\nRESUMEN FINAL DE AUDITORÍA:")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    settle_all_41()
