// Benchmark de 9 algoritmos de ordenamiento en JavaScript (Node.js).
//
// Convencion de conteo (valida para los 5 lenguajes):
//   * Comparacion: cada comparacion entre dos elementos del arreglo.
//   * Intercambio: cada swap de dos elementos.
//   * Insertion sort se implementa con swaps reales para que "intercambios"
//     sea el numero de swaps efectuados.
//   * Merge sort: se cuenta cada escritura en el arreglo auxiliar y cada
//     escritura de vuelta al arreglo principal como un movimiento/intercambio.
//   * Radix sort: no compara elementos, por lo tanto registra 0 comparaciones.
//     Cada escritura en el arreglo destino y la copia final cuentan como
//     movimientos/intercambios.
//   * Bucket sort: se cuentan las comparaciones de la ordenacion interna
//     (insercion) de cada cubeta. Cada desplazamiento interno, la colocacion de
//     la clave y la escritura final de la cubeta al arreglo cuentan como
//     movimientos/intercambios.
//
// El tiempo se mide en una corrida SIN contadores. Los conteos se obtienen en
// una corrida aparte con las versiones instrumentadas.

"use strict";

const fs = require("fs");

const LANGUAGE = "javascript";
const SIZES = [100, 1000, 10000, 100000, 1000000];
const TYPES = ["aleatorio", "ordenado", "inverso"];
const ALGORITHMS = [
    "Bubble Sort",
    "Selection Sort",
    "Insertion Sort",
    "Merge Sort",
    "Shell Sort",
    "Bucket Sort",
    "Quick Sort",
    "Radix Sort",
    "Heap Sort",
];
const ALGORITHM_COUNT = 9;
const VALUE_LIMIT = 1000001;
const RANDOM_SEED = 123456789;

class Counter {
    constructor() {
        this.comparisons = 0;
        this.swaps = 0;
    }
}

function swap(a, i, j) {
    const tmp = a[i];
    a[i] = a[j];
    a[j] = tmp;
}

// ---------------------------------------------------------------------------
// Generacion reproducible de datos (LCG identico en los 5 lenguajes)
// ---------------------------------------------------------------------------
function generateRandom(n) {
    const values = new Array(n);
    let state = RANDOM_SEED;
    for (let i = 0; i < n; ++i) {
        state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
        values[i] = state % VALUE_LIMIT;
    }
    return values;
}

function isSorted(values) {
    for (let i = 1; i < values.length; ++i) {
        if (values[i - 1] > values[i]) return false;
    }
    return true;
}

// ---------------------------------------------------------------------------
// Version sin contadores (solo para medir tiempo)
// ---------------------------------------------------------------------------
function bubbleSort(a) {
    let end = a.length - 1;
    while (end > 0) {
        let swapped = false;
        for (let i = 0; i < end; ++i) {
            if (a[i] > a[i + 1]) {
                swap(a, i, i + 1);
                swapped = true;
            }
        }
        if (!swapped) break;
        --end;
    }
}

function selectionSort(a) {
    const n = a.length;
    for (let i = 0; i < n - 1; ++i) {
        let m = i;
        for (let j = i + 1; j < n; ++j) {
            if (a[j] < a[m]) m = j;
        }
        if (m !== i) swap(a, i, m);
    }
}

function insertionSort(a) {
    const n = a.length;
    for (let i = 1; i < n; ++i) {
        let j = i;
        while (j > 0) {
            if (a[j - 1] <= a[j]) break;
            swap(a, j - 1, j);
            --j;
        }
    }
}

function mergeSortRec(a, aux, lo, hi) {
    if (lo >= hi) return;
    const mid = lo + ((hi - lo) >> 1);
    mergeSortRec(a, aux, lo, mid);
    mergeSortRec(a, aux, mid + 1, hi);
    for (let i = lo; i <= hi; ++i) aux[i] = a[i];
    let i = lo;
    let j = mid + 1;
    let k = lo;
    while (i <= mid && j <= hi) {
        if (aux[i] <= aux[j]) {
            a[k] = aux[i];
            ++i;
        } else {
            a[k] = aux[j];
            ++j;
        }
        ++k;
    }
    while (i <= mid) {
        a[k] = aux[i];
        ++i;
        ++k;
    }
    while (j <= hi) {
        a[k] = aux[j];
        ++j;
        ++k;
    }
}

function mergeSort(a) {
    const n = a.length;
    if (n < 2) return;
    const aux = new Array(n);
    mergeSortRec(a, aux, 0, n - 1);
}

