"""
Motor de Ejercicios Previos (Morning Workouts & Breezes Engine).
Evalúa la condición física real, velocidad matutina y detección de 'Bullet Workouts'.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

# Tiempos par de aprontes matutinos en arena rápida (Dirt FT) en segundos
WORKOUT_PAR_TIMES = {
    3.0: 36.60,   # 3 furlongs (600m)
    4.0: 48.60,   # 4 furlongs (800m) - El estándar más común en USA
    5.0: 60.80,   # 5 furlongs (1000m)
    6.0: 73.20,   # 6 furlongs (1200m)
}


def evaluate_workouts(workouts_list: List[Dict[str, Any]], target_race_date: str) -> Dict[str, Any]:
    """
    Evalúa la secuencia de ejercicios matutinos de un caballo previo a la carrera.
    Parámetros de un apronte:
    - date: Fecha del ejercicio ('YYYY-MM-DD')
    - track: Hipódromo ('SA', 'DMR', 'KEE', etc.)
    - distance_furlongs: 3.0, 4.0, 5.0, 6.0
    - time_seconds: Tiempo registrado
    - workout_type: 'B' (Breezing - cómodo en las manos) o 'H' (Handily - exigido)
    - rank: Posición respecto a todos los caballos de la mañana (ej. 1 si fue el mejor de 45: '1/45')
    - total_workers: Total de caballos que trabajaron esa distancia
    """
    if not workouts_list:
        return {
            "workout_score": 60.0,
            "has_bullet": False,
            "recent_work_days": 99,
            "condition_verdict": "Sin aprontes públicos recientes",
            "last_work_summary": "N/A"
        }

    # Ordenar por fecha descendente
    sorted_works = sorted(workouts_list, key=lambda x: x.get("date", "2000-01-01"), reverse=True)
    latest = sorted_works[0]

    # Calcular días desde el último apronte
    race_d = datetime.strptime(target_race_date, "%Y-%m-%d")
    work_d = datetime.strptime(latest["date"], "%Y-%m-%d")
    days_since_work = (race_d - work_d).days

    # 1. Comprobar si tiene 'Bullet Workout' (el trabajo más rápido o top 5% de la mañana)
    has_bullet = False
    bullet_notes = []
    for w in sorted_works[:3]:
        r = w.get("rank", 99)
        tot = w.get("total_workers", 1)
        if r <= 3 or (tot >= 15 and (r / tot) <= 0.08):
            has_bullet = True
            bullet_notes.append(f"{w['distance_furlongs']}f en {w['time_seconds']}s ({r}/{tot})")

    # 2. Medir la velocidad del último apronte respecto al par
    dist = latest.get("distance_furlongs", 4.0)
    time_sec = latest.get("time_seconds", 49.0)
    par = WORKOUT_PAR_TIMES.get(dist, 48.60)
    speed_diff = par - time_sec  # Positivo = más veloz que el par

    # 3. Puntuación de Acondicionamiento (Workout Fitness Score: 0 a 100)
    base_score = 70.0

    # Bono por velocidad del apronte (+/- 12 pts)
    base_score += speed_diff * 4.0

    # Bono si fue 'Breezing' (en las manos sin castigo)
    if latest.get("workout_type", "B").upper() == "B":
        base_score += 4.0

    # Bono por 'Bullet Workout'
    if has_bullet:
        base_score += 10.0

    # Ajuste por cercanía a la carrera
    if 4 <= days_since_work <= 10:
        base_score += 6.0   # Momento cumbre de preparación
    elif days_since_work < 4:
        base_score -= 3.0   # Podría llegar algo fatigado si fue muy exigente
    elif days_since_work > 16:
        base_score -= 8.0   # Falta de mantenimiento reciente

    score = round(max(30.0, min(100.0, base_score)), 1)

    # Veredicto de acondicionamiento
    if score >= 88.0 or has_bullet:
        condition_verdict = "🎯 Acondicionamiento ÓPTIMO (Apronte sobresaliente)"
    elif score >= 75.0:
        condition_verdict = "✓ Buena preparación física"
    elif score >= 60.0:
        condition_verdict = "Normal / Rutinario"
    else:
        condition_verdict = "⚠️ Lento o falto de ritmo matutino"

    rank_str = f"({latest.get('rank', '-')}/{latest.get('total_workers', '-')})" if latest.get("rank") else ""
    summary = f"{latest.get('distance_furlongs', 4)}f en {time_sec:.2f}s {latest.get('workout_type', 'B')} {rank_str} el {latest.get('date', '')}"

    return {
        "workout_score": score,
        "has_bullet": has_bullet,
        "recent_work_days": days_since_work,
        "condition_verdict": condition_verdict,
        "last_work_summary": summary,
        "bullet_details": bullet_notes
    }
