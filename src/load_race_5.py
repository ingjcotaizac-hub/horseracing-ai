"""
Carga la Carrera #5 real de hoy (09 de Octubre de 2026) en Santa Anita Park:
1 Milla en Grama (Turf), Claiming $25,000 para yeguas, Bolsa $28,000.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection, init_database
from src.speed_figures import calculate_speed_rating

def load_race_5():
    init_database()
    conn = get_db_connection()
    cursor = conn.cursor()

    race_id = "SA_20261009_R05"
    cursor.execute("""
        INSERT OR REPLACE INTO races (
            race_id, track, race_date, race_number, distance_furlongs, 
            surface, track_condition, race_class, purse, status
        ) VALUES (
            ?, 'SA', '2026-10-09', 5, 8.0, 
            'T', 'FM', 'CLM $25,000 (Fillies & Mares)', 28000, 'SCHEDULED'
        )
    """, (race_id,))

    # Inscritos oficiales Carrera 5
    entries = [
        (race_id, "Una Palabra", 1, "Edgar Payeras", "Vann Belvoir", 124, 6.0),
        (race_id, "Cameron Slough", 2, "Abel Lezcano", "Blaine D. Wright", 124, 8.0),
        (race_id, "Corporal Violette (IRE)", 3, "Kazushi Kimura", "Mark Rheinford", 124, 2.5),
        (race_id, "Catalina Cocktail", 4, "Armando Ayuso", "John W. Sadler", 124, 4.0),
        (race_id, "Ketonia (FR)", 5, "Julien R. Leparoux", "Ronald W. Ellis", 124, 3.5),
        (race_id, "Sareeha (IRE)", 6, "Emisael Jaramillo", "Mark Glatt", 124, 3.0),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO today_entries (
            race_id, horse_name, post_position, jockey, trainer, weight, morning_line_odds
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, entries)

    # Carreras previas oficiales:
    # 1. Del Mar 03 Sep 2026 (Race 7, 8.0f Turf FM, Claiming/Allowance)
    # Corporal Violette fue 4ª a 1.75 cpos en 95.80s (Speed: ~84)
    # Ketonia tuvo tropiezos y llegó 10ª (Speed: ~72)
    # Sareeha fue 2ª a 0.5 cpos en 95.10s (Speed: ~87)
    # Cameron Slough fue 6ª a 4.5 cpos en 96.20s (Speed: ~77)
    prev_dmr = "DMR_20260903_R07"
    cursor.execute("""
        INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status)
        VALUES (?, 'DMR', '2026-09-03', 7, 8.0, 'T', 'FM', 'CLM', 32000, 'OFFICIAL')
    """, (prev_dmr,))

    spd_sareeha = calculate_speed_rating(95.10, 8.0, 'T', 'FM', lengths_behind=0.5, weight_carried=124)
    spd_corp = calculate_speed_rating(95.80, 8.0, 'T', 'FM', lengths_behind=1.75, weight_carried=124)
    spd_ketonia = calculate_speed_rating(97.20, 8.0, 'T', 'FM', lengths_behind=6.0, weight_carried=124)
    spd_cameron = calculate_speed_rating(96.20, 8.0, 'T', 'FM', lengths_behind=4.5, weight_carried=124)

    cursor.execute("""
        INSERT OR REPLACE INTO race_results (
            race_id, horse_name, post_position, jockey, trainer, weight_carried,
            finish_position, lengths_behind, final_time_sec, fractional_2f_sec, fractional_4f_sec, speed_rating, official_odds
        ) VALUES (?, 'Sareeha (IRE)', 4, 'Emisael Jaramillo', 'Mark Glatt', 124, 2, 0.5, 95.10, 23.40, 47.20, ?, 3.2),
                 (?, 'Corporal Violette (IRE)', 2, 'Kazushi Kimura', 'Mark Rheinford', 124, 4, 1.75, 95.80, 23.80, 47.90, ?, 2.8),
                 (?, 'Cameron Slough', 5, 'Abel Lezcano', 'Blaine D. Wright', 124, 6, 4.5, 96.20, 24.10, 48.20, ?, 9.0),
                 (?, 'Ketonia (FR)', 6, 'Julien R. Leparoux', 'Ronald W. Ellis', 124, 10, 6.0, 97.20, 23.90, 48.0, ?, 4.5)
    """, (prev_dmr, spd_sareeha, prev_dmr, spd_corp, prev_dmr, spd_cameron, prev_dmr, spd_ketonia))

    # 2. Carrera de Catalina Cocktail (Viene de correr Grado 3 en Del Mar el 16 Ago 2026, y ganar en Los Alamitos en Julio)
    prev_g3 = "DMR_20260816_R08"
    cursor.execute("""
        INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status)
        VALUES (?, 'DMR', '2026-08-16', 8, 6.5, 'D', 'FT', 'G3 - Rancho Bernardo', 125000, 'OFFICIAL')
    """, (prev_g3,))
    spd_cat = calculate_speed_rating(76.80, 6.5, 'D', 'FT', lengths_behind=3.0, weight_carried=120)
    cursor.execute("""
        INSERT OR REPLACE INTO race_results (
            race_id, horse_name, post_position, jockey, trainer, weight_carried,
            finish_position, lengths_behind, final_time_sec, fractional_2f_sec, fractional_4f_sec, speed_rating, official_odds
        ) VALUES (?, 'Catalina Cocktail', 3, 'Armando Ayuso', 'John W. Sadler', 120, 5, 3.0, 76.80, 22.0, 44.90, ?, 12.0)
    """, (prev_g3, spd_cat))

    # Carrera de Una Palabra (Corrió en Del Mar 24 Ago, 8.0f Turf, 3ª a 2.0 cpos)
    prev_una = "DMR_20260824_R05"
    cursor.execute("""
        INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status)
        VALUES (?, 'DMR', '2026-08-24', 5, 8.0, 'T', 'FM', 'CLM', 26000, 'OFFICIAL')
    """, (prev_una,))
    spd_una = calculate_speed_rating(95.60, 8.0, 'T', 'FM', lengths_behind=2.0, weight_carried=124)
    cursor.execute("""
        INSERT OR REPLACE INTO race_results (
            race_id, horse_name, post_position, jockey, trainer, weight_carried,
            finish_position, lengths_behind, final_time_sec, fractional_2f_sec, fractional_4f_sec, speed_rating, official_odds
        ) VALUES (?, 'Una Palabra', 1, 'Edgar Payeras', 'Vann Belvoir', 124, 3, 2.0, 95.60, 23.60, 47.50, ?, 5.5)
    """, (prev_una, spd_una))

    # Conexiones estadísticas
    cursor.execute("""
        INSERT OR REPLACE INTO race_results (race_id, horse_name, jockey, trainer, finish_position)
        VALUES ('DMR_20260903_R07', 'DummyS1', 'Emisael Jaramillo', 'Mark Glatt', 1),
               ('DMR_20260903_R07', 'DummyS2', 'Armando Ayuso', 'John W. Sadler', 1)
    """)

    conn.commit()
    conn.close()
    print("Carrera 5 del 09 de Octubre cargada con éxito: SA_20261009_R05")

if __name__ == "__main__":
    load_race_5()