function shellSort(a) {
    const n = a.length;
    let gap = 1;
    while (gap < Math.floor(n / 3)) gap = gap * 3 + 1;
    while (gap >= 1) {
        for (let i = gap; i < n; ++i) {
            let j = i;
            while (j >= gap) {
                if (a[j - gap] <= a[j]) break;
                swap(a, j - gap, j);
                j -= gap;
            }
        }
        gap = Math.floor(gap / 3);
    }
}

function bucketSort(a) {
    const n = a.length;
    if (n < 2) return;
    const bucketsCount = Math.min(n, 100000);
    const buckets = new Array(bucketsCount);
    for (let i = 0; i < bucketsCount; ++i) buckets[i] = [];
    for (let i = 0; i < n; ++i) {
        const value = a[i];
        const idx = Math.floor((value * bucketsCount) / VALUE_LIMIT);
        buckets[idx].push(value);
    }
    let k = 0;
    for (const bucket of buckets) {
        const m = bucket.length;
        for (let i = 1; i < m; ++i) {
            const key = bucket[i];
            let j = i - 1;
            while (j >= 0 && bucket[j] > key) {
                bucket[j + 1] = bucket[j];
                --j;
            }
            bucket[j + 1] = key;
        }
        for (const value of bucket) a[k++] = value;
    }
}

function quickSortRec(a, lo, hi) {
    while (lo < hi) {
        const mid = lo + ((hi - lo) >> 1);
        if (a[mid] < a[lo]) swap(a, lo, mid);
        if (a[hi] < a[lo]) swap(a, lo, hi);
        if (a[hi] < a[mid]) swap(a, mid, hi);
        swap(a, mid, hi);
        const pivot = a[hi];
        let i = lo;
        for (let j = lo; j < hi; ++j) {
            if (a[j] < pivot) {
                swap(a, i, j);
                ++i;
            }
        }
        swap(a, i, hi);
        const p = i;
        if (p - lo < hi - p) {
            quickSortRec(a, lo, p - 1);
            lo = p + 1;
        } else {
            quickSortRec(a, p + 1, hi);
            hi = p - 1;
        }
    }
}

function quickSort(a) {
    if (a.length > 1) quickSortRec(a, 0, a.length - 1);
}

function radixSort(a) {
    const n = a.length;
    if (n < 2) return;
    let src = a;
    let dst = new Array(n);
    for (const shift of [0, 8, 16]) {
        const count = new Array(256).fill(0);
        for (let i = 0; i < n; ++i) ++count[(src[i] >> shift) & 255];
        let total = 0;
        for (let i = 0; i < 256; ++i) {
            const x = count[i];
            count[i] = total;
            total += x;
        }
        for (let i = 0; i < n; ++i) {
            const value = src[i];
            const digit = (value >> shift) & 255;
            dst[count[digit]++] = value;
        }
        const tmp = src;
        src = dst;
        dst = tmp;
    }
    if (src !== a) {
        for (let i = 0; i < n; ++i) a[i] = src[i];
    }
}

function siftDown(a, root, n) {
    while (true) {
        let child = 2 * root + 1;
        if (child >= n) break;
        if (child + 1 < n && a[child + 1] > a[child]) ++child;
        if (a[root] >= a[child]) break;
        swap(a, root, child);
        root = child;
    }
}

function heapSort(a) {
    const n = a.length;
    for (let start = Math.floor(n / 2) - 1; start >= 0; --start) siftDown(a, start, n);
    for (let end = n - 1; end > 0; --end) {
        swap(a, 0, end);
        siftDown(a, 0, end);
    }
}

// ---------------------------------------------------------------------------
// Versiones instrumentadas (solo para contar)
// ---------------------------------------------------------------------------
function bubbleSortCount(a, c) {
    let end = a.length - 1;
    while (end > 0) {
        let swapped = false;
        for (let i = 0; i < end; ++i) {
            ++c.comparisons;
            if (a[i] > a[i + 1]) {
                swap(a, i, i + 1);
                ++c.swaps;
                swapped = true;
            }
        }
        if (!swapped) break;
        --end;
    }
}

function selectionSortCount(a, c) {
    const n = a.length;
    for (let i = 0; i < n - 1; ++i) {
        let m = i;
        for (let j = i + 1; j < n; ++j) {
            ++c.comparisons;
            if (a[j] < a[m]) m = j;
        }
        if (m !== i) {
            swap(a, i, m);
            ++c.swaps;
        }
    }
}

function insertionSortCount(a, c) {
    const n = a.length;
    for (let i = 1; i < n; ++i) {
        let j = i;
        while (j > 0) {
            ++c.comparisons;
            if (a[j - 1] <= a[j]) break;
            swap(a, j - 1, j);
            ++c.swaps;
            --j;
        }
    }
}

