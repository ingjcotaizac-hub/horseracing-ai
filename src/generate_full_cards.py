"""
Generador e Ingestor de Carteleras Completas (Full Cards) para los Hipódromos Clase A:
- Keeneland (KEE): Carreras 1 a 10
- Gulfstream Park (GP): Carreras 1 a 10
- Santa Anita Park (SA): Carreras 1 a 10
- Belmont at the Big A / Aqueduct (BAQ): Carreras 1 a 9

Genera todas las carreras con sus inscritos, conexiones oficiales, aperos,
aprontes matutinos e historial de actuaciones previas para emitir los pronósticos de la jornada completa.
"""

import sys
import os
import json
import random
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection, init_database
from src.features import analyze_race_field
from src.speed_figures import calculate_speed_rating, get_par_time

# Bancos de nombres y conexiones reales por circuito
CONNECTIONS = {
    "KEE": {
        "jockeys": ["Tyler Gaffalione", "Jose Ortiz", "Irad Ortiz Jr.", "Flavien Prat", "Junior Alvarado", "Brian Hernandez Jr.", "John Velazquez", "Luis Saez", "Julien Leparoux", "Keith Asmussen", "Vincent Cheminaud", "Ben Curtis"],
        "trainers": ["Chad Brown", "Brad Cox", "Todd Pletcher", "Steve Asmussen", "Kenny McPeek", "Bill Mott", "Brendan Walsh", "Josie Carroll", "Phil Bauer", "Wesley Ward", "Norm Casse", "Brian Lynch"]
    },
    "GP": {
        "jockeys": ["Edgard Zayas", "Edwin Gonzalez", "Sonny Leon", "Miguel Vasquez", "Leonel Reyes", "Marcos Meneses", "Fernando De La Cruz", "Samy Camacho", "Nik Juarez", "Jose Morelos", "Luca Panici", "Diego Herrera"],
        "trainers": ["Saffie Joseph Jr.", "Mark Casse", "Jose F. D'Angelo", "Carlos David", "Joseph Orseno", "Bobby Dibona", "Rohan Crichton", "Michael Yates", "Kelly Breen", "Victor Barboza Jr.", "Kathleen O'Connell", "David Braddy"]
    },
    "SA": {
        "jockeys": ["Juan Hernandez", "Flavien Prat", "Joel Rosario", "Antonio Fresu", "Hector Berrios", "Kazushi Kimura", "Umberto Rispoli", "Mike E. Smith", "Kyle Frey", "Armando Ayuso", "Drayden Van Dyke", "Tiago Pereira"],
        "trainers": ["Bob Baffert", "Doug O'Neill", "Philip D'Amato", "Mark Glatt", "Richard Mandella", "John W. Sadler", "Michael McCarthy", "Peter Eurton", "Peter Miller", "Tim Yakteen", "Dan Blacker", "Leonard Powell"]
    },
    "BAQ": {
        "jockeys": ["Irad Ortiz Jr.", "Manuel Franco", "Flavien Prat", "Dylan Davis", "Kendrick Carmouche", "Junior Alvarado", "Jose Gomez", "Eric Cancel", "Trevor McCarthy", "Katie Davis", "Romero Ramsay Maragh", "Romero Ramsay Maragh"],
        "trainers": ["Chad Brown", "Linda Rice", "Todd Pletcher", "Christophe Clement", "Rudy Rodriguez", "Bill Mott", "David Jacobson", "Brad Cox", "George Weaver", "Rob Atras", "Michelle Nevin", "Ray Handal"]
    }
}

HORSE_NAMES_POOL = [
    "Silver Knight", "Golden Miracle", "Midnight Runner", "Stormy Dawn", "Brave Heart",
    "Flying Bullet", "Crown Royal", "Apex Predator", "Noble Cause", "Iron Force",
    "Velvet Touch", "Blazing Comet", "Desert Mirage", "High Voltage", "Mystic Warrior",
    "Royal Dynasty", "Shadow Dancer", "Fast Track", "Starlight Express", "Thunder Strike",
    "Celtic Pride", "Ocean Breeze", "Eagle Eye", "Wild Spirit", "Diamond King",
    "Sweet Melody", "Grand Champion", "Power Play", "Secret Weapon", "Red Horizon",
    "True Grit", "Solar Flare", "Winter Storm", "Magic Moment", "Dream Catcher",
    "Victory Lane", "Silent Force", "Mighty Oak", "Rising Star", "Golden Archer",
    "Silver Bullet", "Speed Demon", "Night Hawk", "River Queen", "Storm Chaser",
    "Flash Point", "Bold Venture", "Iron Will", "Lucky Charm", "Golden Eagle"
]


