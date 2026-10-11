"""
Motor de Features y Extracción de Past Performances Avanzado.
Calcula el perfil analítico completo integrando:
- Speed Figures normalizados
- Proyección táctica de Ritmo (Pace Dynamics: Lone Speed vs Pace Meltdown)
- Aprontes y Ejercicios Previos (Workouts & Bullet detection)
- Aperos y Medicación (Blinkers ON/OFF, Lasix)
- Sesgo de Pista y Baranda (Track Bias & Rail placement)
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection
from src.pace_engine import project_race_pace, compute_pace_adjustment
from src.workouts import evaluate_workouts
from src.equipment_bias import evaluate_equipment_and_angles, evaluate_track_bias


def get_horse_past_performances(horse_name: str, before_date: str = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Recupera las últimas N carreras de un caballo antes de una fecha determinada."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            rr.*, 
            r.track, 
            r.race_date, 
            r.distance_furlongs, 
            r.surface, 
            r.track_condition, 
            r.race_class, 
            r.purse
        FROM race_results rr
        JOIN races r ON rr.race_id = r.race_id
        WHERE rr.horse_name = ?
    """
    params = [horse_name]

    if before_date:
        query += " AND r.race_date < ?"
        params.append(before_date)

    query += " ORDER BY r.race_date DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_connection_stats(name: str, role: str = 'jockey', sample_limit: int = 30) -> float:
    """Calcula el % de victorias reciente de un jinete o entrenador."""
    conn = get_db_connection()
    cursor = conn.cursor()
    col = "jockey" if role == "jockey" else "trainer"

    cursor.execute(f"""
        SELECT 
            COUNT(*) as total_starts,
            SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) as wins
        FROM race_results
        WHERE {col} = ?
        LIMIT ?
    """, (name, sample_limit))

    row = cursor.fetchone()
    conn.close()

    if not row or row["total_starts"] == 0:
        return 14.0  # Promedio estándar base
    return round((row["wins"] / row["total_starts"]) * 100.0, 1)


