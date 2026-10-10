import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import List, Dict, Any
from src.features import compute_horse_profile
from src.database import get_db_connection

console = Console()


def generate_race_pp_card(race_id: str) -> None:
    """Genera la ficha completa de Past Performance para una carrera."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Obtener datos de la carrera
    cursor.execute("""
        SELECT r.*, t.name as track_name
        FROM races r
        JOIN tracks t ON r.track = t.code
        WHERE r.race_id = ?
    """, (race_id,))
    race = cursor.fetchone()

    if not race:
        console.print(f"[bold red]No se encontró la carrera {race_id}[/bold red]")
        conn.close()
        return

    # 2. Obtener los inscritos
    cursor.execute("""
        SELECT * FROM today_entries
        WHERE race_id = ?
        ORDER BY post_position ASC
    """, (race_id,))
    entries = cursor.fetchall()
    conn.close()

    if not entries:
        console.print(f"[bold yellow]No hay inscritos registrados para {race_id}[/bold yellow]")
        return

    # Encabezado estilizado
    surface_desc = {"D": "Dirt (Arena)", "T": "Turf (Grama)", "A": "Tapeta / Sintética"}.get(race["surface"], race["surface"])
    header_text = (
        f"[bold cyan]{race['track_name']} ({race['track']})[/bold cyan] - Carrera #{race['race_number']} | "
        f"Fecha: [bold]{race['race_date']}[/bold]\n"
        f"Distancia: [bold yellow]{race['distance_furlongs']} Furlongs[/bold yellow] (~{int(race['distance_furlongs']*201.16)} metros) | "
        f"Superficie: [bold]{surface_desc}[/bold] | Condición: [bold]{race['track_condition']}[/bold]\n"
        f"Clase: [bold green]{race['race_class']}[/bold green] | Premio (Purse): [bold green]${race['purse']:,.0f}[/bold green]"
    )
    console.print(Panel(header_text, title="PAST PERFORMANCES PROPIAS - TARJETA OFICIAL", border_style="bright_blue"))

    # Procesar perfiles analíticos
    profiles = []
    for entry in entries:
        profile = compute_horse_profile(
            horse_name=entry["horse_name"],
            target_race_date=race["race_date"],
            target_distance=race["distance_furlongs"],
            target_surface=race["surface"],
            target_jockey=entry["jockey"],
            target_trainer=entry["trainer"],
            post_position=entry["post_position"],
            morning_line_odds=entry["morning_line_odds"]
        )
        profiles.append(profile)

    # Ordenar por Índice Compuesto para identificar al favorito analítico
    profiles_ranked = sorted(profiles, key=lambda x: x["composite_score"], reverse=True)
    top_score = profiles_ranked[0]["composite_score"] if profiles_ranked else 100

    # Tabla Resumen de Contendientes
    table = Table(title="TABLA GENERAL DE CONTENDIENTES Y RATINGS", border_style="cyan")
    table.add_column("PP", justify="center", style="bold white")
    table.add_column("Ejemplar", style="bold yellow")
    table.add_column("ML Odds", justify="center", style="magenta")
    table.add_column("Speed (Ult/Pond/Top)", justify="center")
    table.add_column("Pace", justify="center")
    table.add_column("Layoff", justify="center")
    table.add_column("Jockey (%Vic)", justify="left")
    table.add_column("Trainer (%Vic)", justify="left")
    table.add_column("Tendencia", justify="center")
    table.add_column("Indice Propio", justify="right", style="bold green")
    table.add_column("Veredicto", justify="center", style="bold")

    for p in sorted(profiles, key=lambda x: x["post_position"]):
        # Veredicto y detección de Valor (+EV)
        score = p["composite_score"]
        odds = p["morning_line_odds"]
        
        if score == top_score:
            verdict = "[black on bright_green] TOP PICK [*] [/]"
        elif score >= top_score - 4.0:
            if odds >= 4.0:
                verdict = "[bold yellow on dark_blue] VALUE +EV [!] [/]"
            else:
                verdict = "[bold cyan] CONTENDER [/]"
        elif odds >= 8.0 and score >= top_score - 8.0:
            verdict = "[bold bright_magenta] LONGSHOT [/]"
        else:
            verdict = "[dim] OUTSIDER [/]"

        table.add_row(
            str(p["post_position"]),
            p["horse_name"],
            f"{odds:.1f}-1",
            f"{p['last_speed']} / {p['weighted_speed']} / {p['best_speed']}",
            f"{p['pace_style']}",
            f"{p['layoff_days']}d",
            f"{p['jockey']} ({p['jockey_win_pct']}%)",
            f"{p['trainer']} ({p['trainer_win_pct']}%)",
            p["form_trend"],
            f"{score:.1f}",
            verdict
        )

    console.print(table)
    console.print()

    # Detalle de Past Performances (Últimas carreras de cada caballo)
    console.print("[bold underline cyan]HISTORIAL RECIENTE (PAST PERFORMANCES DETALLADAS):[/bold underline cyan]")
    for p in sorted(profiles, key=lambda x: x["post_position"]):
        pps = p["past_performances"]
        console.print(f"\n[bold yellow]#{p['post_position']} {p['horse_name']}[/bold yellow] | Jockey: [white]{p['jockey']}[/white] | Trainer: [white]{p['trainer']}[/white] | Rating Propio: [bold green]{p['composite_score']}[/bold green]")
        
        if not pps:
            console.print("   [dim italic]Sin carreras previas registradas (Debutante)[/dim italic]")
            continue

        pp_table = Table(show_header=True, header_style="bold dim", box=None, padding=(0, 1))
        pp_table.add_column("Fecha", style="dim")
        pp_table.add_column("Hipódromo", justify="center")
        pp_table.add_column("Dist/Sup", justify="center")
        pp_table.add_column("Pista", justify="center")
        pp_table.add_column("Clase", justify="center")
        pp_table.add_column("Llegó", justify="center")
        pp_table.add_column("Margen", justify="center")
        pp_table.add_column("Tiempo", justify="center")
        pp_table.add_column("Speed Fig", justify="bold cyan")
        pp_table.add_column("Jockey")
        pp_table.add_column("Cuota", justify="right")

        for r in pps:
            fin_pos = r["finish_position"]
            margin = "Gano" if fin_pos == 1 else f"{r['lengths_behind']} cpos"
            time_str = f"{r['final_time_sec']:.2f}s" if r.get("final_time_sec") else "N/A"
            suffix = "st" if fin_pos == 1 else ("nd" if fin_pos == 2 else ("rd" if fin_pos == 3 else "th"))
            pos_style = f"[bold green]{fin_pos}{suffix}[/bold green]" if fin_pos == 1 else f"{fin_pos}{suffix}"
            
            pp_table.add_row(
                r["race_date"],
                r["track"],
                f"{r['distance_furlongs']}f {r['surface']}",
                r["track_condition"],
                r["race_class"],
                pos_style,
                margin,
                time_str,
                str(r["speed_rating"]),
                r["jockey"],
                f"{r['official_odds']} - 1"
            )
        console.print(pp_table)
