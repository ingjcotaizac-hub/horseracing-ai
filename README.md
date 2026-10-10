# Horseracing AI - Motor de Pronósticos y Past Performances Propias (USA)

Sistema analítico y generador de **Past Performances (PPs)** independientes para hipódromos de élite de Estados Unidos (Gulfstream Park, Saratoga, Churchill Downs, Belmont Park, Del Mar).

---

## 🚀 Cómo ejecutar la aplicación

### Opción A: Dashboard Web Interactivo (Recomendado)
Abre tu navegador en: **http://localhost:8501** (ya está corriendo en tu máquina)

Para iniciarlo manualmente en cualquier momento:
```powershell
.\venv\Scripts\streamlit.exe run app.py
```

### Opción B: Menú Interactivo en Consola
```powershell
.\venv\Scripts\python.exe main.py
```

---

## 📁 Estructura del Proyecto

```text
Horseracing/
├── data/
│   └── horseracing.db        # Base de datos SQLite local
├── src/
│   ├── database.py           # Esquema relacional (tracks, races, race_results, today_entries)
│   ├── speed_figures.py      # Motor de Speed Figures propios normalizados por Par Times
│   ├── features.py           # Cálculo de Layoff, Ritmo (Pace E/P/S), Conexiones e Índice
│   ├── pp_card.py            # Generador visual de las Fichas de Past Performance
│   ├── scraper_equibase.py   # Módulo de ingesta y parseo de entradas/resultados
│   └── seed_sample_data.py   # Seeder con datos reales de Gulfstream y Saratoga
├── main.py                   # Menú interactivo en consola
├── requirements.txt          # Dependencias del proyecto
└── venv/                     # Entorno virtual con Python 3.12 y librerías
```

---

## 🧮 Métricas Propietarias Implementadas

### 1. Speed Figure Propio (Normalizado)
Compara el tiempo real de la carrera contra el tiempo estándar (*Par Time*) de esa pista, superficie y distancia:
* **85 puntos**: Caballo de nivel promedio en carreras de *Allowance*.
* **95 - 105+ puntos**: Rendimiento de nivel clásico (*Stakes / Graded Stakes*).
* **65 - 75 puntos**: Nivel de carreras de reclamo modesto (*Claiming*).
* Ajustado automáticamente por condición de pista (*Fast, Sloppy, Muddy, Firm, Yielding*) y peso llevado.

### 2. Pace Style (Estilo de Carrera)
* **`E` (Early / Puntero):** Busca la punta desde la gatera.
* **`P` (Presser / Colocado):** Corre acechando a 1-3 cuerpos de los líderes.
* **`S` (Sustained / Rematador):** Corre rezagado y avanza en la recta final.

### 3. Layoff (Días de descanso)
Mide los días desde su última actuación para evaluar si el caballo llega con ritmo competitivo óptimo (14 a 50 días) o tras un paro prolongado.

### 4. Índice Compuesto Propietario (0 a 100)
Combina:
* **50%**: Rendimiento de velocidad ponderada de sus últimas carreras.
* **15%**: Efectividad reciente de Jinete y Entrenador.
* **15%**: Factor de descanso y frescura.
* **10%**: Eficacia demostrada en esa superficie y distancia.
* **10%**: Probabilidad implícita de las cuotas matutinas (*Morning Line*).

---

## 🏆 Veredictos Automáticos
* **`TOP PICK [*]`**: El ejemplar con mejor balance global según el modelo.
* **`VALUE +EV [!]`**: Caballo con altas probabilidades según el modelo pero con dividendo atractivo en las cuotas (gran oportunidad de ganancia).
* **`LONGSHOT`**: Sorpresa con dividendo alto pero con métricas suficientes para meterse en la pizarra.
