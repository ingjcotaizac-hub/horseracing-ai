"""
Motor de cálculo de Speed Figures propios.
Normaliza el rendimiento de los caballos comparando su tiempo real contra
el 'Par Time' (tiempo estándar) de cada distancia, superficie y condición de pista.
"""

# Tiempos estándar 'Par Time' (en segundos) por distancia en furlongs y superficie
# 1 furlong = 1/8 milla = 201.16 metros
PAR_TIMES = {
    'D': {  # Dirt (Arena)
        5.0: 58.00,
        5.5: 64.20,
        6.0: 70.20,    # 1:10.20 (Sprint estándar)
        6.5: 76.60,
        7.0: 83.00,    # 1:23.00
        8.0: 96.20,    # 1:36.20 (1 milla)
        8.5: 103.40,   # 1:43.40 (1 1/16 milla)
        9.0: 109.80,   # 1:49.80 (1 1/8 milla)
        10.0: 121.50,  # 2:01.50 (1 1/4 milla - Clásicos)
    },
    'T': {  # Turf (Grama)
        5.0: 56.80,
        5.5: 62.50,
        8.0: 94.80,
        8.5: 101.80,
        9.0: 108.00,
        10.0: 119.50,
        11.0: 133.00,
        12.0: 145.00,  # 1 1/2 milla
    },
    'A': {  # All-Weather / Tapeta
        5.5: 63.50,
        6.0: 69.80,
        8.0: 95.80,
        8.5: 102.80,
    }
}

# Ajuste por condición de pista (variante de lentitud en segundos)
TRACK_VARIANTS = {
    'FT': 0.0,   # Fast (Dirt)
    'FM': 0.0,   # Firm (Turf)
    'GD': 0.40,  # Good (Levemente pesada)
    'SY': 0.90,  # Sloppy (Fangosa/Arena encharcada)
    'MY': 1.10,  # Muddy (Barro)
    'YL': 1.20,  # Yielding (Grama blanda)
    'SF': 1.60,  # Soft (Grama pesada)
}


def get_par_time(distance_furlongs: float, surface: str = 'D') -> float:
    """Obtiene el tiempo estándar más cercano para la distancia dada."""
    surface_dict = PAR_TIMES.get(surface.upper(), PAR_TIMES['D'])
    if distance_furlongs in surface_dict:
        return surface_dict[distance_furlongs]

    # Si la distancia exacta no está, interpolamos linealmente
    distances = sorted(surface_dict.keys())
    if distance_furlongs <= distances[0]:
        return surface_dict[distances[0]] * (distance_furlongs / distances[0])
    if distance_furlongs >= distances[-1]:
        return surface_dict[distances[-1]] * (distance_furlongs / distances[-1])

    # Interpolar entre dos distancias conocidas
    for i in range(len(distances) - 1):
        d1, d2 = distances[i], distances[i + 1]
        if d1 < distance_furlongs < d2:
            t1, t2 = surface_dict[d1], surface_dict[d2]
            return t1 + (t2 - t1) * ((distance_furlongs - d1) / (d2 - d1))
    return 70.0


def calculate_speed_rating(
    final_time_sec: float,
    distance_furlongs: float,
    surface: str = 'D',
    track_condition: str = 'FT',
    lengths_behind: float = 0.0,
    weight_carried: int = 120
) -> float:
    """
    Calcula el Speed Figure propietario (escala 0 - 115+).
    85 = Nivel medio en carreras de Allowance / buen caballo de pista.
    95 - 105+ = Nivel Stakes / Graded Stakes de élite.
    65 - 75 = Nivel Claiming modesto.
    """
    if final_time_sec is None or final_time_sec <= 0:
        return 50.0

    par = get_par_time(distance_furlongs, surface)
    variant = TRACK_VARIANTS.get(track_condition.upper(), 0.0)

    # El tiempo ajustado de la carrera compensando condición de pista
    adjusted_race_time = final_time_sec - variant

    # Cada segundo equivale a ~5 cuerpos (0.20 seg/cuerpo)
    # En sprints (<= 7f) el valor del segundo es ~12.5 puntos (~2.5 pts por cuerpo)
    # En rutas (> 7f) el valor del segundo es ~9.0 puntos (~1.8 pts por cuerpo)
    if distance_furlongs <= 7.0:
        pts_per_second = 12.5
        pts_per_length = 2.5
    else:
        pts_per_second = 9.0
        pts_per_length = 1.8

    # Si el caballo no ganó, añadimos la penalización por cuerpos de retraso
    # Base: 85 puntos para el caballo que iguala exactamente el Par Time
    delta_seconds = par - adjusted_race_time
    rating = 85.0 + (delta_seconds * pts_per_second) - (lengths_behind * pts_per_length)

    # Ajuste leve por peso (1 punto cada 3 libras por encima/debajo de 120 lbs)
    weight_diff = (120 - weight_carried) / 3.0
    rating += weight_diff

    # Limitar a rango razonable
    return round(max(30.0, min(125.0, rating)), 1)


def calculate_pace_ratings(
    frac_2f: float,
    frac_4f: float,
    final_time: float,
    distance_furlongs: float
) -> dict:
    """
    Calcula los ratings de paso (Early Pace y Late Pace).
    Permite identificar si el caballo corre en la delantera o remata desde atrás.
    """
    if not frac_2f or not frac_4f or not final_time:
        return {"early_pace": 75.0, "late_pace": 75.0, "style": "P"}

    # Fraccional inicial rápido en 6f: ~22.0s en 2f y ~45.0s en 4f
    par_4f = 45.40
    early_pace = 85.0 + (par_4f - frac_4f) * 5.0

    # Fracción final (desde los 800m hasta la meta)
    closing_fraction = final_time - frac_4f
    # Par closing fraccional en 6f (1200m - 800m = 400m): ~25.0s
    par_closing = 25.0 if distance_furlongs <= 7.0 else 38.0
    late_pace = 85.0 + (par_closing - closing_fraction) * 4.0

    # Determinar el estilo de carrera:
    # E = Early (Puntero nato)
    # P = Presser (Corre 2º a 4º acechando)
    # S = Sustained / Closer (Rematador desde el fondo)
    diff = early_pace - late_pace
    if diff >= 6.0:
        style = "E"   # Early Runner
    elif diff <= -6.0:
        style = "S"   # Closer / Rematador
    else:
        style = "P"   # Presser / Colocado

    return {
        "early_pace": round(early_pace, 1),
        "late_pace": round(late_pace, 1),
        "style": style
    }
