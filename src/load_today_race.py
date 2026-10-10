"""
Carga la carrera real de hoy (Viernes 09 de Octubre de 2026) en Santa Anita Park:
Carrera #8 (6.5 Furlongs en Arena, 2 años Maiden Optional Claiming, Bolsa $54,000)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection, init_database
from src.speed_figures import calculate_speed_rating

def load_october_9_race():
    init_database()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Hipódromo
    cursor.execute("INSERT OR IGNORE INTO tracks (code, name, state, country) VALUES ('SA', 'Santa Anita Park', 'CA', 'USA')")
    cursor.execute("INSERT OR IGNORE INTO tracks (code, name, state, country) VALUES ('DMR', 'Del Mar', 'CA', 'USA')")
    cursor.execute("INSERT OR IGNORE INTO tracks (code, name, state, country) VALUES ('LRC', 'Los Alamitos', 'CA', 'USA')")

    # Carrera de hoy 09 de Octubre: Carrera 8
    race_id = "SA_20261009_R08"
    cursor.execute("""
        INSERT OR REPLACE INTO races (
            race_id, track, race_date, race_number, distance_furlongs, 
            surface, track_condition, race_class, purse, status
        ) VALUES (
            ?, 'SA', '2026-10-09', 8, 6.5, 
            'D', 'FT', 'MOC - Maiden Optional Claiming (2yo)', 54000, 'SCHEDULED'
        )
    """, (race_id,))

    # Contendientes oficiales de la Carrera 8 de Santa Anita
    entries = [
        (race_id, "Fractious", 1, "Joel Rosario", "Doug O'Neill", 122, 2.5),
        (race_id, "Grand Indian", 2, "Kyle Frey", "Adam Kitchingman", 122, 10.0),
        (race_id, "Franciscus", 3, "Kazushi Kimura", "Tim Yakteen", 122, 4.5),
        (race_id, "At Peace", 4, "Mike E. Smith", "Richard Mandella", 122, 5.0),
        (race_id, "Nomorebuttafingers", 5, "Drayden Van Dyke", "Richard Baltas", 122, 12.0),
        (race_id, "Boss Man Bolt", 6, "Armando Ayuso", "Mick Ruis Sr.", 122, 6.0),
        (race_id, "Iron Sand", 7, "Juan Hernandez", "Sean Williams", 122, 8.0),
        (race_id, "Magic Wave", 8, "Tiago Pereira", "Hector Palma", 122, 2.8),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO today_entries (
            race_id, horse_name, post_position, jockey, trainer, weight, morning_line_odds
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, entries)

    # Carreras previas oficiales de los que no son debutantes:
    # 1. Carrera previa de Fractious en Del Mar (05 Sep 2026, 6f Dirt FT, 2º a 3.25 cpos, tiempo 70.80s)
    prev_r1 = "DMR_20260905_R04"
    cursor.execute("""
        INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status)
        VALUES (?, 'DMR', '2026-09-05', 4, 6.0, 'D', 'FT', 'MOC', 50000, 'OFFICIAL')
    """, (prev_r1,))
    spd_fractious = calculate_speed_rating(70.80, 6.0, 'D', 'FT', lengths_behind=3.25, weight_carried=120)
    cursor.execute("""
        INSERT OR REPLACE INTO race_results (
            race_id, horse_name, post_position, jockey, trainer, weight_carried,
            finish_position, lengths_behind, final_time_sec, fractional_2f_sec, fractional_4f_sec, speed_rating, official_odds
        ) VALUES (?, 'Fractious', 3, 'Abel Lezcano', "Doug O'Neill", 120, 2, 3.25, 70.80, 22.30, 45.40, ?, 3.4)
    """, (prev_r1, spd_fractious))

    # 2. Carrera previa de Magic Wave en Los Alamitos (14 Sep 2026, 5.5f Dirt FT, 2º a 2.0 cpos, tiempo 64.60s)
    prev_r2 = "LRC_20260914_R03"
    cursor.execute("""
        INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status)
        VALUES (?, 'LRC', '2026-09-14', 3, 5.5, 'D', 'FT', 'MSW', 45000, 'OFFICIAL')
    """, (prev_r2,))
    spd_magic = calculate_speed_rating(64.60, 5.5, 'D', 'FT', lengths_behind=2.0, weight_carried=122)
    cursor.execute("""
        INSERT OR REPLACE INTO race_results (
            race_id, horse_name, post_position, jockey, trainer, weight_carried,
            finish_position, lengths_behind, final_time_sec, fractional_2f_sec, fractional_4f_sec, speed_rating, official_odds
        ) VALUES (?, 'Magic Wave', 5, 'Tiago Pereira', 'Hector Palma', 122, 2, 2.0, 64.60, 21.90, 44.80, ?, 2.6)
    """, (prev_r2, spd_magic))

    # 3. Carrera previa de Boss Man Bolt (Del Mar 24 Ago 2026, 5.5f Dirt FT, 4º a 5.0 cpos, tiempo 65.40s)
    prev_r3 = "DMR_20260824_R02"
    cursor.execute("""
        INSERT OR IGNORE INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status)
        VALUES (?, 'DMR', '2026-08-24', 2, 5.5, 'D', 'FT', 'MCL', 35000, 'OFFICIAL')
    """, (prev_r3,))
    spd_boss = calculate_speed_rating(65.40, 5.5, 'D', 'FT', lengths_behind=5.0, weight_carried=120)
    cursor.execute("""
        INSERT OR REPLACE INTO race_results (
            race_id, horse_name, post_position, jockey, trainer, weight_carried,
            finish_position, lengths_behind, final_time_sec, fractional_2f_sec, fractional_4f_sec, speed_rating, official_odds
        ) VALUES (?, 'Boss Man Bolt', 2, 'Armando Ayuso', 'Mick Ruis Sr.', 120, 4, 5.0, 65.40, 22.40, 45.90, ?, 8.0)
    """, (prev_r3, spd_boss))

    # Estadísticas históricas de conexiones en el circuito californiano:
    # Joel Rosario + Doug O'Neill, Mike Smith + Richard Mandella, Juan Hernandez, Tiago Pereira
    cursor.execute("""
        INSERT OR REPLACE INTO race_results (race_id, horse_name, jockey, trainer, finish_position)
        VALUES ('DMR_20260905_R04', 'Dummy1', 'Joel Rosario', "Doug O'Neill", 1),
               ('DMR_20260905_R04', 'Dummy2', 'Mike E. Smith', 'Richard Mandella', 1),
               ('DMR_20260905_R04', 'Dummy3', 'Juan Hernandez', 'Sean Williams', 2),
               ('DMR_20260905_R04', 'Dummy4', 'Kazushi Kimura', 'Tim Yakteen', 2)
    """)

    conn.commit()
    conn.close()
    print("Carrera del 09 de Octubre cargada con éxito: SA_20261009_R08")

if __name__ == "__main__":
    load_october_9_race()