def compute_horse_profile(
    horse_name: str,
    target_race_date: str,
    target_distance: float,
    target_surface: str,
    target_jockey: str,
    target_trainer: str,
    post_position: int,
    morning_line_odds: float,
    equipment: str = "",
    medication: str = "",
    jockey_change: bool = False,
    workouts_data: List[Dict[str, Any]] = None,
    track_condition: str = "FT",
    rail_feet: int = 0,
    total_field: int = 8
) -> Dict[str, Any]:
    """Genera el vector de variables analíticas individuales (Features) de cada caballo."""
    pps = get_horse_past_performances(horse_name, before_date=target_race_date, limit=5)

    # 1. Días de descanso (Layoff)
    if pps:
        last_date = datetime.strptime(pps[0]["race_date"], "%Y-%m-%d")
        curr_date = datetime.strptime(target_race_date, "%Y-%m-%d")
        layoff_days = (curr_date - last_date).days
        is_second_off_layoff = len(pps) >= 2 and (
            (datetime.strptime(pps[0]["race_date"], "%Y-%m-%d") - datetime.strptime(pps[1]["race_date"], "%Y-%m-%d")).days > 90
        )
    else:
        layoff_days = 60
        is_second_off_layoff = False

    # 2. Speed Figures
    speeds = [p["speed_rating"] for p in pps if p.get("speed_rating")]
    if speeds:
        last_speed = speeds[0]
        best_speed = max(speeds)
        if len(speeds) >= 3:
            weighted_speed = (speeds[0] * 0.50) + (speeds[1] * 0.30) + (speeds[2] * 0.20)
        elif len(speeds) == 2:
            weighted_speed = (speeds[0] * 0.65) + (speeds[1] * 0.35)
        else:
            weighted_speed = speeds[0]
    else:
        # Debutante
        last_speed = 70.0
        weighted_speed = 70.0
        best_speed = 70.0

    # 3. Tendencia de Forma
    if len(speeds) >= 2:
        if speeds[0] > speeds[1] + 3:
            form_trend = "[+] SUBIENDO"
        elif speeds[0] < speeds[1] - 3:
            form_trend = "[-] BAJANDO"
        else:
            form_trend = "[=] ESTABLE"
    else:
        form_trend = "[*] PRIMERAS"

    # 4. Idoneidad de Pista y Superficie
    surface_runs = [p for p in pps if p.get("surface") == target_surface]
    surface_wins = sum(1 for p in surface_runs if p.get("finish_position") == 1)
    surface_suitability = (surface_wins / len(surface_runs)) if surface_runs else 0.20

    # 5. Idoneidad en Distancia
    dist_runs = [p for p in pps if abs(p.get("distance_furlongs", 0) - target_distance) <= 0.6]
    dist_wins = sum(1 for p in dist_runs if p.get("finish_position") == 1)
    dist_suitability = (dist_wins / len(dist_runs)) if dist_runs else 0.20

    # 6. Estadísticas de Conexiones
    jockey_win_pct = get_connection_stats(target_jockey, role='jockey')
    trainer_win_pct = get_connection_stats(target_trainer, role='trainer')

    # 7. Estilo de Carrera predominante (Pace Style)
    styles = []
    for p in pps:
        frac4 = p.get("fractional_4f_sec")
        final_t = p.get("final_time_sec")
        if frac4 and final_t:
            if p.get("lengths_behind", 99) <= 1.5:
                styles.append("E")
            elif p.get("lengths_behind", 99) <= 4.0:
                styles.append("P")
            else:
                styles.append("S")
    predominant_style = max(set(styles), key=styles.count) if styles else "P"

    # 8. Evaluación de Ejercicios Previos (Workouts & Bullet detection)
    workouts_eval = evaluate_workouts(workouts_data or [], target_race_date)

    # 9. Evaluación de Aperos y Ángulos (Blinkers ON, Lasix, etc.)
    angles_eval = evaluate_equipment_and_angles(
        equipment=equipment,
        medication=medication,
        jockey_change=jockey_change,
        is_second_start_off_layoff=is_second_off_layoff,
        is_maiden=(len(pps) == 0 or all(p.get("finish_position") != 1 for p in pps))
    )

    # 10. Sesgo de Pista y Baranda (Track Bias & Rail)
    bias_eval = evaluate_track_bias(
        post_position=post_position,
        total_field=total_field,
        surface=target_surface,
        distance_furlongs=target_distance,
        rail_feet=rail_feet,
        track_condition=track_condition
    )

    # 11. Puntuación Base Individual (Antes del ajuste de ritmo grupal)
    speed_factor = min(100.0, max(0.0, weighted_speed))
    connections_factor = min(100.0, (jockey_win_pct + trainer_win_pct) * 2.2)

    if 14 <= layoff_days <= 50:
        layoff_score = 95.0
    elif 51 <= layoff_days <= 90:
        layoff_score = 80.0
    elif layoff_days < 14:
        layoff_score = 65.0
    else:
        layoff_score = 50.0

    ml_factor = max(10.0, 100.0 - (morning_line_odds * 8.0))

    base_score = (
        (speed_factor * 0.40) +
        (workouts_eval["workout_score"] * 0.15) +
        (connections_factor * 0.15) +
        (layoff_score * 0.10) +
        (ml_factor * 0.10) +
        ((surface_suitability * 100.0) * 0.10) +
        angles_eval["equipment_score"] +
        bias_eval["bias_score"]
    )

    return {
        "horse_name": horse_name,
        "post_position": post_position,
        "morning_line_odds": morning_line_odds,
        "jockey": target_jockey,
        "jockey_win_pct": jockey_win_pct,
        "trainer": target_trainer,
        "trainer_win_pct": trainer_win_pct,
        "last_speed": round(last_speed, 1),
        "weighted_speed": round(weighted_speed, 1),
        "best_speed": round(best_speed, 1),
        "layoff_days": layoff_days,
        "form_trend": form_trend,
        "pace_style": predominant_style,
        "surface_record": f"{surface_wins}/{len(surface_runs)}",
        "dist_record": f"{dist_wins}/{len(dist_runs)}",
        "base_score": round(base_score, 1),
        "composite_score": round(base_score, 1), # Se ajustará en analyze_race_field
        "workout_score": workouts_eval["workout_score"],
        "has_bullet_workout": workouts_eval["has_bullet"],
        "workout_verdict": workouts_eval["condition_verdict"],
        "last_workout": workouts_eval["last_work_summary"],
        "equipment_flags": angles_eval["flags"],
        "bias_notes": bias_eval["bias_notes"],
        "past_performances": pps
    }


