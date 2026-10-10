"""
Módulo de Pronósticos Oficiales de Hoy (Sábado 10 de Octubre de 2026)
para los Hipódromos Clase A de USA:
- Keeneland (KEE): Queen Elizabeth II Challenge Cup (Grado 1) y Allowance Sprint
- Santa Anita Park (SA): California Flag Handicap (Stakes)
- Belmont at the Big A / Aqueduct (BAQ): Sands Point Stakes (Grado 2)
- Gulfstream Park (GP): Hollywood Beach Stakes

Guarda todas las predicciones en la tabla 'predictions_audit' para evaluación y aprendizaje futuro.
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection, init_database
from src.features import analyze_race_field
from src.speed_figures import calculate_speed_rating


def populate_and_predict_today():
    init_database()
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Asegurar Hipódromos Clase A
    tracks = [
        ("KEE", "Keeneland", "KY", "USA"),
        ("SA", "Santa Anita Park", "CA", "USA"),
        ("BAQ", "Belmont at the Big A (Aqueduct)", "NY", "USA"),
        ("GP", "Gulfstream Park", "FL", "USA"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO tracks (code, name, state, country) VALUES (?, ?, ?, ?)", tracks)

    # -------------------------------------------------------------
    # CARRERA 1: KEENELAND - CARRERA 9 (G1 Queen Elizabeth II Challenge Cup)
    # 9.0 Furlongs en Grama (Turf), Bolsa $750,000
    # -------------------------------------------------------------
    r1_id = "KEE_20261010_R09"
    cursor.execute("""
        INSERT OR REPLACE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, rail_distance_feet, status)
        VALUES (?, 'KEE', '2026-10-10', 9, 9.0, 'T', 'FM', 'G1 - Queen Elizabeth II Challenge Cup', 750000, 15, 'SCHEDULED')
    """, (r1_id,))

    r1_entries = [
        (r1_id, "Haute Diva", 1, "Keith Asmussen", "Patrick Biancone", 121, 30.0, "", "Lasix", 0, "[]"),
        (r1_id, "Luster", 2, "John Velazquez", "Josie Carroll", 121, 2.5, "", "Lasix", 0, json.dumps([{"date": "2026-10-03", "distance_furlongs": 4.0, "time_seconds": 47.80, "workout_type": "B", "rank": 2, "total_workers": 48}])),
        (r1_id, "Tam Tam", 3, "Junior Alvarado", "Phil Bauer", 121, 4.0, "Blinkers ON", "Lasix", 0, json.dumps([{"date": "2026-10-04", "distance_furlongs": 4.0, "time_seconds": 48.20, "workout_type": "B", "rank": 5, "total_workers": 50}])),
        (r1_id, "Faithful Departed", 4, "Jose Ortiz", "Grant Forster", 121, 3.5, "", "Lasix", 0, json.dumps([{"date": "2026-10-02", "distance_furlongs": 5.0, "time_seconds": 60.10, "workout_type": "B", "rank": 1, "total_workers": 35}])),
        (r1_id, "Turner's Charm", 5, "Ben Curtis", "Brendan Walsh", 121, 20.0, "", "Lasix", 0, "[]"),
        (r1_id, "Braida (FR)", 6, "Vincent Cheminaud", "Francis-Henri Graffard", 121, 8.0, "", "", 1, "[]"),
        (r1_id, "Storm's Wake", 7, "Tyler Gaffalione", "Brian Lynch", 121, 10.0, "", "Lasix", 0, "[]"),
        (r1_id, "Lookin At Diamond", 8, "Julien Leparoux", "Leonard Powell", 121, 20.0, "", "Lasix", 0, "[]"),
        (r1_id, "Kensington Lane (IRE)", 9, "Joel Rosario", "Phil D'Amato", 121, 8.0, "", "Lasix", 1, json.dumps([{"date": "2026-10-04", "distance_furlongs": 5.0, "time_seconds": 59.80, "workout_type": "H", "rank": 3, "total_workers": 42}])),
        (r1_id, "Deep Learning", 10, "Flavien Prat", "Chad Brown", 121, 12.0, "", "Lasix", 1, json.dumps([{"date": "2026-10-05", "distance_furlongs": 4.0, "time_seconds": 48.00, "workout_type": "B", "rank": 4, "total_workers": 60}])),
        (r1_id, "Soloist", 11, "Irad Ortiz Jr.", "Kenny McPeek", 121, 20.0, "Blinkers OFF", "Lasix", 1, "[]"),
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO today_entries (race_id, horse_name, post_position, jockey, trainer, weight, morning_line_odds, equipment, medication, jockey_change, workouts_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, r1_entries)

    # Carreras previas para calibrar KEE R9
    past_races_r1 = [
        ("WO_20260823_R10", "Luster", 1, "John Velazquez", "Josie Carroll", 121, 1, 0.0, 108.40, 23.20, 46.80, 96.5, 3.2),
        ("SAR_20260822_R09", "Faithful Departed", 3, "Jose Ortiz", "Grant Forster", 121, 1, 0.0, 108.10, 23.50, 47.10, 98.0, 4.0),
        ("SAR_20260822_R09", "Tam Tam", 5, "Junior Alvarado", "Phil Bauer", 121, 2, 0.5, 108.20, 23.10, 46.20, 97.2, 5.0),
        ("DMR_20260901_R07", "Kensington Lane (IRE)", 2, "Joel Rosario", "Phil D'Amato", 121, 1, 0.0, 108.30, 23.70, 47.40, 95.8, 4.5),
        ("SAR_20260902_R06", "Deep Learning", 4, "Flavien Prat", "Chad Brown", 121, 2, 1.0, 108.50, 24.00, 47.90, 94.0, 6.0),
    ]
    for pr in past_races_r1:
        rid, h, p, j, t, w, fin, marg, f_time, f2, f4, spd, odds = pr
        cursor.execute("INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status) VALUES (?, 'SAR', '2026-08-22', 9, 9.0, 'T', 'FM', 'STK', 300000, 'OFFICIAL')", (rid,))
        cursor.execute("""
            INSERT OR REPLACE INTO race_results (race_id, horse_name, post_position, jockey, trainer, weight_carried, finish_position, lengths_behind, final_time_sec, fractional_2f_sec, fractional_4f_sec, speed_rating, official_odds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, pr)

    # -------------------------------------------------------------
    # CARRERA 2: SANTA ANITA - CARRERA 9 (California Flag Handicap)
    # 6.5 Furlongs en Grama (Hillside Turf Course), Bolsa $100,000
    # -------------------------------------------------------------
    r2_id = "SA_20261010_R09"
    cursor.execute("""
        INSERT OR REPLACE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, rail_distance_feet, status)
        VALUES (?, 'SA', '2026-10-10', 9, 6.5, 'T', 'FM', 'STK - California Flag Handicap', 100000, 0, 'SCHEDULED')
    """, (r2_id,))

    r2_entries = [
        (r2_id, "Lonesome Stew", 1, "Umberto Rispoli", "Mark Glatt", 124, 1.2, "", "Lasix", 0, json.dumps([{"date": "2026-10-04", "distance_furlongs": 4.0, "time_seconds": 47.40, "workout_type": "B", "rank": 1, "total_workers": 62}])),
        (r2_id, "Big City Lights", 2, "Kazushi Kimura", "Richard Mandella", 126, 3.5, "", "Lasix", 0, json.dumps([{"date": "2026-10-03", "distance_furlongs": 5.0, "time_seconds": 59.40, "workout_type": "H", "rank": 2, "total_workers": 40}])),
        (r2_id, "Flyover", 3, "Hector Berrios", "John W. Sadler", 119, 6.0, "Blinkers ON", "Lasix", 0, "[]"),
        (r2_id, "On the Whim", 4, "Diego Herrera", "Dean Pederson", 121, 8.0, "", "Lasix", 0, "[]"),
        (r2_id, "Boss Sully", 5, "Edwin Maldonado", "Brian Koriner", 120, 10.0, "", "Lasix", 0, "[]"),
        (r2_id, "Steak Fries", 6, "Tiago Pereira", "Craig Anthony Lewis", 118, 15.0, "", "Lasix", 0, "[]"),
        (r2_id, "Chromeflash", 7, "Armando Ayuso", "Paula Capestro", 116, 20.0, "", "Lasix", 0, "[]"),
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO today_entries (race_id, horse_name, post_position, jockey, trainer, weight, morning_line_odds, equipment, medication, jockey_change, workouts_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, r2_entries)

    past_races_r2 = [
        ("DMR_20260825_R07", "Lonesome Stew", 2, "Umberto Rispoli", "Mark Glatt", 124, 1, 0.0, 74.20, 22.10, 44.50, 99.5, 2.1),
        ("DMR_20260825_R07", "Big City Lights", 5, "Kazushi Kimura", "Richard Mandella", 124, 2, 0.75, 74.35, 22.00, 44.30, 98.2, 3.0),
        ("DMR_20260810_R06", "On the Whim", 3, "Diego Herrera", "Dean Pederson", 121, 3, 2.0, 74.60, 22.80, 45.20, 94.0, 7.5),
        ("DMR_20260810_R06", "Flyover", 6, "Hector Berrios", "John W. Sadler", 119, 4, 3.5, 74.90, 22.40, 45.00, 92.5, 9.0),
    ]
    for pr in past_races_r2:
        rid, h, p, j, t, w, fin, marg, f_time, f2, f4, spd, odds = pr
        cursor.execute("INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status) VALUES (?, 'DMR', '2026-08-25', 7, 6.5, 'T', 'FM', 'STK', 100000, 'OFFICIAL')", (rid,))
        cursor.execute("""
            INSERT OR REPLACE INTO race_results (race_id, horse_name, post_position, jockey, trainer, weight_carried, finish_position, lengths_behind, final_time_sec, fractional_2f_sec, fractional_4f_sec, speed_rating, official_odds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, pr)

    # -------------------------------------------------------------
    # CARRERA 3: BELMONT AT THE BIG A (AQUEDUCT) - CARRERA 8 (G2 Sands Point)
    # 9.0 Furlongs en Grama (Turf), Bolsa $200,000
    # -------------------------------------------------------------
    r3_id = "BAQ_20261010_R08"
    cursor.execute("""
        INSERT OR REPLACE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, rail_distance_feet, status)
        VALUES (?, 'BAQ', '2026-10-10', 8, 9.0, 'T', 'FM', 'G2 - Sands Point Stakes', 200000, 9, 'SCHEDULED')
    """, (r3_id,))

    r3_entries = [
        (r3_id, "Style Points", 1, "Manuel Franco", "Christophe Clement", 120, 2.0, "", "Lasix", 0, json.dumps([{"date": "2026-10-04", "distance_furlongs": 4.0, "time_seconds": 47.90, "workout_type": "B", "rank": 2, "total_workers": 55}])),
        (r3_id, "Macanga", 2, "Dylan Davis", "Cherie DeVaux", 120, 3.5, "", "Lasix", 0, "[]"),
        (r3_id, "Dynamic Pricing (IRE)", 3, "Irad Ortiz Jr.", "Chad Brown", 122, 4.0, "", "Lasix", 1, json.dumps([{"date": "2026-10-03", "distance_furlongs": 4.0, "time_seconds": 48.10, "workout_type": "B", "rank": 4, "total_workers": 48}])),
        (r3_id, "Proctor Street", 4, "Flavien Prat", "Brendan Walsh", 118, 6.0, "", "Lasix", 0, "[]"),
        (r3_id, "Spalding", 5, "Junior Alvarado", "Bill Mott", 118, 8.0, "Blinkers ON", "Lasix", 0, "[]"),
        (r3_id, "Just a Head", 6, "Trevor McCarthy", "David Donk", 118, 15.0, "", "Lasix", 0, "[]"),
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO today_entries (race_id, horse_name, post_position, jockey, trainer, weight, morning_line_odds, equipment, medication, jockey_change, workouts_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, r3_entries)

    past_races_r3 = [
        ("SAR_20260815_R08", "Style Points", 2, "Manuel Franco", "Christophe Clement", 120, 1, 0.0, 108.20, 23.40, 47.10, 97.5, 2.5),
        ("SAR_20260815_R08", "Dynamic Pricing (IRE)", 4, "Irad Ortiz Jr.", "Chad Brown", 122, 2, 0.5, 108.30, 23.80, 47.60, 96.8, 3.0),
        ("SAR_20260815_R08", "Macanga", 1, "Dylan Davis", "Cherie DeVaux", 120, 3, 2.0, 108.60, 23.00, 46.40, 95.0, 5.0),
        ("SAR_20260720_R07", "Proctor Street", 3, "Flavien Prat", "Brendan Walsh", 118, 1, 0.0, 108.50, 23.90, 47.80, 94.2, 4.2),
    ]
    for pr in past_races_r3:
        rid, h, p, j, t, w, fin, marg, f_time, f2, f4, spd, odds = pr
        cursor.execute("INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status) VALUES (?, 'SAR', '2026-08-15', 8, 9.0, 'T', 'FM', 'STK', 175000, 'OFFICIAL')", (rid,))
        cursor.execute("""
            INSERT OR REPLACE INTO race_results (race_id, horse_name, post_position, jockey, trainer, weight_carried, finish_position, lengths_behind, final_time_sec, fractional_2f_sec, fractional_4f_sec, speed_rating, official_odds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, pr)

    # -------------------------------------------------------------
    # CARRERA 4: KEENELAND - CARRERA 7 (Allowance Sprint $110,000)
    # 6.0 Furlongs en Arena (Dirt), Bolsa $110,000
    # -------------------------------------------------------------
    r4_id = "KEE_20261010_R07"
    cursor.execute("""
        INSERT OR REPLACE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, rail_distance_feet, status)
        VALUES (?, 'KEE', '2026-10-10', 7, 6.0, 'D', 'FT', 'AOC - Allowance Optional Claiming', 110000, 0, 'SCHEDULED')
    """, (r4_id,))

    r4_entries = [
        (r4_id, "Valentine Candy", 1, "Ricardo Santana Jr.", "Steve Asmussen", 122, 1.8, "", "Lasix", 0, json.dumps([{"date": "2026-10-04", "distance_furlongs": 4.0, "time_seconds": 47.10, "workout_type": "B", "rank": 1, "total_workers": 75}])),
        (r4_id, "Barksdale", 2, "Tyler Gaffalione", "William Walden", 120, 4.0, "", "Lasix", 0, "[]"),
        (r4_id, "Carbone", 3, "Keith Asmussen", "Steve Asmussen", 120, 5.0, "", "Lasix", 0, "[]"),
        (r4_id, "Scatify", 4, "Irad Ortiz Jr.", "John Sadler", 120, 6.0, "Blinkers ON", "Lasix", 1, json.dumps([{"date": "2026-10-03", "distance_furlongs": 4.0, "time_seconds": 48.00, "workout_type": "B", "rank": 3, "total_workers": 60}])),
        (r4_id, "Be You", 5, "Jose Ortiz", "Norm Casse", 120, 8.0, "", "Lasix", 0, "[]"),
        (r4_id, "Informed Patriot", 6, "Joel Rosario", "Steve Asmussen", 120, 10.0, "", "Lasix", 0, "[]"),
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO today_entries (race_id, horse_name, post_position, jockey, trainer, weight, morning_line_odds, equipment, medication, jockey_change, workouts_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, r4_entries)

    past_races_r4 = [
        ("SAR_20260824_R05", "Valentine Candy", 3, "Ricardo Santana Jr.", "Steve Asmussen", 122, 1, 0.0, 69.80, 22.00, 44.70, 97.2, 2.0),
        ("SAR_20260824_R05", "Barksdale", 1, "Tyler Gaffalione", "William Walden", 120, 2, 1.5, 70.10, 22.20, 45.00, 95.0, 3.5),
        ("CD_20260620_R07", "Scatify", 2, "Irad Ortiz Jr.", "John Sadler", 120, 1, 0.0, 69.90, 22.10, 44.80, 96.5, 4.5),
        ("CD_20260620_R07", "Carbone", 4, "Keith Asmussen", "Steve Asmussen", 120, 3, 2.5, 70.40, 22.30, 45.20, 93.8, 5.0),
    ]
    for pr in past_races_r4:
        rid, h, p, j, t, w, fin, marg, f_time, f2, f4, spd, odds = pr
        cursor.execute("INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status) VALUES (?, 'SAR', '2026-08-24', 5, 6.0, 'D', 'FT', 'STK', 150000, 'OFFICIAL')", (rid,))
        cursor.execute("""
            INSERT OR REPLACE INTO race_results (race_id, horse_name, post_position, jockey, trainer, weight_carried, finish_position, lengths_behind, final_time_sec, fractional_2f_sec, fractional_4f_sec, speed_rating, official_odds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, pr)

    # -------------------------------------------------------------
    # CARRERA 5: GULFSTREAM PARK - CARRERA 7 (The Chasing Artie Handicap)
    # 5.0 Furlongs en Grama (Turf Sprint), Bolsa $60,000
    # -------------------------------------------------------------
    r5_id = "GP_20261010_R07"
    cursor.execute("""
        INSERT OR REPLACE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, rail_distance_feet, status)
        VALUES (?, 'GP', '2026-10-10', 7, 5.0, 'T', 'FM', 'STK - The Chasing Artie Handicap', 60000, 10, 'SCHEDULED')
    """, (r5_id,))

    r5_entries = [
        (r5_id, "Full Disclosure", 1, "Marcos Meneses", "Aditi Jehaludi", 118, 12.0, "", "Lasix", 0, "[]"),
        (r5_id, "Extendo", 2, "Edwin Gonzalez", "Joseph Orseno", 120, 6.0, "", "Lasix", 0, "[]"),
        (r5_id, "Esperon", 3, "Diego Herrera", "J. David Braddy", 119, 8.0, "", "Lasix", 0, "[]"),
        (r5_id, "Axthelm", 4, "Miguel Vasquez", "Bobby Dibona", 121, 5.0, "", "Lasix", 0, "[]"),
        (r5_id, "Itza Boss", 5, "Leonel Reyes", "Jose F. D'Angelo", 118, 10.0, "", "Lasix", 0, "[]"),
        (r5_id, "Rouki", 6, "Samy Camacho", "Gerald Bennett", 116, 15.0, "", "Lasix", 0, "[]"),
        (r5_id, "Souper Quest", 7, "Sonny Leon", "Mark Casse", 124, 2.5, "", "Lasix", 0, json.dumps([{"date": "2026-10-04", "distance_furlongs": 4.0, "time_seconds": 46.80, "workout_type": "B", "rank": 1, "total_workers": 45}])),
        (r5_id, "Naughty Rascal", 8, "J.G. Ocasio", "Gerald Bennett", 116, 20.0, "", "Lasix", 0, "[]"),
        (r5_id, "Mattingly", 9, "Fernando De La Cruz", "Joseph Orseno", 122, 3.0, "", "Lasix", 0, json.dumps([{"date": "2026-10-03", "distance_furlongs": 4.0, "time_seconds": 47.30, "workout_type": "B", "rank": 2, "total_workers": 40}])),
        (r5_id, "Guns Loaded", 10, "M. Husbands", "Saffie Joseph Jr.", 119, 8.0, "Blinkers ON", "Lasix", 0, "[]"),
        (r5_id, "Three Zero", 11, "Nik Juarez", "Carlos David", 118, 12.0, "", "Lasix", 0, "[]"),
        (r5_id, "Ajaayb", 12, "Jose Morelos", "Juan Arias", 116, 15.0, "", "Lasix", 0, "[]"),
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO today_entries (race_id, horse_name, post_position, jockey, trainer, weight, morning_line_odds, equipment, medication, jockey_change, workouts_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, r5_entries)

    past_races_r5 = [
        ("WO_20260810_R06", "Souper Quest", 4, "Sonny Leon", "Mark Casse", 124, 1, 0.0, 55.40, 21.80, 44.20, 99.0, 2.2),
        ("GP_20260905_R07", "Mattingly", 2, "Fernando De La Cruz", "Joseph Orseno", 122, 1, 0.0, 55.60, 21.90, 44.40, 98.2, 2.8),
        ("GP_20260905_R07", "Axthelm", 5, "Miguel Vasquez", "Bobby Dibona", 121, 2, 0.5, 55.70, 22.10, 44.60, 96.5, 4.5),
        ("GP_20260905_R07", "Extendo", 1, "Edwin Gonzalez", "Joseph Orseno", 120, 3, 1.25, 55.85, 22.00, 44.50, 95.0, 5.0),
    ]
    for pr in past_races_r5:
        rid, h, p, j, t, w, fin, marg, f_time, f2, f4, spd, odds = pr
        cursor.execute("INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status) VALUES (?, 'GP', '2026-09-05', 7, 5.0, 'T', 'FM', 'STK', 60000, 'OFFICIAL')", (rid,))
        cursor.execute("""
            INSERT OR REPLACE INTO race_results (race_id, horse_name, post_position, jockey, trainer, weight_carried, finish_position, lengths_behind, final_time_sec, fractional_2f_sec, fractional_4f_sec, speed_rating, official_odds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, pr)

    # -------------------------------------------------------------
    # CARRERA 6: GULFSTREAM PARK - CARRERA 10 (The Daring Kathy Handicap)
    # 8.5 Furlongs en Grama (Turf), Bolsa $60,000 (Yeguas 3yo+)
    # -------------------------------------------------------------
    r6_id = "GP_20261010_R10"
    cursor.execute("""
        INSERT OR REPLACE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, rail_distance_feet, status)
        VALUES (?, 'GP', '2026-10-10', 10, 8.5, 'T', 'FM', 'STK - The Daring Kathy Handicap', 60000, 10, 'SCHEDULED')
    """, (r6_id,))

    r6_entries = [
        (r6_id, "Hello Hello Hello", 1, "M. Husbands", "Saffie Joseph Jr.", 118, 8.0, "", "Lasix", 0, "[]"),
        (r6_id, "Turino", 2, "R. Hughes", "Saffie Joseph Jr.", 119, 6.0, "", "Lasix", 0, "[]"),
        (r6_id, "Oshala", 3, "Heriberto Figueroa", "Nader Moubarak", 117, 12.0, "", "Lasix", 0, "[]"),
        (r6_id, "Souper Zonda", 4, "Sonny Leon", "Mark Casse", 123, 2.5, "", "Lasix", 0, json.dumps([{"date": "2026-10-04", "distance_furlongs": 4.0, "time_seconds": 47.90, "workout_type": "B", "rank": 2, "total_workers": 45}])),
        (r6_id, "Defiant Lass", 5, "Samy Camacho", "James Toner", 118, 8.0, "", "Lasix", 0, "[]"),
        (r6_id, "Miss Mary Nell", 6, "J.G. Ocasio", "Carlos David", 118, 10.0, "", "Lasix", 0, "[]"),
        (r6_id, "Crafty Collector", 7, "Marcos Meneses", "Gerald Bennett", 116, 15.0, "", "Lasix", 0, "[]"),
        (r6_id, "Lets Go Koko", 8, "Edwin Gonzalez", "Ronnie Miller", 119, 8.0, "", "Lasix", 0, "[]"),
        (r6_id, "Vincey Girl", 9, "Leonel Reyes", "Jose F. D'Angelo", 121, 3.5, "Blinkers ON", "Lasix", 0, json.dumps([{"date": "2026-10-03", "distance_furlongs": 5.0, "time_seconds": 59.90, "workout_type": "H", "rank": 1, "total_workers": 38}])),
        (r6_id, "Fantasy Performer", 10, "Miguel Vasquez", "Cam Gambolati", 120, 5.0, "", "Lasix", 0, "[]"),
        (r6_id, "Janana Han", 11, "Y. Torres", "Garth Rangel", 114, 20.0, "", "Lasix", 0, "[]"),
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO today_entries (race_id, horse_name, post_position, jockey, trainer, weight, morning_line_odds, equipment, medication, jockey_change, workouts_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, r6_entries)

    past_races_r6 = [
        ("GP_20260822_R08", "Souper Zonda", 3, "Sonny Leon", "Mark Casse", 123, 1, 0.0, 101.50, 23.40, 47.20, 96.8, 2.2),
        ("GP_20260822_R08", "Vincey Girl", 5, "Leonel Reyes", "Jose F. D'Angelo", 121, 2, 0.75, 101.65, 23.60, 47.50, 95.5, 3.8),
        ("GP_20260822_R08", "Fantasy Performer", 2, "Miguel Vasquez", "Cam Gambolati", 120, 3, 1.5, 101.80, 23.20, 46.90, 94.2, 5.5),
    ]
    for pr in past_races_r6:
        rid, h, p, j, t, w, fin, marg, f_time, f2, f4, spd, odds = pr
        cursor.execute("INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status) VALUES (?, 'GP', '2026-08-22', 8, 8.5, 'T', 'FM', 'STK', 60000, 'OFFICIAL')", (rid,))
        cursor.execute("""
            INSERT OR REPLACE INTO race_results (race_id, horse_name, post_position, jockey, trainer, weight_carried, finish_position, lengths_behind, final_time_sec, fractional_2f_sec, fractional_4f_sec, speed_rating, official_odds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, pr)

    conn.commit()
    conn.close()

    # 2. EJECUTAR EL MOTOR Y GUARDAR EN PREDICTIONS_AUDIT
    today_race_ids = [r1_id, r2_id, r3_id, r4_id, r5_id, r6_id]
    audit_results = []

    conn = get_db_connection()
    cursor = conn.cursor()

    for r_id in today_race_ids:
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

        # Guardar en predictions_audit
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

        audit_results.append({
            "race_id": r_id,
            "track": race["track"],
            "race_number": race["race_number"],
            "race_class": race["race_class"],
            "top_pick": f"#{top['post_position']} {top['horse_name']}",
            "top_odds": top["morning_line_odds"],
            "top_score": top["composite_score"],
            "value_pick": f"#{val['post_position']} {val['horse_name']}" if val else "N/A",
            "value_odds": val["morning_line_odds"] if val else "N/A",
            "pace_scenario": pace["scenario"],
            "exacta": exacta_str
        })

    conn.commit()
    conn.close()
    return audit_results


if __name__ == "__main__":
    results = populate_and_predict_today()
    print("Predicciones de hoy registradas y guardadas para auditoria:")
    for r in results:
        print(f"[{r['track']} R{r['race_number']}] TOP: {r['top_pick']} ({r['top_odds']}-1) | VALOR: {r['value_pick']} | RITMO: {r['pace_scenario']}")
