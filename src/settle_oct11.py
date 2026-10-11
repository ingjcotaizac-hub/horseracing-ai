"""
Script de Liquidación Oficial de la Jornada del Domingo 11 de Octubre de 2026.
Liquida todas las carreras oficiales concluidas en Keeneland, Belmont (BAQ),
Gulfstream Park y Santa Anita.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.settle_and_learn import record_race_result, get_performance_summary

OFFICIAL_RESULTS_OCT_11 = [
    # =========================================================================
    # KEENELAND (KEE) - 11 OCT 2026
    # =========================================================================
    {
        "race_id": "KEE_20261011_R01",
        "winner": "Indy Charges On", "odds": 3.0,
        "second": "Pike Place", "third": "Bebedouro",
        "notes": "¡Top Pick (#3 Indy Charges On) y Exacta (#3 con #1) ACERTADOS!"
    },
    {
        "race_id": "KEE_20261011_R02",
        "winner": "Bourbonkoma", "odds": 6.0,
        "second": "Straitshootinlarry", "third": "Unionista",
        "notes": "Ganó Bourbonkoma a 6-1. Top Pick (#3 Unionista) en pizarra 3º."
    },
    {
        "race_id": "KEE_20261011_R03",
        "winner": "Wits and Wagers", "odds": 3.5,
        "second": "Fugitive Star", "third": "Coras Legacy",
        "notes": "Wits and Wagers ganó a 7/2. Retirados confirmados: Little Dixie y Hidden Recipe."
    },
    {
        "race_id": "KEE_20261011_R04",
        "winner": "Love Knicks Hart", "odds": 4.0,
        "second": "Tesouro de Pirata", "third": "Oraia",
        "notes": "Love Knicks Hart ganó. Top Pick (#6 Tesouro de Pirata) 2º en la exacta."
    },
    {
        "race_id": "KEE_20261011_R05",
        "winner": "Free Advice", "odds": 6.0,
        "second": "Password", "third": "Winery",
        "notes": "Free Advice ganó. Enemigo (#6 Password) 2º y Top Pick (#8 Winery) 3º."
    },
    {
        "race_id": "KEE_20261011_R06",
        "winner": "Fleetfoot Mac", "odds": 5.0,
        "second": "Kashville", "third": "Supreme Commander",
        "notes": "¡Top Pick (#2 Fleetfoot Mac) ACERTADO a 5.0-1! Gran dividendo (+ $10.00)."
    },
    {
        "race_id": "KEE_20261011_R07",
        "winner": "Modo", "odds": 2.5,
        "second": "Landed", "third": "Overcome Adversity",
        "notes": "Modo ganó a 5/2 sobre Landed."
    },
    {
        "race_id": "KEE_20261011_R08",
        "winner": "Time to Dazzle", "odds": 3.5,
        "second": "Ag Bullet", "third": "Usha",
        "notes": "G2 Franklin Stakes ($400k): ¡Top Pick (#3 Time to Dazzle) ACERTADO a 3.5-1 (+ $7.00)!"
    },
    {
        "race_id": "KEE_20261011_R09",
        "winner": "Turnback", "odds": 6.0,
        "second": "Colossus", "third": "Emilio",
        "notes": "Turnback ganó a 6-1."
    },

    # =========================================================================
    # GULFSTREAM PARK (GP) - 11 OCT 2026
    # =========================================================================
    {
        "race_id": "GP_20261011_R01",
        "winner": "Maximus Cat", "odds": 3.0,
        "second": "Mr. Bigshot", "third": "Freedom Street",
        "notes": "Maximus Cat ganó. Top Pick (#3 Mr. Bigshot) 2º en la exacta."
    },
    {
        "race_id": "GP_20261011_R02",
        "winner": "Philipina A", "odds": 3.0,
        "second": "Authentic Star", "third": "Gustavia",
        "notes": "¡El Enemigo (#1 Philipina A) ACERTADO a 3.0-1! Retirados: Sol Val Fleurie y Baby Masha."
    },
    {
        "race_id": "GP_20261011_R03",
        "winner": "Catch the Queen", "odds": 2.0,
        "second": "Bundalay", "third": "Baronia",
        "notes": "¡Top Pick (#2 Catch the Queen) ACERTADO a 2.0-1 (+ $4.00)!"
    },
    {
        "race_id": "GP_20261011_R04",
        "winner": "Sneak Preview", "odds": 6.0,
        "second": "The Best Distance", "third": "Pioneer Prince",
        "notes": "Sneak Preview ganó a 6-1. Enemigo The Best Distance 2º."
    },
    {
        "race_id": "GP_20261011_R05",
        "winner": "Uriel's Decree", "odds": 3.5,
        "second": "Dharmak", "third": "Fight And Pray",
        "notes": "¡El Enemigo (#2 Uriel's Decree) ACERTADO a 3.5-1! Top Pick (#1 Dharmak) 2º."
    },
    {
        "race_id": "GP_20261011_R06",
        "winner": "Somerset Mia", "odds": 8.0,
        "second": "Pretty Geisha", "third": "Sound It Out",
        "notes": "Somerset Mia ganó a 8-1. Enemigo Sound It Out 3º."
    },
    {
        "race_id": "GP_20261011_R07",
        "winner": "Zevi's Zone", "odds": 2.0,
        "second": "Governor Dutton", "third": "Titans Edge",
        "notes": "¡Top Pick (#1 Zevi's Zone) ACERTADO a 2.0-1 (+ $4.00)!"
    },
    {
        "race_id": "GP_20261011_R08",
        "winner": "Alinao Forever", "odds": 12.0,
        "second": "Full Nelson", "third": "Hillbilly Bob",
        "notes": "Alinao Forever sorpresa a 12-1."
    },

    # =========================================================================
    # BELMONT AT THE BIG A (BAQ) - 11 OCT 2026
    # =========================================================================
    {
        "race_id": "BAQ_20261011_R01",
        "winner": "Miss Twitter", "odds": 12.0,
        "second": "Runyon Canyon", "third": "Legal Squeeze",
        "notes": "Miss Twitter ganó a 12-1. Top Pick (#3 Runyon Canyon) 2º."
    },
    {
        "race_id": "BAQ_20261011_R02",
        "winner": "Asset Light", "odds": 4.0,
        "second": "Ethereal Quality", "third": "Fantasy Road",
        "notes": "Asset Light ganó a 4-1. Top Pick (#3 Ethereal Quality) 2º."
    },
    {
        "race_id": "BAQ_20261011_R03",
        "winner": "Just Tipsy", "odds": 8.0,
        "second": "Tap Rules", "third": "Karsten",
        "notes": "💣 ¡BOMBA ACERTADA! #3 Just Tipsy ganó a 8.0-1 (+ $16.00 neto) sobre el Top Pick Tap Rules (2º)."
    },
    {
        "race_id": "BAQ_20261011_R04",
        "winner": "Lisa Joy", "odds": 4.0,
        "second": "Alibi", "third": "Consensus View",
        "notes": "Lisa Joy ganó a 4-1."
    },
    {
        "race_id": "BAQ_20261011_R05",
        "winner": "Zomoroda", "odds": 5.0,
        "second": "Cornichiwa", "third": "Breaker",
        "notes": "Zomoroda ganó a 5-1. Enemigo Cornichiwa 2º."
    },
    {
        "race_id": "BAQ_20261011_R06",
        "winner": "Mike's Magic", "odds": 10.0,
        "second": "Hot Property", "third": "Escape Hall",
        "notes": "Mike's Magic ganó a 10-1."
    },
    {
        "race_id": "BAQ_20261011_R07",
        "winner": "Our Preferred Pal", "odds": 3.5,
        "second": "Credit Risk", "third": "Clap Back",
        "notes": "¡Top Pick (#1 Our Preferred Pal) ACERTADO a 3.5-1 (+ $7.00)!"
    },
    {
        "race_id": "BAQ_20261011_R08",
        "winner": "Three Thirteen", "odds": 4.0,
        "second": "Noble One", "third": "Sicilian Defense",
        "notes": "Three Thirteen ganó a 4-1."
    },

    # =========================================================================
    # SANTA ANITA PARK (SA) - 11 OCT 2026 (Primeras Carreras Concluidas)
    # =========================================================================
    {
        "race_id": "SA_20261011_R01",
        "winner": "Sip It", "odds": 3.5,
        "second": "Ocean Club", "third": "Character",
        "notes": "¡Top Pick (#3 Sip It) ACERTADO a 3.5-1 (+ $7.00)! Además la Bomba (#8 Character) 3º en pizarra."
    },
    {
        "race_id": "SA_20261011_R02",
        "winner": "Kivo", "odds": 3.0,
        "second": "Bold Type", "third": "Cyprus Avenue",
        "notes": "¡Top Pick (#2 Kivo) ACERTADO a 3.0-1 (+ $6.00)!"
    }
]


def settle_all_oct11():
    print(f"Liquidando {len(OFFICIAL_RESULTS_OCT_11)} carreras oficiales de hoy...")
    success = 0
    for r in OFFICIAL_RESULTS_OCT_11:
        ok = record_race_result(
            race_id=r["race_id"],
            actual_winner=r["winner"],
            actual_odds=r["odds"],
            second_place=r.get("second", ""),
            third_place=r.get("third", ""),
            race_notes=r.get("notes", "")
        )
        if ok:
            success += 1

    print(f"\n¡{success} carreras liquidadas oficialmente!")
    summary = get_performance_summary()
    print("\n--- RESUMEN GLOBAL DE RENDIMIENTO ---")
    print(f"Total Evaluadas: {summary['total_evaluated']}")
    print(f"Aciertos Top Pick (Win-Only): {summary['wins']} ({summary['win_rate']}%)")
    print(f"Aciertos El Enemigo: {summary.get('enemy_wins', 0)}")
    print(f"Aciertos Combinados (Top Pick o Enemigo): {summary.get('combined_wins', 0)} ({summary.get('combined_win_rate', 0)}%)")
    print(f"Exactas Acertadas: {summary.get('exacta_hits', 0)}")
    print(f"En Pizarra (ITM %): {summary['itm_rate']}%")
    print(f"P/L Total: ${summary['total_profit']:+.2f} | ROI: {summary['roi_pct']:+.1f}%")
    print(f"Carreras Aún Pendientes: {summary['pending_count']}")


if __name__ == "__main__":
    settle_all_oct11()