def analyze_race_field(race_id: str) -> Dict[str, Any]:
    """
    Realiza el análisis integral de toda la carrera:
    1. Extrae datos de la carrera y todos los inscritos
    2. Modela el ritmo de carrera esperado (Pace Projection)
    3. Bonifica/penaliza a cada ejemplar según la dinámica de la carrera
    4. Genera el ranking final, Top Pick, Valor (+EV) y Sorpresa (Longshot)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.*, t.name as track_name
        FROM races r
        JOIN tracks t ON r.track = t.code
        WHERE r.race_id = ?
    """, (race_id,))
    race = cursor.fetchone()

    if not race:
        conn.close()
        return {}

    cursor.execute("""
        SELECT * FROM today_entries
        WHERE race_id = ? AND (is_scratched = 0 OR is_scratched IS NULL)
        ORDER BY post_position ASC
    """, (race_id,))
    entries = cursor.fetchall()
    conn.close()

    if not entries:
        return {}

    total_field = len(entries)
    rail_feet = race["rail_distance_feet"] if "rail_distance_feet" in race.keys() and race["rail_distance_feet"] else 0

    # 1. Calcular perfiles individuales
    profiles = []
    for entry in entries:
        workouts_raw = []
        if "workouts_json" in entry.keys() and entry["workouts_json"]:
            try:
                workouts_raw = json.loads(entry["workouts_json"])
            except Exception:
                workouts_raw = []

        prof = compute_horse_profile(
            horse_name=entry["horse_name"],
            target_race_date=race["race_date"],
            target_distance=race["distance_furlongs"],
            target_surface=race["surface"],
            target_jockey=entry["jockey"],
            target_trainer=entry["trainer"],
            post_position=entry["post_position"],
            morning_line_odds=entry["morning_line_odds"],
            equipment=entry["equipment"] if "equipment" in entry.keys() else "",
            medication=entry["medication"] if "medication" in entry.keys() else "",
            jockey_change=bool(entry["jockey_change"]) if "jockey_change" in entry.keys() else False,
            workouts_data=workouts_raw,
            track_condition=race["track_condition"],
            rail_feet=rail_feet,
            total_field=total_field
        )
        profiles.append(prof)

    # 2. Modelar el Ritmo de Carrera (Pace Dynamics)
    pace_analysis = project_race_pace(profiles, race["distance_furlongs"], race["surface"])

    # 3. Aplicar ajuste táctico de ritmo a cada caballo
    for prof in profiles:
        pace_adj = compute_pace_adjustment(prof["pace_style"], pace_analysis["scenario"])
        prof["pace_adjustment"] = pace_adj
        prof["composite_score"] = round(max(20.0, min(120.0, prof["base_score"] + pace_adj)), 1)

    # 4. Ordenar ranking final
    ranked = sorted(profiles, key=lambda x: x["composite_score"], reverse=True)
    top_score = ranked[0]["composite_score"] if ranked else 100.0

    # 5. Detectar Top Pick, El Enemigo, Nivel de Paridad y Bomba / Valor
    top_pick = ranked[0]
    enemy_pick = ranked[1] if len(ranked) > 1 else None

    # Paridad entre punteros
    parity_level = "STANDOUT"
    parity_reason = "Ventaja técnica clara sobre el resto del lote"

    if enemy_pick:
        score_diff = round(top_pick["composite_score"] - enemy_pick["composite_score"], 1)
        if score_diff <= 5.5 or top_pick["morning_line_odds"] >= 3.5 or pace_analysis["scenario"] in ["PACE_COLLAPSE", "CONTESTED_PACE"]:
            parity_level = "HIGH_PARITY"
            parity_reason = f"Alta paridad: {enemy_pick['horse_name']} a solo {score_diff} pts del líder"

    # Apuesta de Valor (+EV)
    value_pick = None
    for p in ranked[1:]:
        if p["morning_line_odds"] >= 3.5 and p["composite_score"] >= (top_score - 6.5) and not value_pick:
            value_pick = p
            break

    # Bomba / Sorpresa (8-1 en adelante)
    longshot_pick = None
    for p in ranked:
        if p["horse_name"] == top_pick["horse_name"]:
            continue
        if p["morning_line_odds"] >= 8.0 and not longshot_pick:
            longshot_pick = p
            break

    if not longshot_pick:
        for p in ranked:
            if p["horse_name"] != top_pick["horse_name"] and p["morning_line_odds"] >= 6.0:
                longshot_pick = p
                break

    return {
        "race": dict(race),
        "pace_analysis": pace_analysis,
        "profiles": profiles,
        "ranked_profiles": ranked,
        "top_pick": top_pick,
        "enemy_pick": enemy_pick,
        "parity_level": parity_level,
        "parity_reason": parity_reason,
        "value_pick": value_pick,
        "longshot_pick": longshot_pick
    }
