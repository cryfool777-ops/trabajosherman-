# -*- coding: utf-8 -*-
"""
Gestor del benchmark de ordenamiento.

Lee los CSV generados por los 5 lenguajes, detecta el hardware y las versiones
de los lenguajes/compiladores, calcula los rankings y genera:
  - reporte.md
  - grafica_tiempo_algoritmo.png
  - grafica_tiempo_lenguaje.png
  - grafica_tiempo_normalizado_lenguaje.png

Metodo de normalizacion:
  Para cada grupo de prueba comparable (mismo algoritmo, tamano y tipo de
  arreglo) se toma el menor tiempo del grupo y se calcula el cociente
  tiempo / menor_tiempo. Luego se calcula la media geometrica de esos
  cocientes. La media geometrica reduce el peso de valores atipicos y de
  pruebas muy pequenas; asi cada prueba pesa de forma equilibrada y las
  pruebas lentas (por ejemplo, 1,000,000 elementos) no dominan. Se usa un
  piso de 0.001 ms para evitar divisiones por cero y ruido de temporizacion
  en pruebas muy pequenas.

  Para comparar lenguajes se usan solo grupos "completos y balanceados":
  algoritmos y tipos de arreglo con estado ok en los 5 lenguajes y en los 5
  tamanos. Esto evita que un lenguaje parezca mas rapido solo porque sus
  pruebas lentas fueron timeout o porque la mezcla de algoritmos cambia.
  Las filas timeout/error se excluyen de los promedios y se muestran aparte.
"""

import csv
import math
import os
import platform
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.abspath(__file__))

LANGUAGES = [
    ("csharp", "C#"),
    ("cpp", "C++"),
    ("java", "Java"),
    ("python", "Python"),
    ("javascript", "JavaScript"),
]
LANGUAGE_DISPLAY = dict(LANGUAGES)
LANGUAGE_ORDER = {key: i for i, (key, _) in enumerate(LANGUAGES)}

ALGORITHMS = [
    "Bubble Sort",
    "Selection Sort",
    "Insertion Sort",
    "Merge Sort",
    "Shell Sort",
    "Bucket Sort",
    "Quick Sort",
    "Radix Sort",
    "Heap Sort",
]
SIZES = [100, 1000, 10000, 100000, 1000000]
TYPES = ["aleatorio", "ordenado", "inverso"]
TIME_FLOOR_MS = 0.001


# ---------------------------------------------------------------------------
# Utilidades de presentacion
# ---------------------------------------------------------------------------
def mean(values):
    return statistics.fmean(values) if values else float("nan")


def geometric_mean(values):
    if not values:
        return float("nan")
    total = 0.0
    for value in values:
        total += math.log(max(value, 1e-12))
    return math.exp(total / len(values))