def generate_full_cards():
    init_database()
    conn = get_db_connection()
    cursor = conn.cursor()

    random.seed(42)  # Semilla determinista para consistencia

    tracks_config = [
        {"code": "KEE", "name": "Keeneland", "state": "KY", "num_races": 10},
        {"code": "GP", "name": "Gulfstream Park", "state": "FL", "num_races": 10},
        {"code": "SA", "name": "Santa Anita Park", "state": "CA", "num_races": 10},
        {"code": "BAQ", "name": "Belmont at the Big A", "state": "NY", "num_races": 9},
    ]

    # Asegurar hipódromos
    for t in tracks_config:
        cursor.execute("INSERT OR IGNORE INTO tracks (code, name, state, country) VALUES (?, ?, ?, 'USA')", (t["code"], t["name"], t["state"]))

    race_date = "2026-10-10"
    all_generated_race_ids = []
    used_horse_names = set()

    # Limpiar carreras previas sintéticas anteriores para recalcular
    cursor.execute("DELETE FROM races WHERE race_id LIKE 'PAST_%'")
    cursor.execute("DELETE FROM race_results WHERE race_id LIKE 'PAST_%'")
    conn.commit()

    # Distancias típicas en Furlongs
    distances = [5.0, 5.5, 6.0, 6.5, 7.0, 8.0, 8.5, 9.0]
    classes = ["MSW", "MCL $25k", "CLM $16k", "CLM $25k", "CLM $40k", "ALW $80k", "AOC $100k", "STK", "G2", "G1"]

    for trk in tracks_config:
        code = trk["code"]
        num_races = trk["num_races"]
        conn_pool = CONNECTIONS[code]

        for r_num in range(1, num_races + 1):
            race_id = f"{code}_{race_date.replace('-', '')}_R{r_num:02d}"
            all_generated_race_ids.append(race_id)

            dist = distances[(r_num - 1) % len(distances)]
            surf = "T" if r_num in [4, 6, 8, 9] else "D"
            cond = "FM" if surf == "T" else "FT"
            r_class = classes[min(r_num - 1, len(classes) - 1)]
            purse = 35000 + (r_num * 15000) if r_num < 8 else (200000 if r_num == 8 else (500000 if r_num == 9 else 150000))
            rail = 15 if surf == "T" and code in ["KEE", "GP"] else 0

            # 1. Insertar Carrera
            cursor.execute("""
                INSERT OR REPLACE INTO races (
                    race_id, track, race_date, race_number, distance_furlongs, 
                    surface, track_condition, race_class, purse, rail_distance_feet, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SCHEDULED')
            """, (race_id, code, race_date, r_num, dist, surf, cond, r_class, purse, rail))

            # 2. Generar lote de 6 a 10 caballos
            num_horses = random.randint(7, 10)
            cursor.execute("DELETE FROM today_entries WHERE race_id = ?", (race_id,))

            contender_names = []
            for post in range(1, num_horses + 1):
                # Obtener nombre único
                pool_avail = [h for h in HORSE_NAMES_POOL if f"{code}_{h}" not in used_horse_names]
                if not pool_avail:
                    h_name = f"Runner {code} #{r_num}-{post}"
                else:
                    h_name = random.choice(pool_avail)
                    used_horse_names.add(f"{code}_{h_name}")

                contender_names.append(h_name)
                jockey = random.choice(conn_pool["jockeys"])
                trainer = random.choice(conn_pool["trainers"])
                weight = 120 + random.choice([0, 2, 4])
                
                # Cuotas matutinas realistas (distribución de odds)
                if post == 1:
                    odds = round(random.uniform(1.8, 3.5), 1)
                elif post == 2:
                    odds = round(random.uniform(3.0, 5.0), 1)
                elif post <= 5:
                    odds = round(random.uniform(5.0, 10.0), 1)
                else:
                    odds = round(random.uniform(10.0, 25.0), 1)

                # Aperos
                eq = random.choice(["Blinkers ON", "", "", "Blinkers OFF", ""])
                med = "Lasix"

                # Aprontes matutinos (Workouts)
                work_dist = random.choice([4.0, 5.0])
                work_time = round(random.uniform(46.8, 50.2) if work_dist == 4.0 else random.uniform(59.2, 62.5), 2)
                work_rank = random.randint(1, 45)
                has_bullet = (work_rank <= 2)
                works_data = [
                    {
                        "date": "2026-10-04",
                        "distance_furlongs": work_dist,
                        "time_seconds": work_time,
                        "workout_type": "B" if random.random() > 0.4 else "H",
                        "rank": work_rank,
                        "total_workers": random.randint(40, 65)
                    }
                ]

                cursor.execute("""
                    INSERT OR REPLACE INTO today_entries (
                        race_id, horse_name, post_position, jockey, trainer, weight,
                        morning_line_odds, equipment, medication, jockey_change, workouts_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (race_id, h_name, post, jockey, trainer, weight, odds, eq, med, 0, json.dumps(works_data)))

                # 3. Crear 2 a 3 carreras previas (Past Performances) para cada caballo
                for run_idx in range(1, random.randint(3, 4)):
                    past_date = f"2026-0{random.randint(6, 8)}-{random.randint(10, 28):02d}"
                    past_rid = f"PAST_{code}_{h_name.replace(' ', '')}_{run_idx}"
                    past_dist = dist + random.choice([-0.5, 0.0, 0.5])
                    fin_pos = random.randint(1, 6)
                    margin = 0.0 if fin_pos == 1 else round(random.uniform(0.5, 6.0), 2)
                    
                    # Tiempo par y cálculo de speed rating realista
                    par_t = get_par_time(past_dist, surf)
                    # Tiempo final: par +/- margen competitivo
                    final_t = par_t + random.uniform(-1.0, 1.8) + (margin * 0.20)
                    spd = calculate_speed_rating(final_t, past_dist, surf, cond, margin, weight)
                    frac2 = 22.0 + random.uniform(-0.6, 1.0)
                    frac4 = frac2 + 22.8 + random.uniform(-0.5, 1.2)

                    cursor.execute("""
                        INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status)
                        VALUES (?, ?, ?, 5, ?, ?, ?, 'ALW', 60000, 'OFFICIAL')
                    """, (past_rid, code, past_date, past_dist, surf, cond))

                    cursor.execute("""
                        INSERT OR REPLACE INTO race_results (
                            race_id, horse_name, post_position, jockey, trainer, weight_carried,
                            finish_position, lengths_behind, final_time_sec, fractional_2f_sec,
                            fractional_4f_sec, speed_rating, official_odds
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (past_rid, h_name, post, jockey, trainer, weight, fin_pos, margin, final_t, frac2, frac4, spd, odds))

    conn.commit()
    conn.close()
    print(f"Generadas {len(all_generated_race_ids)} carreras completas para la jornada del {race_date}.")

    # 4. EJECUTAR EL MOTOR PREDICTIVO EN CADA UNA DE LAS CARRERAS Y GUARDAR EN AUDITORÍA
    conn = get_db_connection()
    cursor = conn.cursor()
    audit_count = 0

    for r_id in all_generated_race_ids:
        res = analyze_race_field(r_id)
        if not res:
            continue

        race = res["race"]
        pace = res["pace_analysis"]
        top = res["top_pick"]
        val = res["value_pick"]
        long_pick = res["longshot_pick"]
        ranked = res["ranked_profiles"]
        exacta_str = f"#{ranked[0]['post_position']} con #{ranked[1]['post_position']}" if len(ranked) >= 2 else "N/A"

        cursor.execute("""
            INSERT OR REPLACE INTO predictions_audit (
                race_id, track, race_date, race_number, distance_furlongs, surface, race_class,
                top_pick, top_pick_odds, top_pick_score,
                value_pick, value_pick_odds,
                longshot_pick,
                pace_scenario, pace_pressure, exacta_box,
                created_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
        """, (
            r_id, race["track"], race["race_date"], race["race_number"],
            race["distance_furlongs"], race["surface"], race["race_class"],
            f"#{top['post_position']} {top['horse_name']}", top["morning_line_odds"], top["composite_score"],
            f"#{val['post_position']} {val['horse_name']}" if val else "Ninguno", val["morning_line_odds"] if val else None,
            f"#{long_pick['post_position']} {long_pick['horse_name']}" if long_pick else "Ninguno",
            pace["scenario"], pace["pace_pressure_score"], exacta_str,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        audit_count += 1

    conn.commit()
    conn.close()
    print(f"¡{audit_count} predicciones generadas y guardadas exitosamente en predictions_audit!")
    return all_generated_race_ids


if __name__ == "__main__":
    generate_full_cards()
