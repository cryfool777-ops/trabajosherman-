# -*- coding: utf-8 -*-
"""
Benchmark de 9 algoritmos de ordenamiento en Python.

Convencion de conteo (valida para los 5 lenguajes):
  * Comparacion: cada comparacion entre dos elementos del arreglo.
  * Intercambio: cada swap de dos elementos.
  * Insertion sort se implementa con swaps reales para que "intercambios" sea
    el numero de swaps efectuados.
  * Merge sort: se cuenta cada escritura en el arreglo auxiliar y cada
    escritura de vuelta al arreglo principal como un movimiento/intercambio.
  * Radix sort: no compara elementos, por lo tanto registra 0 comparaciones.
    Cada escritura en el arreglo destino y la copia final cuentan como
    movimientos/intercambios.
  * Bucket sort: se cuentan las comparaciones de la ordenacion interna
    (insercion) de cada cubeta. Cada desplazamiento interno, la colocacion de
    la clave y la escritura final de la cubeta al arreglo cuentan como
    movimientos/intercambios.

El tiempo se mide en una corrida SIN contadores. Los conteos se obtienen en
una corrida aparte con las versiones instrumentadas.
"""

import csv
import sys
import time

sys.setrecursionlimit(1000000)

LANGUAGE = "python"
SIZES = [100, 1000, 10000, 100000, 1000000]
TYPES = ["aleatorio", "ordenado", "inverso"]
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
SLOW_ALGORITHMS = {0, 1, 2}  # Bubble, Selection, Insertion
VALUE_LIMIT = 1000001
RANDOM_SEED = 123456789


class Counter:
    __slots__ = ("comparisons", "swaps")

    def __init__(self):
        self.comparisons = 0
        self.swaps = 0


# ---------------------------------------------------------------------------
# Generacion reproducible de datos (LCG identico en los 5 lenguajes)
# ---------------------------------------------------------------------------
def generate_random(n):
    values = [0] * n
    state = RANDOM_SEED
    for i in range(n):
        state = (state * 1664525 + 1013904223) & 0xFFFFFFFF
        values[i] = state % VALUE_LIMIT
    return values


def is_sorted(values):
    for i in range(1, len(values)):
        if values[i - 1] > values[i]:
            return False
    return True


# ---------------------------------------------------------------------------
# Version sin contadores (solo para medir tiempo)
# ---------------------------------------------------------------------------
def bubble_sort(a):
    n = len(a)
    end = n - 1
    while end > 0:
        swapped = False
        for i in range(end):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True
        if not swapped:
            break
        end -= 1


def selection_sort(a):
    n = len(a)
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            if a[j] < a[m]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]


def insertion_sort(a):
    n = len(a)
    for i in range(1, n):
        j = i
        while j > 0:
            if a[j - 1] <= a[j]:
                break
            a[j - 1], a[j] = a[j], a[j - 1]
            j -= 1


def merge_sort(a):
    n = len(a)
    if n < 2:
        return
    aux = [0] * n
    _merge_sort(a, aux, 0, n - 1)


def _merge_sort(a, aux, lo, hi):
    if lo >= hi:
        return
    mid = (lo + hi) // 2
    _merge_sort(a, aux, lo, mid)
    _merge_sort(a, aux, mid + 1, hi)
    for i in range(lo, hi + 1):
        aux[i] = a[i]
    i, j, k = lo, mid + 1, lo
    while i <= mid and j <= hi:
        if aux[i] <= aux[j]:
            a[k] = aux[i]
            i += 1
        else:
            a[k] = aux[j]
            j += 1
        k += 1
    while i <= mid:
        a[k] = aux[i]
        i += 1
        k += 1
    while j <= hi:
        a[k] = aux[j]
        j += 1
        k += 1


def shell_sort(a):
    n = len(a)
    gap = 1
    while gap < n // 3:
        gap = gap * 3 + 1
    while gap >= 1:
        for i in range(gap, n):
            j = i
            while j >= gap:
                if a[j - gap] <= a[j]:
                    break
                a[j - gap], a[j] = a[j], a[j - gap]
                j -= gap
        gap //= 3