function mergeSortRecCount(a, aux, lo, hi, c) {
    if (lo >= hi) return;
    const mid = lo + ((hi - lo) >> 1);
    mergeSortRecCount(a, aux, lo, mid, c);
    mergeSortRecCount(a, aux, mid + 1, hi, c);
    for (let i = lo; i <= hi; ++i) {
        aux[i] = a[i];
        ++c.swaps;
    }
    let i = lo;
    let j = mid + 1;
    let k = lo;
    while (i <= mid && j <= hi) {
        ++c.comparisons;
        if (aux[i] <= aux[j]) {
            a[k] = aux[i];
            ++i;
        } else {
            a[k] = aux[j];
            ++j;
        }
        ++c.swaps;
        ++k;
    }
    while (i <= mid) {
        a[k] = aux[i];
        ++i;
        ++k;
        ++c.swaps;
    }
    while (j <= hi) {
        a[k] = aux[j];
        ++j;
        ++k;
        ++c.swaps;
    }
}

function mergeSortCount(a, c) {
    const n = a.length;
    if (n < 2) return;
    const aux = new Array(n);
    mergeSortRecCount(a, aux, 0, n - 1, c);
}

function shellSortCount(a, c) {
    const n = a.length;
    let gap = 1;
    while (gap < Math.floor(n / 3)) gap = gap * 3 + 1;
    while (gap >= 1) {
        for (let i = gap; i < n; ++i) {
            let j = i;
            while (j >= gap) {
                ++c.comparisons;
                if (a[j - gap] <= a[j]) break;
                swap(a, j - gap, j);
                ++c.swaps;
                j -= gap;
            }
        }
        gap = Math.floor(gap / 3);
    }
}

function bucketSortCount(a, c) {
    const n = a.length;
    if (n < 2) return;
    const bucketsCount = Math.min(n, 100000);
    const buckets = new Array(bucketsCount);
    for (let i = 0; i < bucketsCount; ++i) buckets[i] = [];
    for (let i = 0; i < n; ++i) {
        const value = a[i];
        const idx = Math.floor((value * bucketsCount) / VALUE_LIMIT);
        buckets[idx].push(value);
    }
    let k = 0;
    for (const bucket of buckets) {
        const m = bucket.length;
        for (let i = 1; i < m; ++i) {
            const key = bucket[i];
            let j = i - 1;
            while (j >= 0) {
                ++c.comparisons;
                if (bucket[j] <= key) break;
                bucket[j + 1] = bucket[j];
                ++c.swaps;
                --j;
            }
            bucket[j + 1] = key;
            ++c.swaps;
        }
        for (const value of bucket) {
            a[k++] = value;
            ++c.swaps;
        }
    }
}

function quickSortRecCount(a, lo, hi, c) {
    while (lo < hi) {
        const mid = lo + ((hi - lo) >> 1);
        ++c.comparisons;
        if (a[mid] < a[lo]) {
            swap(a, lo, mid);
            ++c.swaps;
        }
        ++c.comparisons;
        if (a[hi] < a[lo]) {
            swap(a, lo, hi);
            ++c.swaps;
        }
        ++c.comparisons;
        if (a[hi] < a[mid]) {
            swap(a, mid, hi);
            ++c.swaps;
        }
        swap(a, mid, hi);
        ++c.swaps;
        const pivot = a[hi];
        let i = lo;
        for (let j = lo; j < hi; ++j) {
            ++c.comparisons;
            if (a[j] < pivot) {
                swap(a, i, j);
                ++c.swaps;
                ++i;
            }
        }
        swap(a, i, hi);
        ++c.swaps;
        const p = i;
        if (p - lo < hi - p) {
            quickSortRecCount(a, lo, p - 1, c);
            lo = p + 1;
        } else {
            quickSortRecCount(a, p + 1, hi, c);
            hi = p - 1;
        }
    }
}

function quickSortCount(a, c) {
    if (a.length > 1) quickSortRecCount(a, 0, a.length - 1, c);
}

function radixSortCount(a, c) {
    const n = a.length;
    if (n < 2) return;
    let src = a;
    let dst = new Array(n);
    for (const shift of [0, 8, 16]) {
        const count = new Array(256).fill(0);
        for (let i = 0; i < n; ++i) ++count[(src[i] >> shift) & 255];
        let total = 0;
        for (let i = 0; i < 256; ++i) {
            const x = count[i];
            count[i] = total;
            total += x;
        }
        for (let i = 0; i < n; ++i) {
            const value = src[i];
            const digit = (value >> shift) & 255;
            dst[count[digit]++] = value;
            ++c.swaps;
        }
        const tmp = src;
        src = dst;
        dst = tmp;
    }
    if (src !== a) {
        for (let i = 0; i < n; ++i) {
            a[i] = src[i];
            ++c.swaps;
        }
    }
}

