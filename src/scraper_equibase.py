"""
Módulo de descarga y parseo de Entries y Result Charts de hipódromos de EE. UU.
Diseñado para consultar las páginas públicas de Equibase / Daily Racing Form.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def parse_odds_string(odds_str: str) -> float:
    """Convierte texto de cuota tipo '5/2', '9-5', '3.50', '8/1' a float decimal."""
    if not odds_str:
        return 5.0
    clean = odds_str.strip().replace("*", "")
    try:
        if "/" in clean:
            num, den = clean.split("/")
            return round(float(num) / float(den), 2)
        elif "-" in clean:
            num, den = clean.split("-")
            return round(float(num) / float(den), 2)
        return float(clean)
    except Exception:
        return 5.0


def parse_fractional_time(time_str: str) -> Optional[float]:
    """Convierte tiempos tipo ':22.45', '1:10.23' o '1:43.80' a segundos."""
    if not time_str:
        return None
    clean = time_str.strip().lstrip(":")
    try:
        if ":" in clean:
            parts = clean.split(":")
            mins = float(parts[0])
            secs = float(parts[1])
            return round(mins * 60 + secs, 2)
        return round(float(clean), 2)
    except Exception:
        return None


def fetch_equibase_entries(track_code: str, date_obj: datetime) -> List[Dict[str, Any]]:
    """
    Descarga y parsea la lista de inscritos (Entries) de un hipódromo para una fecha.
    URL estándar de Equibase: https://www.equibase.com/static/entry/{TRK}{MMDDYY}USA-EQB.html
    """
    date_str = date_obj.strftime("%m%d%y")
    url = f"https://www.equibase.com/static/entry/{track_code.upper()}{date_str}USA-EQB.html"

    print(f"Consultando entradas en: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Aviso: Estado HTTP {response.status_code} al consultar entradas de {track_code}.")
            return []

        soup = BeautifulSoup(response.content, "lxml")
        races_data = []

        # El HTML de Equibase organiza las carreras por tablas con encabezados de número de carrera
        race_tables = soup.find_all("table")
        for table in race_tables:
            # Buscar filas de caballos
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 6:
                    # Extraer columnas típicas (PP, Horse, Jockey, Trainer, Weight, ML Odds)
                    text_cols = [c.get_text(strip=True) for c in cols]
                    if any("Horse" in t for t in text_cols):
                        continue
                    # Parseo flexible según la disposición de columnas
                    try:
                        post_pos = int(re.search(r'\d+', text_cols[0]).group()) if re.search(r'\d+', text_cols[0]) else 1
                        horse_name = text_cols[1]
                        jockey = text_cols[2]
                        weight = int(re.search(r'\d+', text_cols[3]).group()) if re.search(r'\d+', text_cols[3]) else 120
                        trainer = text_cols[4] if len(text_cols) > 4 else "Unknown"
                        ml_odds = parse_odds_string(text_cols[5]) if len(text_cols) > 5 else 4.0

                        races_data.append({
                            "post_position": post_pos,
                            "horse_name": horse_name,
                            "jockey": jockey,
                            "trainer": trainer,
                            "weight": weight,
                            "morning_line_odds": ml_odds
                        })
                    except Exception:
                        continue

        return races_data
    except Exception as e:
        print(f"Error en la consulta de Equibase: {e}")
        return []