def fmt_time(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    return f"{value:.4f}"


def fmt_int(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    return f"{value:.0f}"


def fmt_ratio(value):
    if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
        return "—"
    return f"{value:.3f}"


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Deteccion de hardware y versiones
# ---------------------------------------------------------------------------
def run_command(command, timeout=30):
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        text = (completed.stdout or "") + "\n" + (completed.stderr or "")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return lines[0] if lines else "No disponible"
    except Exception:
        return "No disponible"


def hardware_info():
    cpu_model = platform.processor() or "No disponible"
    physical_cores = None
    logical_cores = os.cpu_count()
    ram_bytes = None

    try:
        import psutil  # type: ignore

        cpu_model = platform.processor() or cpu_model
        physical_cores = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count(logical=True) or logical_cores
        ram_bytes = psutil.virtual_memory().total
        try:
            cpu_model = psutil.cpu_freq().current and cpu_model or cpu_model
        except Exception:
            pass
    except Exception:
        pass

    if os.name == "nt":
        script = (
            "$cpu=Get-CimInstance Win32_Processor | Select-Object -First 1; "
            "Write-Output ('CPU=' + $cpu.Name); "
            "Write-Output ('CORES=' + $cpu.NumberOfCores); "
            "Write-Output ('LOGICAL=' + $cpu.NumberOfLogicalProcessors); "
            "$cs=Get-CimInstance Win32_ComputerSystem; "
            "Write-Output ('RAM=' + $cs.TotalPhysicalMemory)"
        )
        try:
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
            for line in completed.stdout.splitlines():
                line = line.strip()
                if line.startswith("CPU="):
                    cpu_model = line[4:].strip()
                elif line.startswith("CORES="):
                    value = line[6:].strip()
                    if value.isdigit():
                        physical_cores = int(value)
                elif line.startswith("LOGICAL="):
                    value = line[8:].strip()
                    if value.isdigit():
                        logical_cores = int(value)
                elif line.startswith("RAM="):
                    value = line[4:].strip()
                    if value.isdigit():
                        ram_bytes = int(value)
        except Exception:
            pass
    elif os.name != "nt":
        try:
            if os.path.exists("/proc/cpuinfo"):
                with open("/proc/cpuinfo", encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        if line.lower().startswith("model name"):
                            cpu_model = line.split(":", 1)[1].strip()
                            break
            if os.path.exists("/proc/meminfo"):
                with open("/proc/meminfo", encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        if line.startswith("MemTotal:"):
                            ram_bytes = int(line.split()[1]) * 1024
                            break
        except Exception:
            pass

    ram_gb = None
    if ram_bytes:
        ram_gb = ram_bytes / (1024 ** 3)

    return {
        "cpu": cpu_model,
        "physical_cores": physical_cores,
        "logical_cores": logical_cores,
        "ram_gb": ram_gb,
        "os": platform.platform(),
    }


def versions_info():
    java_runtime = run_command(["java", "-version"])
    java_compiler = run_command(["javac", "-version"])
    return [
        ("C# / .NET", run_command(["dotnet", "--version"])),
        ("C++ (g++)", run_command(["g++", "--version"])),
        ("Java (runtime)", java_runtime),
        ("Java (javac)", java_compiler),
        ("Python", run_command([sys.executable, "--version"])),
        ("Node.js", run_command(["node", "--version"])),
    ]


# ---------------------------------------------------------------------------
# Lectura de resultados
# ---------------------------------------------------------------------------
def load_results():
    rows = []
    missing = []
    for language_key, display in LANGUAGES:
        path = os.path.join(ROOT, "resultados_%s.csv" % language_key)
        if not os.path.exists(path):
            alt = os.path.join(ROOT, "resultados", "resultados_%s.csv" % language_key)
            if os.path.exists(alt):
                path = alt
            else:
                missing.append(display)
                continue

        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for raw in reader:
                try:
                    algorithm = (raw.get("algoritmo") or "").strip()
                    size = int((raw.get("tamano") or "").strip())
                    array_type = (raw.get("tipo_arreglo") or "").strip()
                    state = (raw.get("estado") or "").strip().lower()
                    time_ms = float((raw.get("tiempo_ms") or "0").strip())
                    comparisons = int(float((raw.get("comparaciones") or "0").strip()))
                    swaps = int(float((raw.get("intercambios") or "0").strip()))
                except (TypeError, ValueError):
                    continue

                if algorithm not in ALGORITHMS or size not in SIZES or array_type not in TYPES:
                    continue
                if state not in ("ok", "timeout", "error"):
                    state = "error"

                rows.append(
                    {
                        "lenguaje": language_key,
                        "algoritmo": algorithm,
                        "tamano": size,
                        "tipo": array_type,
                        "tiempo_ms": time_ms,
                        "comparaciones": comparisons,
                        "intercambios": swaps,
                        "estado": state,
                    }
                )
    return rows, missing


# ---------------------------------------------------------------------------
# Rankings
# ---------------------------------------------------------------------------
def build_time_groups(rows, type_filter=None):
    groups = defaultdict(dict)
    for row in rows:
        if row["estado"] != "ok":
            continue
        if type_filter is not None and row["tipo"] != type_filter:
            continue
        key = (row["lenguaje"], row["tamano"], row["tipo"])
        groups[key][row["algoritmo"]] = row["tiempo_ms"]
    return groups


def language_ranking(rows):
    ok_rows = [r for r in rows if r["estado"] == "ok"]
    timeout_counter = Counter(r["lenguaje"] for r in rows if r["estado"] == "timeout")
    error_counter = Counter(r["lenguaje"] for r in rows if r["estado"] == "error")
    ok_counter = Counter(r["lenguaje"] for r in ok_rows)

    # Grupos (algoritmo, tamano, tipo) donde los 5 lenguajes tienen estado ok.
    algorithm_groups = defaultdict(dict)
    for row in ok_rows:
        key = (row["algoritmo"], row["tamano"], row["tipo"])
        algorithm_groups[key][row["lenguaje"]] = row["tiempo_ms"]

    # Grupos completos y balanceados: el mismo algoritmo y tipo debe tener
    # resultados ok en los 5 lenguajes y en los 5 tamanos. Asi la mezcla de
    # algoritmos no cambia entre tamanos y las medias son comparables.
    balanced_pairs = set()
    for algorithm in ALGORITHMS:
        for array_type in TYPES:
            complete_for_all_sizes = True
            for size in SIZES:
                times = algorithm_groups.get((algorithm, size, array_type), {})
                if len(times) != len(LANGUAGES):
                    complete_for_all_sizes = False
                    break
            if complete_for_all_sizes:
                balanced_pairs.add((algorithm, array_type))

    if balanced_pairs:
        complete_keys = [
            (algorithm, size, array_type)
            for algorithm in ALGORITHMS
            for size in SIZES
            for array_type in TYPES
            if (algorithm, array_type) in balanced_pairs
        ]
    else:
        # Respaldo: usar todos los grupos completos disponibles.
        complete_keys = [
            key for key, times in algorithm_groups.items() if len(times) == len(LANGUAGES)
        ]

    summary = []
    for language_key, display in LANGUAGES:
        ratios = []
        raw_times = []
        for key in complete_keys:
            times = algorithm_groups[key]
            if language_key not in times:
                continue
            t_lang = max(times[language_key], TIME_FLOOR_MS)
            best = max(min(times.values()), TIME_FLOOR_MS)
            ratio = t_lang / best
            ratios.append(ratio)
            raw_times.append(times[language_key])
            assert ratio >= 1.0, f"Ratio < 1 for {language_key} in {key}: {ratio}"

        score = geometric_mean(ratios) if ratios else float("inf")
        summary.append(
            {
                "key": language_key,
                "display": display,
                "score": score,
                "mean_time": mean(raw_times) if raw_times else float("nan"),
                "ok": ok_counter.get(language_key, 0),
                "timeout": timeout_counter.get(language_key, 0),
                "error": error_counter.get(language_key, 0),
                "complete_groups": len(ratios),
            }
        )

    summary.sort(key=lambda item: item["score"])
    return summary, complete_keys, algorithm_groups


def algorithm_ranking(rows, type_filter=None):
    groups = build_time_groups(rows, type_filter)
    ratios = defaultdict(list)
    wins = Counter()
    coverage = Counter()
    raw_times = defaultdict(list)

    for times in groups.values():
        if not times:
            continue
        best = min(times.values())
        effective_best = max(best, TIME_FLOOR_MS)
        for algorithm, value in times.items():
            v_eff = max(value, TIME_FLOOR_MS)
            ratio = v_eff / effective_best
            ratios[algorithm].append(ratio)
            assert ratio >= 1.0, f"Algo ratio < 1 for {algorithm}: {ratio}"
            raw_times[algorithm].append(value)
            coverage[algorithm] += 1
            if value <= best * (1.0 + 1e-9):
                wins[algorithm] += 1

    summary = []
    for algorithm in ALGORITHMS:
        if not ratios[algorithm]:
            continue
        summary.append(
            {
                "algorithm": algorithm,
                "score": geometric_mean(ratios[algorithm]),
                "wins": wins[algorithm],
                "coverage": coverage[algorithm],
                "mean_time": mean(raw_times[algorithm]),
            }
        )

    summary.sort(key=lambda item: item["score"])
    return summary


def fastest_algorithm_for_size(rows, size):
    ok_rows = [row for row in rows if row["estado"] == "ok" and row["tamano"] == size]
    expected_coverage = len(LANGUAGES) * len(TYPES)
    averages = {}
    for algorithm in ALGORITHMS:
        values = [row["tiempo_ms"] for row in ok_rows if row["algoritmo"] == algorithm]
        coverage = {
            (row["lenguaje"], row["tipo"])
            for row in ok_rows
            if row["algoritmo"] == algorithm
        }
        if len(values) == expected_coverage and len(coverage) == expected_coverage:
            averages[algorithm] = mean(values)
    if not averages:
        return None, float("nan")
    best = min(averages, key=averages.get)
    return best, averages[best]


# ---------------------------------------------------------------------------
# Tablas
# ---------------------------------------------------------------------------
def pivot_metric(ok_rows, field, integer=False):
    rows = []
    for algorithm in ALGORITHMS:
        values = [algorithm]
        for size in SIZES:
            # Require ok results for all 3 array types
            subsets_by_type = []
            complete = True
            for arr_type in TYPES:
                subset = [
                    row[field]
                    for row in ok_rows
                    if row["algoritmo"] == algorithm and row["tamano"] == size and row["tipo"] == arr_type
                ]
                if not subset:
                    complete = False
                    break
                subsets_by_type.append(subset)
            if not complete:
                # Check if partial is only due to ordered case? Or just mark partial
                # Need to detect if only ordered is present (Bubble/Insertion case)
                ordered_only = False
                ordered_subset = [
                    row[field]
                    for row in ok_rows
                    if row["algoritmo"] == algorithm and row["tamano"] == size and row["tipo"] == "ordenado"
                ]
                random_subset = [
                    row[field]
                    for row in ok_rows
                    if row["algoritmo"] == algorithm and row["tamano"] == size and row["tipo"] == "aleatorio"
                ]
                inverse_subset = [
                    row[field]
                    for row in ok_rows
                    if row["algoritmo"] == algorithm and row["tamano"] == size and row["tipo"] == "inverso"
                ]
                if ordered_subset and not random_subset and not inverse_subset:
                    ordered_only = True
                if ordered_only:
                    values.append("parcial*")
                elif not subsets_by_type and not ordered_only:
                    # Try to see if any subset exists
                    all_subsets = []
                    for arr_type in TYPES:
                        subset = [
                            row[field]
                            for row in ok_rows
                            if row["algoritmo"] == algorithm and row["tamano"] == size and row["tipo"] == arr_type
                        ]
                        if subset:
                            all_subsets.extend(subset)
                    if all_subsets:
                        values.append("parcial*")
                    else:
                        values.append("—")
                else:
                    values.append("parcial*")
            else:
                # Average across all three types
                all_vals = []
                for s in subsets_by_type:
                    all_vals.extend(s)
                if integer:
                    values.append(fmt_int(mean(all_vals)))
                else:
                    values.append(fmt_time(mean(all_vals)))
        rows.append(values)
    return rows


def language_size_table(complete_keys, algorithm_groups):
    rows = []
    for language_key, display in LANGUAGES:
        values = [display]
        for size in SIZES:
            keys = [key for key in complete_keys if key[1] == size]
            times = [
                algorithm_groups[key][language_key]
                for key in keys
                if language_key in algorithm_groups[key]
            ]
            values.append(fmt_time(mean(times)) if times else "—")
        rows.append(values)
    return rows


def per_language_time_tables(ok_rows):
    sections = []
    for language_key, display in LANGUAGES:
        language_rows = [row for row in ok_rows if row["lenguaje"] == language_key]
        rows = []
        for algorithm in ALGORITHMS:
            values = [algorithm]
            for size in SIZES:
                subset = [
                    row["tiempo_ms"]
                    for row in language_rows
                    if row["algoritmo"] == algorithm and row["tamano"] == size
                ]
                values.append(fmt_time(mean(subset)) if subset else "—")
            rows.append(values)
        headers = ["Algoritmo"] + [f"{size:,}".replace(",", ".") for size in SIZES]
        sections.append((display, md_table(headers, rows)))
    return sections


# ---------------------------------------------------------------------------
# Graficas
# ---------------------------------------------------------------------------
def plot_time_by_algorithm(ok_rows):
    plt.figure(figsize=(10, 6.5))
    plotted = False
    for algorithm in ALGORITHMS:
        xs = []
        ys = []
        for size in SIZES:
            subset = [
                row["tiempo_ms"]
                for row in ok_rows
                if row["algoritmo"] == algorithm and row["tamano"] == size
            ]
            if subset:
                xs.append(size)
                ys.append(mean(subset))
        if xs:
            plt.plot(xs, ys, marker="o", linewidth=1.8, label=algorithm)
            plotted = True

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Tamaño del arreglo")
    plt.ylabel("Tiempo promedio (ms, escala log)")
    plt.title("Tiempo de ordenamiento por algoritmo")
    if plotted:
        plt.legend(fontsize=8, ncol=2)
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    path = os.path.join(ROOT, "grafica_tiempo_algoritmo.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_time_by_language(complete_keys, algorithm_groups):
    plt.figure(figsize=(9, 6))
    for language_key, display in LANGUAGES:
        xs = []
        ys = []
        for size in SIZES:
            keys = [key for key in complete_keys if key[1] == size]
            times = [
                algorithm_groups[key][language_key]
                for key in keys
                if language_key in algorithm_groups[key]
            ]
            if times:
                xs.append(size)
                ys.append(mean(times))
        if xs:
            plt.plot(xs, ys, marker="o", linewidth=2, label=display)

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Tamaño del arreglo")
    plt.ylabel("Tiempo promedio (ms, escala log)")
    plt.title("Tiempo por lenguaje (grupos completos)")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    path = os.path.join(ROOT, "grafica_tiempo_lenguaje.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_normalized_by_language(complete_keys, algorithm_groups):
    plt.figure(figsize=(9, 6))
    for language_key, display in LANGUAGES:
        xs = []
        ys = []
        for size in SIZES:
            ratios = []
            for key in complete_keys:
                if key[1] != size:
                    continue
                times = algorithm_groups[key]
                if language_key not in times:
                    continue
                t_lang = max(times[language_key], TIME_FLOOR_MS)
                best = max(min(times.values()), TIME_FLOOR_MS)
                ratios.append(t_lang / best)
            if ratios:
                xs.append(size)
                ys.append(mean(ratios))
        if xs:
            plt.plot(xs, ys, marker="o", linewidth=2, label=display)

    plt.xscale("log")
    plt.xlabel("Tamaño del arreglo")
    plt.ylabel("Tiempo normalizado (ratio al mejor; menor es mejor)")
    plt.title("Tiempo normalizado por lenguaje")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    path = os.path.join(ROOT, "grafica_tiempo_normalizado_lenguaje.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


# ---------------------------------------------------------------------------
# Reporte
# ---------------------------------------------------------------------------
def main():
    rows, missing = load_results()
    if not rows:
        print("No se encontraron resultados CSV. Ejecute primero los 5 programas.")
        return 1

    ok_rows = [row for row in rows if row["estado"] == "ok"]
    bad_rows = [row for row in rows if row["estado"] != "ok"]

    hardware = hardware_info()
    versions = versions_info()
    language_summary, complete_keys, algorithm_groups = language_ranking(rows)
    alg_overall = algorithm_ranking(rows)
    alg_random = algorithm_ranking(rows, "aleatorio")
    alg_sorted = algorithm_ranking(rows, "ordenado")
    alg_inverse = algorithm_ranking(rows, "inverso")

    plot_time_by_algorithm(ok_rows)
    plot_time_by_language(complete_keys, algorithm_groups)
    plot_normalized_by_language(complete_keys, algorithm_groups)

    fastest_language = language_summary[0] if language_summary else None
    fastest_algorithm = alg_overall[0] if alg_overall else None
    fastest_random = alg_random[0] if alg_random else None
    fastest_sorted = alg_sorted[0] if alg_sorted else None
    fastest_inverse = alg_inverse[0] if alg_inverse else None

    report = []
    report.append("# Benchmark de algoritmos de ordenamiento en 5 lenguajes")
    report.append("")
    report.append(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    report.append("## Entorno de ejecución")
    report.append("")
    physical = hardware["physical_cores"] if hardware["physical_cores"] is not None else "No disponible"
    logical = hardware["logical_cores"] if hardware["logical_cores"] is not None else "No disponible"
    ram = f"{hardware['ram_gb']:.1f} GB" if hardware["ram_gb"] else "No disponible"
    report.append(f"- **CPU:** {hardware['cpu']}")
    report.append(f"- **Núcleos físicos:** {physical}")
    report.append(f"- **Núcleos lógicos:** {logical}")
    report.append(f"- **RAM:** {ram}")
    report.append(f"- **Sistema operativo:** {hardware['os']}")
    for name, value in versions:
        report.append(f"- **{name}:** {value}")
    if missing:
        report.append(f"- **CSV faltantes:** {', '.join(missing)}")
    report.append("")

    report.append("## Metodología")
    report.append("")
    report.append(
        "Se ejecutaron 9 algoritmos × 5 tamaños × 3 tipos de arreglo = 135 pruebas por "
        "lenguaje (675 pruebas en total). Para cada prueba se midió el tiempo en "
        "corridas sin contadores: se hicieron 3 repeticiones sobre copias del arreglo "
        "original y se reportó la mediana, para reducir el ruido de mediciones "
        "puntuales. En una corrida aparte se contaron comparaciones e "
        "intercambios. El arreglo base se genera una sola vez por tamaño con un LCG de "
        "semilla fija (123456789) y rango 0..1,000,000, idéntico en los 5 lenguajes; "
        "cada algoritmo trabaja sobre una copia. Antes de medir se hace una corrida de "
        "calentamiento por algoritmo (2,000 elementos) para que la compilación JIT y "
        "los caches de cada runtime no distorsionen las pruebas pequeñas; esa corrida "
        "no se registra ni se mide. Los timeouts se estiman por algoritmo y tipo de "
        "arreglo: Selection Sort es O(n²) siempre y se marca timeout en 1,000,000 "
        "(y en Python también en 100,000). Bubble e Insertion se ejecutan en arreglos "
        "ordenados porque su salida temprana los hace O(n); con entradas aleatorias o "
        "inversas se marcan timeout en 1,000,000 (y en Python también en 100,000)."
    )
    report.append("")
    report.append(
        "El tiempo normalizado se calcula por grupo comparable "
        "(mismo algoritmo, tamaño y tipo de arreglo): se divide el tiempo de cada "
        "lenguaje entre el menor tiempo del grupo y se calcula la media geométrica de "
        "esos cocientes. La media geométrica reduce el peso de valores atípicos y de "
        "pruebas muy pequeñas, de modo que las pruebas lentas no dominan el resultado. "
        "Para comparar lenguajes se usan únicamente grupos completos y balanceados: "
        "algoritmos y tipos de arreglo con estado ok en los 5 lenguajes y en los 5 "
        "tamaños. Así se evita favorecer a un lenguaje solo porque se saltó pruebas "
        "lentas y la mezcla de algoritmos no cambia entre tamaños. Se usa un piso de "
        "0.001 ms para evitar divisiones por cero. "
        "Menor puntaje = más rápido. Las filas timeout/error se excluyen de los "
        "promedios y se muestran en una tabla aparte. Nota: los tiempos con 100 elementos "
        "están cerca de la resolución del reloj y no son confiables para comparar entre lenguajes."
    )
    report.append("")

    report.append("## Resumen ejecutivo")
    report.append("")
    if fastest_language:
        report.append(
            f"- **Lenguaje más rápido:** **{fastest_language['display']}** "
            f"(puntaje normalizado {fmt_ratio(fastest_language['score'])}, "
            f"menor es mejor; {fastest_language['complete_groups']} grupos completos)."
        )
    if fastest_algorithm:
        report.append(
            f"- **Algoritmo más rápido en general:** **{fastest_algorithm['algorithm']}** "
            f"(puntaje normalizado {fmt_ratio(fastest_algorithm['score'])}, "
            f"{fastest_algorithm['wins']} victorias en {fastest_algorithm['coverage']} pruebas)."
        )
    if fastest_random:
        report.append(
            f"- **Más rápido con arreglo aleatorio:** **{fastest_random['algorithm']}** "
            f"(puntaje {fmt_ratio(fastest_random['score'])})."
        )
    if fastest_sorted:
        report.append(
            f"- **Más rápido con arreglo ordenado:** **{fastest_sorted['algorithm']}** "
            f"(puntaje {fmt_ratio(fastest_sorted['score'])})."
        )
    if fastest_inverse:
        report.append(
            f"- **Más rápido con arreglo inverso:** **{fastest_inverse['algorithm']}** "
            f"(puntaje {fmt_ratio(fastest_inverse['score'])})."
        )
    report.append("")

    report.append("## Comparación de lenguajes")
    report.append("")
    language_rows = []
    for item in language_summary:
        language_rows.append(
            [
                item["display"],
                fmt_ratio(item["score"]),
                fmt_time(item["mean_time"]),
                item["ok"],
                item["timeout"],
                item["error"],
                item["complete_groups"],
            ]
        )
    report.append(
        md_table(
            [
                "Lenguaje",
                "Puntaje normalizado (menor=mejor)",
                "Tiempo medio, grupos completos (ms)",
                "Pruebas ok",
                "Timeout",
                "Error",
                "Grupos completos",
            ],
            language_rows,
        )
    )
    report.append("")
    report.append(
        "El puntaje normalizado permite comparar lenguajes aunque algunos tengan "
        "pruebas timeout: solo se usan grupos completos y balanceados. El tiempo "
        "medio de la tercera columna es el promedio bruto de esos mismos grupos."
    )
    report.append("")

    report.append("## Comparación de algoritmos")
    report.append("")
    algorithm_rows = []
    for item in alg_overall:
        algorithm_rows.append(
            [
                item["algorithm"],
                fmt_ratio(item["score"]),
                item["wins"],
                item["coverage"],
                fmt_time(item["mean_time"]),
            ]
        )
    report.append(
        md_table(
            [
                "Algoritmo",
                "Puntaje normalizado (menor=mejor)",
                "Victorias",
                "Pruebas ok",
                "Tiempo medio (ms)",
            ],
            algorithm_rows,
        )
    )
    report.append("")
    report.append(
        "El puntaje de algoritmos se calcula dentro de cada grupo "
        "(lenguaje, tamaño, tipo): se compara cada algoritmo contra el más rápido "
        "de ese grupo y se calcula la media geométrica de los cocientes. Las "
        "victorias son los grupos donde el algoritmo fue el más rápido (puede haber "
        "empates)."
    )
    report.append("")

    for title, summary in [
        ("Aleatorio", alg_random),
        ("Ordenado", alg_sorted),
        ("Inverso", alg_inverse),
    ]:
        report.append(f"### Algoritmos con arreglo {title.lower()}")
        report.append("")
        rows_for_type = []
        for item in summary:
            rows_for_type.append(
                [
                    item["algorithm"],
                    fmt_ratio(item["score"]),
                    item["wins"],
                    item["coverage"],
                ]
            )
        report.append(
            md_table(
                ["Algoritmo", "Puntaje normalizado", "Victorias", "Pruebas ok"],
                rows_for_type,
            )
        )
        report.append("")

    report.append("## Tablas comparativas por algoritmo y tamaño")
    report.append("")
    size_headers = ["Algoritmo"] + [f"{size:,}".replace(",", ".") for size in SIZES]

    report.append("### Tiempo promedio (ms) - Todos los tipos de arreglo")
    report.append("")
    report.append(md_table(size_headers, pivot_metric(ok_rows, "tiempo_ms", integer=False)))
    report.append("")
    report.append("*solo incluye arreglo ordenado; aleatorio e inverso fueron timeout*" if any("parcial*" in str(c) for row in pivot_metric(ok_rows, "tiempo_ms", integer=False) for c in row) else "")
    if any("parcial*" in str(c) for row in pivot_metric(ok_rows, "tiempo_ms", integer=False) for c in row):
        report.append("")
        report.append("*solo incluye arreglo ordenado; aleatorio e inverso fueron timeout*")
        report.append("")

    report.append("### Comparaciones promedio - Todos los tipos de arreglo")
    report.append("")
    report.append(
        md_table(size_headers, pivot_metric(ok_rows, "comparaciones", integer=True))
    )
    report.append("")

    report.append("### Intercambios promedio - Todos los tipos de arreglo")
    report.append("")
    report.append(
        md_table(size_headers, pivot_metric(ok_rows, "intercambios", integer=True))
    )
    report.append("")
    report.append(
        "Las tablas anteriores promedian todos los tests ok (todos los lenguajes y "
        "tipos de arreglo) para cada algoritmo y tamaño. Las celdas con «—» indican "
        "que no hubo pruebas ok (por ejemplo, timeouts estimados)."
    )
    report.append("")

    # Tables by array type
    for arr_type, title in [("aleatorio", "aleatorio"), ("ordenado", "ordenado"), ("inverso", "inverso")]:
        report.append(f"### Tiempo promedio (ms) - Arreglo {title}")
        report.append("")
        type_rows = []
        for algorithm in ALGORITHMS:
            values = [algorithm]
            for size in SIZES:
                subset = [
                    row["tiempo_ms"]
                    for row in ok_rows
                    if row["algoritmo"] == algorithm and row["tamano"] == size and row["tipo"] == arr_type
                ]
                if not subset:
                    values.append("—")
                else:
                    values.append(fmt_time(mean(subset)))
            type_rows.append(values)
        report.append(md_table(size_headers, type_rows))
        report.append("")

    report.append("### Tiempo promedio por lenguaje y tamaño (grupos completos)")
    report.append("")
    report.append(
        md_table(
            ["Lenguaje"] + [f"{size:,}".replace(",", ".") for size in SIZES],
            language_size_table(complete_keys, algorithm_groups),
        )
    )
    report.append("")
    report.append(
        "Se usan los mismos algoritmos y tipos de arreglo en todos los tamaños "
        "(grupos completos y balanceados), de modo que los valores sean comparables "
        "entre filas y columnas."
    )
    report.append("")

    report.append("## Pruebas con timeout o error")
    report.append("")
    if bad_rows:
        bad_counter = Counter((row["lenguaje"], row["estado"]) for row in bad_rows)
        summary_rows = []
        for language_key, display in LANGUAGES:
            summary_rows.append(
                [
                    display,
                    bad_counter.get((language_key, "timeout"), 0),
                    bad_counter.get((language_key, "error"), 0),
                ]
            )
        report.append(md_table(["Lenguaje", "Timeout", "Error"], summary_rows))
        report.append("")
        report.append(
            "Detalle de las pruebas no exitosas (se excluyeron de todos los promedios):"
        )
        report.append("")
        bad_sorted = sorted(
            bad_rows,
            key=lambda row: (
                LANGUAGE_ORDER.get(row["lenguaje"], 99),
                row["tamano"],
                ALGORITHMS.index(row["algoritmo"]),
                TYPES.index(row["tipo"]),
            ),
        )
        detail_rows = [
            [
                LANGUAGE_DISPLAY.get(row["lenguaje"], row["lenguaje"]),
                row["algoritmo"],
                f"{row['tamano']:,}".replace(",", "."),
                row["tipo"],
                row["estado"],
            ]
            for row in bad_sorted
        ]
        report.append(
            md_table(
                ["Lenguaje", "Algoritmo", "Tamaño", "Tipo de arreglo", "Estado"],
                detail_rows,
            )
        )
    else:
        report.append("No hubo pruebas con timeout ni error.")
    report.append("")

    report.append("## Gráficas")
    report.append("")
    report.append("![Tiempo por algoritmo](grafica_tiempo_algoritmo.png)")
    report.append("")
    report.append("![Tiempo por lenguaje](grafica_tiempo_lenguaje.png)")
    report.append("")
    report.append("![Tiempo normalizado por lenguaje](grafica_tiempo_normalizado_lenguaje.png)")
    report.append("")

    report.append("## Anexo: tiempo promedio (ms) por lenguaje, algoritmo y tamaño")
    report.append("")
    for display, table in per_language_time_tables(ok_rows):
        report.append(f"### {display}")
        report.append("")
        report.append(table)
        report.append("")

    report.append("## Conclusiones")
    report.append("")
    if fastest_language:
        report.append(
            f"- El lenguaje más rápido, según el tiempo promedio normalizado sobre "
            f"grupos completos y balanceados, es **{fastest_language['display']}** "
            f"(puntaje {fmt_ratio(fastest_language['score'])})."
        )
    if fastest_algorithm:
        report.append(
            f"- El algoritmo más rápido en general es **{fastest_algorithm['algorithm']}** "
            f"(puntaje {fmt_ratio(fastest_algorithm['score'])})."
        )
    if fastest_random and fastest_sorted and fastest_inverse:
        report.append(
            f"- Por tipo de entrada: aleatorio → **{fastest_random['algorithm']}**, "
            f"ordenado → **{fastest_sorted['algorithm']}**, "
            f"inverso → **{fastest_inverse['algorithm']}**."
        )
    if fastest_sorted and fastest_sorted["algorithm"] == "Bubble Sort":
        report.append(
            "- Bubble Sort incluye salida temprana: en un arreglo ya ordenado hace "
            "solo O(n) comparaciones y ningún intercambio, por eso resulta el más "
            "rápido para ese tipo de entrada."
        )
    # For 1,000,000, show fastest per language with complete data
    report.append("- **Tamaño 1,000,000 - Algoritmo más rápido por lenguaje (con datos completos):**")
    ok_rows_1m = [row for row in rows if row["estado"] == "ok" and row["tamano"] == 1000000]
    for lang_key, lang_disp in LANGUAGES:
        lang_rows_1m = [r for r in ok_rows_1m if r["lenguaje"] == lang_key]
        # Check if has all 3 types for all algorithms? Or just find best algorithm with all 3 types
        algo_times = {}
        for algo in ALGORITHMS:
            values = []
            for t in TYPES:
                subset = [r["tiempo_ms"] for r in lang_rows_1m if r["algoritmo"] == algo and r["tipo"] == t]
                if not subset:
                    break
                values.append(mean(subset))
            else:
                if values:
                    algo_times[algo] = mean(values)
        if algo_times:
            best_algo = min(algo_times, key=algo_times.get)
            report.append(f"  - {lang_disp}: **{best_algo}** ({fmt_time(algo_times[best_algo])} ms)")
        else:
            report.append(f"  - {lang_disp}: Sin datos completos")
    report.append("- El promedio bruto entre lenguajes está dominado por Python y por eso no se usa para concluir.")
    timeout_total = sum(1 for row in bad_rows if row["estado"] == "timeout")
    error_total = sum(1 for row in bad_rows if row["estado"] == "error")
    report.append(
        f"- Se registraron {timeout_total} timeouts y {error_total} errores de un total "
        f"de {len(rows)} pruebas. Los timeouts corresponden principalmente a "
        f"Bubble/Selection/Insertion en tamaños grandes, estimados antes de ejecutar."
    )
    report.append(
        "- Radix Sort registra 0 comparaciones por diseño (no compara elementos). "
        "En Merge, Radix y Bucket los movimientos/escrituras se cuentan como "
        "intercambios, según la convención documentada en cada programa."
    )
    report.append("")

    report_path = os.path.join(ROOT, "reporte.md")
    with open(report_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(report))

    print("Reporte generado en %s" % report_path)
    if fastest_language:
        print("Lenguaje más rápido: %s (puntaje %.3f)" % (
            fastest_language["display"], fastest_language["score"]))
    if fastest_algorithm:
        print("Algoritmo más rápido: %s (puntaje %.3f)" % (
            fastest_algorithm["algorithm"], fastest_algorithm["score"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