function siftDownCount(a, root, n, c) {
    while (true) {
        let child = 2 * root + 1;
        if (child >= n) break;
        if (child + 1 < n) {
            ++c.comparisons;
            if (a[child + 1] > a[child]) ++child;
        }
        ++c.comparisons;
        if (a[root] >= a[child]) break;
        swap(a, root, child);
        ++c.swaps;
        root = child;
    }
}

function heapSortCount(a, c) {
    const n = a.length;
    for (let start = Math.floor(n / 2) - 1; start >= 0; --start) siftDownCount(a, start, n, c);
    for (let end = n - 1; end > 0; --end) {
        swap(a, 0, end);
        ++c.swaps;
        siftDownCount(a, 0, end, c);
    }
}

// ---------------------------------------------------------------------------
// Dispatch y programa principal
// ---------------------------------------------------------------------------
const CLEAN = [
    bubbleSort,
    selectionSort,
    insertionSort,
    mergeSort,
    shellSort,
    bucketSort,
    quickSort,
    radixSort,
    heapSort,
];

const COUNTED = [
    bubbleSortCount,
    selectionSortCount,
    insertionSortCount,
    mergeSortCount,
    shellSortCount,
    bucketSortCount,
    quickSortCount,
    radixSortCount,
    heapSortCount,
];

function measureTime(algorithmIndex, a) {
    const start = process.hrtime.bigint();
    CLEAN[algorithmIndex](a);
    const end = process.hrtime.bigint();
    return Number(end - start) / 1e6;
}

function shouldTimeout(algorithmIndex, n, typeIndex) {
    if (algorithmIndex > 2) return false;
    if (n < 100000) return false;
    const orderedInput = typeIndex === 1;
    if (algorithmIndex === 1) return n >= 1000000;
    if (orderedInput) return false;
    return n >= 1000000;
}

function row(algorithm, n, type, time, comparisons, swaps, state) {
    return [LANGUAGE, algorithm, n, type, time, comparisons, swaps, state].join(",") + "\n";
}

function main() {
    const lines = [];
    lines.push("lenguaje,algoritmo,tamano,tipo_arreglo,tiempo_ms,comparaciones,intercambios,estado\n");

    // Calentamiento (no se mide): activa el JIT antes de las pruebas.
    const warmBase = generateRandom(2000);
    for (let ai = 0; ai < ALGORITHM_COUNT; ++ai) {
        CLEAN[ai](warmBase.slice());
    }

    for (const n of SIZES) {
        const base = generateRandom(n);
        const ordered = base.slice().sort((x, y) => x - y);
        const inverse = ordered.slice().reverse();
        const sources = [base, ordered, inverse];

        for (let ai = 0; ai < ALGORITHM_COUNT; ++ai) {
            for (let ti = 0; ti < 3; ++ti) {
                if (shouldTimeout(ai, n, ti)) {
                    lines.push(row(ALGORITHMS[ai], n, TYPES[ti], "0.000000", 0, 0, "timeout"));
                    continue;
                }

                try {
                    const samples = [];
                    let valid = true;
                    for (let rep = 0; rep < 3; ++rep) {
                        const timed = sources[ti].slice();
                        samples.push(measureTime(ai, timed));
                        if (!isSorted(timed)) {
                            valid = false;
                            break;
                        }
                    }
                    if (!valid) {
                        lines.push(row(ALGORITHMS[ai], n, TYPES[ti], "0.000000", 0, 0, "error"));
                        continue;
                    }
                    samples.sort((x, y) => x - y);
                    const elapsed = samples[1];
                    const elapsedText = elapsed.toFixed(6);

                    const counter = new Counter();
                    const counted = sources[ti].slice();
                    COUNTED[ai](counted, counter);

                    if (!isSorted(counted)) {
                        lines.push(row(ALGORITHMS[ai], n, TYPES[ti], elapsedText, 0, 0, "error"));
                        continue;
                    }

                    lines.push(row(ALGORITHMS[ai], n, TYPES[ti], elapsedText,
                        counter.comparisons, counter.swaps, "ok"));
                } catch (e) {
                    lines.push(row(ALGORITHMS[ai], n, TYPES[ti], "0.000000", 0, 0, "error"));
                }
            }
        }
    }

    fs.writeFileSync("resultados_javascript.csv", lines.join(""), "utf8");
    console.log("Resultados escritos en resultados_javascript.csv");
}

main();