def bucket_sort(a):
    n = len(a)
    if n < 2:
        return
    buckets_count = min(n, 100000)
    buckets = [[] for _ in range(buckets_count)]
    for value in a:
        buckets[value * buckets_count // VALUE_LIMIT].append(value)
    k = 0
    for bucket in buckets:
        m = len(bucket)
        for i in range(1, m):
            key = bucket[i]
            j = i - 1
            while j >= 0 and bucket[j] > key:
                bucket[j + 1] = bucket[j]
                j -= 1
            bucket[j + 1] = key
        for value in bucket:
            a[k] = value
            k += 1


def quick_sort(a):
    n = len(a)
    if n > 1:
        _quick_sort(a, 0, n - 1)


def _quick_sort(a, lo, hi):
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if a[mid] < a[lo]:
            a[lo], a[mid] = a[mid], a[lo]
        if a[hi] < a[lo]:
            a[lo], a[hi] = a[hi], a[lo]
        if a[hi] < a[mid]:
            a[mid], a[hi] = a[hi], a[mid]
        a[mid], a[hi] = a[hi], a[mid]
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        p = i
        if p - lo < hi - p:
            _quick_sort(a, lo, p - 1)
            lo = p + 1
        else:
            _quick_sort(a, p + 1, hi)
            hi = p - 1


def radix_sort(a):
    n = len(a)
    if n < 2:
        return
    src = a
    dst = [0] * n
    for shift in (0, 8, 16):
        count = [0] * 256
        for value in src:
            count[(value >> shift) & 255] += 1
        total = 0
        for i in range(256):
            c = count[i]
            count[i] = total
            total += c
        for value in src:
            digit = (value >> shift) & 255
            dst[count[digit]] = value
            count[digit] += 1
        src, dst = dst, src
    if src is not a:
        a[:] = src


def heap_sort(a):
    n = len(a)
    for start in range(n // 2 - 1, -1, -1):
        _sift_down(a, start, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        _sift_down(a, 0, end)


def _sift_down(a, root, n):
    while True:
        child = 2 * root + 1
        if child >= n:
            break
        if child + 1 < n and a[child + 1] > a[child]:
            child += 1
        if a[root] >= a[child]:
            break
        a[root], a[child] = a[child], a[root]
        root = child


# ---------------------------------------------------------------------------
# Versiones instrumentadas (solo para contar)
# ---------------------------------------------------------------------------
def bubble_sort_count(a, c):
    n = len(a)
    end = n - 1
    while end > 0:
        swapped = False
        for i in range(end):
            c.comparisons += 1
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                c.swaps += 1
                swapped = True
        if not swapped:
            break
        end -= 1


def selection_sort_count(a, c):
    n = len(a)
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            c.comparisons += 1
            if a[j] < a[m]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]
            c.swaps += 1


def insertion_sort_count(a, c):
    n = len(a)
    for i in range(1, n):
        j = i
        while j > 0:
            c.comparisons += 1
            if a[j - 1] <= a[j]:
                break
            a[j - 1], a[j] = a[j], a[j - 1]
            c.swaps += 1
            j -= 1


def merge_sort_count(a, c):
    n = len(a)
    if n < 2:
        return
    aux = [0] * n
    _merge_sort_count(a, aux, 0, n - 1, c)


def _merge_sort_count(a, aux, lo, hi, c):
    if lo >= hi:
        return
    mid = (lo + hi) // 2
    _merge_sort_count(a, aux, lo, mid, c)
    _merge_sort_count(a, aux, mid + 1, hi, c)
    for i in range(lo, hi + 1):
        aux[i] = a[i]
        c.swaps += 1
    i, j, k = lo, mid + 1, lo
    while i <= mid and j <= hi:
        c.comparisons += 1
        if aux[i] <= aux[j]:
            a[k] = aux[i]
            i += 1
        else:
            a[k] = aux[j]
            j += 1
        c.swaps += 1
        k += 1
    while i <= mid:
        a[k] = aux[i]
        i += 1
        k += 1
        c.swaps += 1
    while j <= hi:
        a[k] = aux[j]
        j += 1
        k += 1
        c.swaps += 1


def shell_sort_count(a, c):
    n = len(a)
    gap = 1
    while gap < n // 3:
        gap = gap * 3 + 1
    while gap >= 1:
        for i in range(gap, n):
            j = i
            while j >= gap:
                c.comparisons += 1
                if a[j - gap] <= a[j]:
                    break
                a[j - gap], a[j] = a[j], a[j - gap]
                c.swaps += 1
                j -= gap
        gap //= 3


def bucket_sort_count(a, c):
    n = len(a)
    if n < 2:
        return
    buckets_count = min(n, 100000)
    buckets = [[] for _ in range(buckets_count)]
    for value in a:
        buckets[value * buckets_count // VALUE_LIMIT].append(value)
    k = 0
    for bucket in buckets:
        m = len(bucket)
        for i in range(1, m):
            key = bucket[i]
            j = i - 1
            while j >= 0:
                c.comparisons += 1
                if bucket[j] <= key:
                    break
                bucket[j + 1] = bucket[j]
                c.swaps += 1
                j -= 1
            bucket[j + 1] = key
            c.swaps += 1
        for value in bucket:
            a[k] = value
            c.swaps += 1
            k += 1


def quick_sort_count(a, c):
    n = len(a)
    if n > 1:
        _quick_sort_count(a, 0, n - 1, c)


def _quick_sort_count(a, lo, hi, c):
    while lo < hi:
        mid = lo + (hi - lo) // 2
        c.comparisons += 1
        if a[mid] < a[lo]:
            a[lo], a[mid] = a[mid], a[lo]
            c.swaps += 1
        c.comparisons += 1
        if a[hi] < a[lo]:
            a[lo], a[hi] = a[hi], a[lo]
            c.swaps += 1
        c.comparisons += 1
        if a[hi] < a[mid]:
            a[mid], a[hi] = a[hi], a[mid]
            c.swaps += 1
        a[mid], a[hi] = a[hi], a[mid]
        c.swaps += 1
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            c.comparisons += 1
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                c.swaps += 1
                i += 1
        a[i], a[hi] = a[hi], a[i]
        c.swaps += 1
        p = i
        if p - lo < hi - p:
            _quick_sort_count(a, lo, p - 1, c)
            lo = p + 1
        else:
            _quick_sort_count(a, p + 1, hi, c)
            hi = p - 1


def radix_sort_count(a, c):
    n = len(a)
    if n < 2:
        return
    src = a
    dst = [0] * n
    for shift in (0, 8, 16):
        count = [0] * 256
        for value in src:
            count[(value >> shift) & 255] += 1
        total = 0
        for i in range(256):
            x = count[i]
            count[i] = total
            total += x
        for value in src:
            digit = (value >> shift) & 255
            dst[count[digit]] = value
            count[digit] += 1
            c.swaps += 1
        src, dst = dst, src
    if src is not a:
        for i in range(n):
            a[i] = src[i]
            c.swaps += 1


def heap_sort_count(a, c):
    n = len(a)
    for start in range(n // 2 - 1, -1, -1):
        _sift_down_count(a, start, n, c)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        c.swaps += 1
        _sift_down_count(a, 0, end, c)


def _sift_down_count(a, root, n, c):
    while True:
        child = 2 * root + 1
        if child >= n:
            break
        if child + 1 < n:
            c.comparisons += 1
            if a[child + 1] > a[child]:
                child += 1
        c.comparisons += 1
        if a[root] >= a[child]:
            break
        a[root], a[child] = a[child], a[root]
        c.swaps += 1
        root = child


CLEAN = [
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    shell_sort,
    bucket_sort,
    quick_sort,
    radix_sort,
    heap_sort,
]

COUNTED = [
    bubble_sort_count,
    selection_sort_count,
    insertion_sort_count,
    merge_sort_count,
    shell_sort_count,
    bucket_sort_count,
    quick_sort_count,
    radix_sort_count,
    heap_sort_count,
]


def should_timeout(algorithm_index, n, array_type_index):
    if algorithm_index not in SLOW_ALGORITHMS:
        return False
    if n < 100000:
        return False
    ordered_input = array_type_index == 1
    # Selection siempre es O(n^2). Bubble e Insertion son O(n) cuando el
    # arreglo ya esta ordenado gracias a la salida temprana.
    if algorithm_index == 1:
        if n >= 1000000:
            return True
        return n >= 100000 and LANGUAGE == "python"
    if ordered_input:
        return False
    if n >= 1000000:
        return True
    # Estimacion para Python: Bubble/Insertion con 100k desordenados superan
    # ampliamente los 10 minutos (aprox. 5e9 operaciones de bytecode).
    return n >= 100000 and LANGUAGE == "python"


def main():
    output_path = "resultados_%s.csv" % LANGUAGE
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "lenguaje",
                "algoritmo",
                "tamano",
                "tipo_arreglo",
                "tiempo_ms",
                "comparaciones",
                "intercambios",
                "estado",
            ]
        )

        # Calentamiento (no se mide): activa JIT/caches antes de las pruebas.
        warm_base = generate_random(2000)
        for warm_func in CLEAN:
            warm_func(list(warm_base))

        for n in SIZES:
            base = generate_random(n)
            ordered = sorted(base)
            inverse = ordered[::-1]
            sources = [base, ordered, inverse]

            for ai, algorithm in enumerate(ALGORITHMS):
                for ti, array_type in enumerate(TYPES):
                    if should_timeout(ai, n, ti):
                        writer.writerow(
                            [LANGUAGE, algorithm, n, array_type, "0.000000", 0, 0, "timeout"]
                        )
                        continue

                    source = sources[ti]
                    counted = list(source)

                    try:
                        samples = []
                        valid = True
                        for _ in range(3):
                            timed = list(source)
                            start = time.perf_counter()
                            CLEAN[ai](timed)
                            samples.append((time.perf_counter() - start) * 1000.0)
                            if not is_sorted(timed):
                                valid = False
                                break

                        if not valid:
                            writer.writerow(
                                [LANGUAGE, algorithm, n, array_type, "0.000000", 0, 0, "error"]
                            )
                            continue

                        samples.sort()
                        elapsed_ms = samples[1]

                        counter = Counter()
                        COUNTED[ai](counted, counter)

                        if not is_sorted(counted):
                            writer.writerow(
                                [LANGUAGE, algorithm, n, array_type, "%.6f" % elapsed_ms, 0, 0, "error"]
                            )
                            continue

                        writer.writerow(
                            [
                                LANGUAGE,
                                algorithm,
                                n,
                                array_type,
                                "%.6f" % elapsed_ms,
                                counter.comparisons,
                                counter.swaps,
                                "ok",
                            ]
                        )
                    except Exception:
                        writer.writerow(
                            [LANGUAGE, algorithm, n, array_type, "0.000000", 0, 0, "error"]
                        )

    print("Resultados escritos en %s" % output_path)


if __name__ == "__main__":
    main()
