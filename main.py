"""
Aplicación Principal: Motor de Pronósticos y Past Performances para Carreras USA.
"""

import sys
import os

# Asegurar que el directorio raíz del proyecto está en el PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.database import get_db_connection, init_database
from src.seed_sample_data import seed_data
from src.pp_card import generate_race_pp_card
from src.features import get_horse_past_performances

console = Console()


def show_scheduled_races():
    """Muestra todas las carreras disponibles en la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.race_id, r.race_date, r.race_number, r.distance_furlongs, r.surface, r.race_class, r.purse, t.name as track_name
        FROM races r
        JOIN tracks t ON r.track = t.code
        WHERE r.status = 'SCHEDULED'
        ORDER BY r.race_date ASC, r.race_number ASC
    """)
    races = cursor.fetchall()
    conn.close()

    if not races:
        console.print("[yellow]No hay carreras programadas actualmente.[/yellow]")
        return []

    table = Table(title="CARRERAS PROGRAMADAS DISPONIBLES", border_style="bright_blue")
    table.add_column("ID Carrera", style="bold cyan")
    table.add_column("Hipódromo", style="bold")
    table.add_column("Fecha", justify="center")
    table.add_column("Carrera #", justify="center")
    table.add_column("Distancia", justify="center")
    table.add_column("Sup.", justify="center")
    table.add_column("Clase", justify="left")
    table.add_column("Premio", justify="right", style="green")

    race_ids = []
    for r in races:
        race_ids.append(r["race_id"])
        table.add_row(
            r["race_id"],
            r["track_name"],
            r["race_date"],
            str(r["race_number"]),
            f"{r['distance_furlongs']}f",
            r["surface"],
            r["race_class"],
            f"${r['purse']:,.0f}" if r["purse"] else "N/A"
        )
    console.print(table)
    return race_ids


def inspect_horse_history(horse_name: str):
    """Muestra el historial y ficha completa de un caballo."""
    pps = get_horse_past_performances(horse_name, limit=10)
    if not pps:
        console.print(f"[bold red]No se encontraron registros para el caballo '{horse_name}'.[/bold red]")
        return

    console.print(Panel(f"Historial de Carreras: [bold yellow]{horse_name}[/bold yellow]", border_style="green"))
    table = Table(border_style="dim")
    table.add_column("Fecha")
    table.add_column("Hipódromo")
    table.add_column("Dist / Sup")
    table.add_column("Pista")
    table.add_column("Clase")
    table.add_column("Llegada", justify="center")
    table.add_column("Margen", justify="center")
    table.add_column("Tiempo", justify="center")
    table.add_column("Speed Fig Propio", style="bold cyan", justify="center")
    table.add_column("Jockey")
    table.add_column("Trainer")
    table.add_column("Cuota", justify="right")

    for r in pps:
        pos_str = f"1º (Ganó)" if r["finish_position"] == 1 else f"{r['finish_position']}º"
        margin = "0.0" if r["finish_position"] == 1 else f"+{r['lengths_behind']} cpos"
        table.add_row(
            r["race_date"],
            r["track"],
            f"{r['distance_furlongs']}f {r['surface']}",
            r["track_condition"],
            r["race_class"],
            pos_str,
            margin,
            f"{r['final_time_sec']:.2f}s",
            str(r["speed_rating"]),
            r["jockey"],
            r["trainer"],
            f"{r['official_odds']} - 1"
        )
    console.print(table)


def main_menu():
    init_database()
    console.print(Panel.fit(
        "[bold cyan]HORSERACING AI - MOTOR DE PRONOSTICOS Y PAST PERFORMANCES (USA)[/bold cyan]\n"
        "[italic white]Analisis Cuantitativo, Speed Figures Propios y Deteccion de Valor (+EV)[/italic white]",
        border_style="bright_blue"
    ))

    while True:
        console.print("\n[bold]Menú Principal:[/bold]")
        console.print("1. [bold cyan]Ver Carreras Programadas[/bold cyan]")
        console.print("2. [bold green]Generar Ficha de Past Performance y Pronóstico de una Carrera[/bold green]")
        console.print("3. [bold yellow]Consultar Historial de un Caballo Específico[/bold yellow]")
        console.print("4. [bold magenta]Cargar / Restaurar Datos de Prueba (Gulfstream Park & Saratoga)[/bold magenta]")
        console.print("5. Salir")

        try:
            choice = input("\nSelecciona una opción (1-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            show_scheduled_races()
        elif choice == "2":
            races = show_scheduled_races()
            if races:
                race_id = input("\nIngresa el ID de la carrera (ej. GP_20261010_R08): ").strip()
                if not race_id:
                    race_id = races[0]
                generate_race_pp_card(race_id)
        elif choice == "3":
            h_name = input("\nIngresa el nombre del caballo (ej. Speedy Lightning): ").strip()
            if h_name:
                inspect_horse_history(h_name)
        elif choice == "4":
            seed_data()
            console.print("[bold green]Datos de prueba cargados con éxito.[/bold green]")
        elif choice == "5":
            console.print("[cyan]¡Hasta luego y buena suerte en la pista![/cyan]")
            break
        else:
            console.print("[red]Opción no válida.[/red]")


if __name__ == "__main__":
    main_menu()
