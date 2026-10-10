"""
Visor de Past Performances (Gaceta de Carreras Oficial) en Terminal / CLI.
Permite consultar las actuaciones anteriores, aprontes y perfil de cualquier ejemplar o carrera.

Uso:
  python src/view_past_performance.py --track KEE --race 1
  python src/view_past_performance.py --horse "Silver Knight"
  python src/view_past_performance.py --card GP
  python src/view_past_performance.py --summary
"""

import sys
import os
import argparse
import json
from tabulate import tabulate

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection
from src.features import get_horse_past_performances, analyze_race_field

# Forzar salida utf-8 en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def show_summary():
    """Muestra el resumen de todas las carreras y pistas cargadas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.track, t.name as track_name, r.race_date, COUNT(r.race_id) as total_races
        FROM races r
        LEFT JOIN tracks t ON r.track = t.code
        WHERE r.status = 'SCHEDULED'
        GROUP BY r.track, r.race_date
        ORDER BY r.track ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    print("\n" + "=" * 70)
    print("   🏇 PROGRAMAS DE CARRERAS DISPONIBLES (USA CLASE A)")
    print("=" * 70)
    data = []
    for r in rows:
        data.append([r["track"], r["track_name"], r["race_date"], f"{r['total_races']} carreras programadas"])
    print(tabulate(data, headers=["Código", "Hipódromo", "Fecha", "Carreras"], tablefmt="grid"))
    print("\nPara ver una carrera específica:")
    print("  python src/view_past_performance.py --track KEE --race 1")
    print("Para ver la cartelera completa de un hipódromo:")
    print("  python src/view_past_performance.py --card SA")
    print("Para ver el historial de un caballo:")
    print("  python src/view_past_performance.py --horse \"Silver Knight\"\n")


def show_race_program(track_code: str, race_number: int):
    """Muestra la gaceta completa de una carrera específica."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.*, t.name as track_name
        FROM races r
        LEFT JOIN tracks t ON r.track = t.code
        WHERE r.track = ? AND r.race_number = ? AND r.status = 'SCHEDULED'
    """, (track_code.upper(), race_number))
    race = cursor.fetchone()

    if not race:
        print(f"\n[!] No se encontró la carrera {track_code.upper()} R{race_number}.")
        conn.close()
        return

    race_dict = dict(race)
    race_id = race_dict["race_id"]

    cursor.execute("""
        SELECT * FROM today_entries WHERE race_id = ? ORDER BY post_position ASC
    """, (race_id,))
    entries = [dict(e) for e in cursor.fetchall()]
    conn.close()

    surf_name = "Arena (Dirt)" if race_dict["surface"] == "D" else ("Grama (Turf)" if race_dict["surface"] == "T" else "Sintética")

    print("\n" + "=" * 80)
    print(f"🏇 {race_dict['track_name']} ({race_dict['track']}) - CARRERA #{race_dict['race_number']}")
    print(f"📅 Fecha: {race_dict['race_date']} | Distancia: {race_dict['distance_furlongs']} Furlongs (~{int(race_dict['distance_furlongs']*201.16)} m)")
    print(f"🌱 Pista: {surf_name} ({race_dict['track_condition']}) | Baranda: {race_dict.get('rail_distance_feet', 0)} ft")
    print(f"💰 Bolsa: ${race_dict['purse']:,.0f} | Clase: {race_dict['race_class']}")
    print("=" * 80)

    # Tabla general de inscritos
    entry_rows = []
    for e in entries:
        works = json.loads(e.get("workouts_json") or "[]")
        work_str = "Sin registro"
        if works:
            w = works[0]
            bullet = " 🎯 [BULLET]" if w.get("rank", 99) <= 2 else ""
            work_str = f"{w['distance_furlongs']}f en {w['time_seconds']}s (Rank {w.get('rank', '-')}/{w.get('total_workers', '-')}){bullet}"

        eq_str = e.get("equipment") or "Normal"
        entry_rows.append([
            f"#{e['post_position']}",
            e["horse_name"],
            f"{e['morning_line_odds']:.1f}-1",
            e["jockey"],
            e["trainer"],
            f"{e['weight']} lbs",
            eq_str,
            work_str
        ])

    print("\n📋 PARTICIPANTES INSCRITOS:")
    print(tabulate(entry_rows, headers=["PP", "Ejemplar", "M/L", "Jinete", "Entrenador", "Peso", "Aperos", "Último Apronte"], tablefmt="fancy_grid"))

    # Mostrar Past Performances detalladas por caballo
    print("\n" + "-" * 80)
    print("📑 HISTORIAL DE PAST PERFORMANCES (ACTUACIONES ANTERIORES):")
    print("-" * 80)

    for e in entries:
        h_name = e["horse_name"]
        pps = get_horse_past_performances(h_name, before_date=race_dict["race_date"])
        print(f"\n🐴 #{e['post_position']} {h_name} | M/L: {e['morning_line_odds']:.1f}-1 | Jinete: {e['jockey']} | Prep: {e['trainer']}")

        if not pps:
            print("   ↳ Sin actuaciones previas registradas (Debutante).")
            continue

        pp_table = []
        for p in pps:
            fin = f"{p['finish_position']}º" if p['finish_position'] > 1 else "1º GANÓ"
            margin = f"+{p['lengths_behind']} cpos" if p['finish_position'] > 1 else "0.0"
            pp_table.append([
                p["race_date"],
                p["track"],
                f"{p['distance_furlongs']}f {p['surface']}",
                p["track_condition"],
                p["race_class"],
                fin,
                margin,
                f"{p['final_time_sec']:.2f}s",
                f"{p['speed_rating']:.1f}",
                p["jockey"],
                f"{p['official_odds']}-1"
            ])

        print(tabulate(pp_table, headers=["Fecha", "Hip", "Dist/Pista", "Cond", "Clase", "Pos", "Margen", "Tiempo", "Speed", "Jinete", "Cuota"], tablefmt="simple"))


def show_horse_history(horse_name: str):
    """Muestra el historial y ficha completa de un caballo."""
    pps = get_horse_past_performances(horse_name)
    if not pps:
        print(f"\n[!] No se encontraron actuaciones para el caballo '{horse_name}'.")
        return

    print("\n" + "=" * 80)
    print(f"🐴 FICHA DE PAST PERFORMANCE: {horse_name.upper()}")
    print("=" * 80)

    pp_table = []
    for p in pps:
        fin = f"{p['finish_position']}º" if p['finish_position'] > 1 else "1º GANÓ"
        margin = f"+{p['lengths_behind']} cpos" if p['finish_position'] > 1 else "0.0"
        pp_table.append([
            p["race_date"],
            p["track"],
            f"{p['distance_furlongs']}f {p['surface']}",
            p["track_condition"],
            p["race_class"],
            fin,
            margin,
            f"{p['final_time_sec']:.2f}s",
            f"{p['speed_rating']:.1f}",
            p["jockey"],
            p["trainer"],
            f"{p['official_odds']}-1"
        ])

    print(tabulate(pp_table, headers=["Fecha", "Hip", "Dist/Pista", "Cond", "Clase", "Pos", "Margen", "Tiempo", "Speed", "Jinete", "Trainer", "Cuota"], tablefmt="fancy_grid"))


def main():
    parser = argparse.ArgumentParser(description="Visor de Past Performances y Gacetas de Carreras")
    parser.add_argument("--track", type=str, help="Código del Hipódromo (ej: KEE, GP, SA, BAQ)")
    parser.add_argument("--race", type=int, help="Número de carrera (ej: 1, 5, 10)")
    parser.add_argument("--horse", type=str, help="Nombre del caballo a consultar")
    parser.add_argument("--card", type=str, help="Ver todas las carreras de un hipódromo")
    parser.add_argument("--summary", action="store_true", help="Mostrar resumen de todas las pistas y carreras")

    args = parser.parse_args()

    if args.summary or (not args.track and not args.horse and not args.card):
        show_summary()
    elif args.horse:
        show_horse_history(args.horse)
    elif args.card:
        for r in range(1, 11):
            show_race_program(args.card, r)
    elif args.track and args.race:
        show_race_program(args.track, args.race)
    else:
        print("\nUso incorrecto. Ejecuta:")
        print("  python src/view_past_performance.py --track KEE --race 1")
        print("  python src/view_past_performance.py --summary")


if __name__ == "__main__":
    main()
