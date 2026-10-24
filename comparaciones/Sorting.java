import java.io.BufferedWriter;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Locale;

// Benchmark de 9 algoritmos de ordenamiento en Java.
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

public class Sorting {
    static final String LANGUAGE = "java";
    static final int[] SIZES = {100, 1000, 10000, 100000, 1000000};
    static final String[] TYPES = {"aleatorio", "ordenado", "inverso"};
    static final String[] ALGORITHMS = {
        "Bubble Sort", "Selection Sort", "Insertion Sort",
        "Merge Sort", "Shell Sort", "Bucket Sort",
        "Quick Sort", "Radix Sort", "Heap Sort"
    };
    static final int ALGORITHM_COUNT = 9;
    static final int VALUE_LIMIT = 1000001;
    static final long RANDOM_SEED = 123456789L;

    static class Counter {
        long comparisons = 0;
        long swaps = 0;
    }

    interface CleanSorter {
        void sort(int[] a);
    }

    interface CountedSorter {
        void sort(int[] a, Counter c);
    }

    static void swap(int[] a, int i, int j) {
        int tmp = a[i];
        a[i] = a[j];
        a[j] = tmp;
    }

    // -----------------------------------------------------------------------
    // Generacion reproducible de datos (LCG identico en los 5 lenguajes)
    // -----------------------------------------------------------------------
    static int[] generateRandom(int n) {
        int[] values = new int[n];
        long state = RANDOM_SEED;
        for (int i = 0; i < n; ++i) {
            state = (state * 1664525L + 1013904223L) & 0xFFFFFFFFL;
            values[i] = (int) (state % VALUE_LIMIT);
        }
        return values;
    }

    static boolean isSorted(int[] values) {
        for (int i = 1; i < values.length; ++i) {
            if (values[i - 1] > values[i]) return false;
        }
        return true;
    }

    // -----------------------------------------------------------------------
    // Version sin contadores (solo para medir tiempo)
    // -----------------------------------------------------------------------
    static void bubbleSort(int[] a) {
        int end = a.length - 1;
        while (end > 0) {
            boolean swapped = false;
            for (int i = 0; i < end; ++i) {
                if (a[i] > a[i + 1]) {
                    swap(a, i, i + 1);
                    swapped = true;
                }
            }
            if (!swapped) break;
            --end;
        }
    }

    static void selectionSort(int[] a) {
        int n = a.length;
        for (int i = 0; i < n - 1; ++i) {
            int m = i;
            for (int j = i + 1; j < n; ++j) {
                if (a[j] < a[m]) m = j;
            }
            if (m != i) swap(a, i, m);
        }
    }

    static void insertionSort(int[] a) {
        int n = a.length;
        for (int i = 1; i < n; ++i) {
            int j = i;
            while (j > 0) {
                if (a[j - 1] <= a[j]) break;
                swap(a, j - 1, j);
                --j;
            }
        }
    }

    static void mergeSortRec(int[] a, int[] aux, int lo, int hi) {
        if (lo >= hi) return;
        int mid = lo + (hi - lo) / 2;
        mergeSortRec(a, aux, lo, mid);
        mergeSortRec(a, aux, mid + 1, hi);
        for (int i = lo; i <= hi; ++i) aux[i] = a[i];
        int i = lo, j = mid + 1, k = lo;
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

    static void mergeSort(int[] a) {
        int n = a.length;
        if (n < 2) return;
        int[] aux = new int[n];
        mergeSortRec(a, aux, 0, n - 1);
    }

    static void shellSort(int[] a) {
        int n = a.length;
        int gap = 1;
        while (gap < n / 3) gap = gap * 3 + 1;
        while (gap >= 1) {
            for (int i = gap; i < n; ++i) {
                int j = i;
                while (j >= gap) {
                    if (a[j - gap] <= a[j]) break;
                    swap(a, j - gap, j);
                    j -= gap;
                }
            }
            gap /= 3;
        }
    }

    @SuppressWarnings("unchecked")
    static void bucketSort(int[] a) {
        int n = a.length;
        if (n < 2) return;
        int bucketsCount = Math.min(n, 100000);
        ArrayList<Integer>[] buckets = new ArrayList[bucketsCount];
        for (int i = 0; i < bucketsCount; ++i) buckets[i] = new ArrayList<>();
        for (int value : a) {
            int idx = (int) ((long) value * bucketsCount / VALUE_LIMIT);
            buckets[idx].add(value);
        }
        int k = 0;
        for (ArrayList<Integer> bucket : buckets) {
            int m = bucket.size();
            for (int i = 1; i < m; ++i) {
                int key = bucket.get(i);
                int j = i - 1;
                while (j >= 0 && bucket.get(j) > key) {
                    bucket.set(j + 1, bucket.get(j));
                    --j;
                }
                bucket.set(j + 1, key);
            }
            for (int value : bucket) a[k++] = value;
        }
    }

    static void quickSortRec(int[] a, int lo, int hi) {
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] < a[lo]) swap(a, lo, mid);
            if (a[hi] < a[lo]) swap(a, lo, hi);
            if (a[hi] < a[mid]) swap(a, mid, hi);
            swap(a, mid, hi);
            int pivot = a[hi];
            int i = lo;
            for (int j = lo; j < hi; ++j) {
                if (a[j] < pivot) {
                    swap(a, i, j);
                    ++i;
                }
            }
            swap(a, i, hi);
            int p = i;
            if (p - lo < hi - p) {
                quickSortRec(a, lo, p - 1);
                lo = p + 1;
            } else {
                quickSortRec(a, p + 1, hi);
                hi = p - 1;
            }
        }
    }

    static void quickSort(int[] a) {
        if (a.length > 1) quickSortRec(a, 0, a.length - 1);
    }

    static void radixSort(int[] a) {
        int n = a.length;
        if (n < 2) return;
        int[] temp = new int[n];
        int[] src = a;
        int[] dst = temp;
        for (int shift : new int[] {0, 8, 16}) {
            int[] count = new int[256];
            for (int value : src) ++count[(value >> shift) & 255];
            int total = 0;
            for (int i = 0; i < 256; ++i) {
                int x = count[i];
                count[i] = total;
                total += x;
            }
            for (int value : src) {
                int digit = (value >> shift) & 255;
                dst[count[digit]++] = value;
            }
            int[] t = src;
            src = dst;
            dst = t;
        }
        if (src != a) System.arraycopy(src, 0, a, 0, n);
    }

    static void siftDown(int[] a, int root, int n) {
        while (true) {
            int child = 2 * root + 1;
            if (child >= n) break;
            if (child + 1 < n && a[child + 1] > a[child]) ++child;
            if (a[root] >= a[child]) break;
            swap(a, root, child);
            root = child;
        }
    }

    static void heapSort(int[] a) {
        int n = a.length;
        for (int start = n / 2 - 1; start >= 0; --start) siftDown(a, start, n);
        for (int end = n - 1; end > 0; --end) {
            swap(a, 0, end);
            siftDown(a, 0, end);
        }
    }

    // -----------------------------------------------------------------------
    // Versiones instrumentadas (solo para contar)
    // -----------------------------------------------------------------------
    static void bubbleSortCount(int[] a, Counter c) {
        int end = a.length - 1;
        while (end > 0) {
            boolean swapped = false;
            for (int i = 0; i < end; ++i) {
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

    static void selectionSortCount(int[] a, Counter c) {
        int n = a.length;
        for (int i = 0; i < n - 1; ++i) {
            int m = i;
            for (int j = i + 1; j < n; ++j) {
                ++c.comparisons;
                if (a[j] < a[m]) m = j;
            }
            if (m != i) {
                swap(a, i, m);
                ++c.swaps;
            }
        }
    }

    static void insertionSortCount(int[] a, Counter c) {
        int n = a.length;
        for (int i = 1; i < n; ++i) {
            int j = i;
            while (j > 0) {
                ++c.comparisons;
                if (a[j - 1] <= a[j]) break;
                swap(a, j - 1, j);
                ++c.swaps;
                --j;
            }
        }
    }

    static void mergeSortRecCount(int[] a, int[] aux, int lo, int hi, Counter c) {
        if (lo >= hi) return;
        int mid = lo + (hi - lo) / 2;
        mergeSortRecCount(a, aux, lo, mid, c);
        mergeSortRecCount(a, aux, mid + 1, hi, c);
        for (int i = lo; i <= hi; ++i) {
            aux[i] = a[i];
            ++c.swaps;
        }
        int i = lo, j = mid + 1, k = lo;
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

    static void mergeSortCount(int[] a, Counter c) {
        int n = a.length;
        if (n < 2) return;
        int[] aux = new int[n];
        mergeSortRecCount(a, aux, 0, n - 1, c);
    }

    static void shellSortCount(int[] a, Counter c) {
        int n = a.length;
        int gap = 1;
        while (gap < n / 3) gap = gap * 3 + 1;
        while (gap >= 1) {
            for (int i = gap; i < n; ++i) {
                int j = i;
                while (j >= gap) {
                    ++c.comparisons;
                    if (a[j - gap] <= a[j]) break;
                    swap(a, j - gap, j);
                    ++c.swaps;
                    j -= gap;
                }
            }
            gap /= 3;
        }
    }

    @SuppressWarnings("unchecked")
    static void bucketSortCount(int[] a, Counter c) {
        int n = a.length;
        if (n < 2) return;
        int bucketsCount = Math.min(n, 100000);
        ArrayList<Integer>[] buckets = new ArrayList[bucketsCount];
        for (int i = 0; i < bucketsCount; ++i) buckets[i] = new ArrayList<>();
        for (int value : a) {
            int idx = (int) ((long) value * bucketsCount / VALUE_LIMIT);
            buckets[idx].add(value);
        }
        int k = 0;
        for (ArrayList<Integer> bucket : buckets) {
            int m = bucket.size();
            for (int i = 1; i < m; ++i) {
                int key = bucket.get(i);
                int j = i - 1;
                while (j >= 0) {
                    ++c.comparisons;
                    if (bucket.get(j) <= key) break;
                    bucket.set(j + 1, bucket.get(j));
                    ++c.swaps;
                    --j;
                }
                bucket.set(j + 1, key);
                ++c.swaps;
            }
            for (int value : bucket) {
                a[k++] = value;
                ++c.swaps;
            }
        }
    }

    static void quickSortRecCount(int[] a, int lo, int hi, Counter c) {
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
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
            int pivot = a[hi];
            int i = lo;
            for (int j = lo; j < hi; ++j) {
                ++c.comparisons;
                if (a[j] < pivot) {
                    swap(a, i, j);
                    ++c.swaps;
                    ++i;
                }
            }
            swap(a, i, hi);
            ++c.swaps;
            int p = i;
            if (p - lo < hi - p) {
                quickSortRecCount(a, lo, p - 1, c);
                lo = p + 1;
            } else {
                quickSortRecCount(a, p + 1, hi, c);
                hi = p - 1;
            }
        }
    }

    static void quickSortCount(int[] a, Counter c) {
        if (a.length > 1) quickSortRecCount(a, 0, a.length - 1, c);
    }

    static void radixSortCount(int[] a, Counter c) {
        int n = a.length;
        if (n < 2) return;
        int[] temp = new int[n];
        int[] src = a;
        int[] dst = temp;
        for (int shift : new int[] {0, 8, 16}) {
            int[] count = new int[256];
            for (int value : src) ++count[(value >> shift) & 255];
            int total = 0;
            for (int i = 0; i < 256; ++i) {
                int x = count[i];
                count[i] = total;
                total += x;
            }
            for (int value : src) {
                int digit = (value >> shift) & 255;
                dst[count[digit]++] = value;
                ++c.swaps;
            }
            int[] t = src;
            src = dst;
            dst = t;
        }
        if (src != a) {
            for (int i = 0; i < n; ++i) {
                a[i] = src[i];
                ++c.swaps;
            }
        }
    }

    static void siftDownCount(int[] a, int root, int n, Counter c) {
        while (true) {
            int child = 2 * root + 1;
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

    static void heapSortCount(int[] a, Counter c) {
        int n = a.length;
        for (int start = n / 2 - 1; start >= 0; --start) siftDownCount(a, start, n, c);
        for (int end = n - 1; end > 0; --end) {
            swap(a, 0, end);
            ++c.swaps;
            siftDownCount(a, 0, end, c);
        }
    }

    // -----------------------------------------------------------------------
    // Dispatch y programa principal
    // -----------------------------------------------------------------------
    static final CleanSorter[] CLEAN = {
        Sorting::bubbleSort, Sorting::selectionSort, Sorting::insertionSort,
        Sorting::mergeSort, Sorting::shellSort, Sorting::bucketSort,
        Sorting::quickSort, Sorting::radixSort, Sorting::heapSort
    };

    static final CountedSorter[] COUNTED = {
        Sorting::bubbleSortCount, Sorting::selectionSortCount, Sorting::insertionSortCount,
        Sorting::mergeSortCount, Sorting::shellSortCount, Sorting::bucketSortCount,
        Sorting::quickSortCount, Sorting::radixSortCount, Sorting::heapSortCount
    };

    static double measureTime(int algorithmIndex, int[] a) {
        long start = System.nanoTime();
        CLEAN[algorithmIndex].sort(a);
        long end = System.nanoTime();
        return (end - start) / 1_000_000.0;
    }

    static boolean shouldTimeout(int algorithmIndex, int n, int typeIndex) {
        if (algorithmIndex > 2) return false;
        if (n < 100000) return false;
        boolean orderedInput = (typeIndex == 1);
        if (algorithmIndex == 1) return n >= 1000000;
        if (orderedInput) return false;
        return n >= 1000000;
    }

    static String row(String algorithm, int n, String type, String time, long comparisons,
                      long swaps, String state) {
        return LANGUAGE + "," + algorithm + "," + n + "," + type + "," + time + ","
                + comparisons + "," + swaps + "," + state + "\n";
    }

    public static void main(String[] args) {
        String outputPath = "resultados_java.csv";
        try (BufferedWriter out = new BufferedWriter(new OutputStreamWriter(
                new FileOutputStream(outputPath), StandardCharsets.UTF_8))) {
            out.write("lenguaje,algoritmo,tamano,tipo_arreglo,tiempo_ms,comparaciones,intercambios,estado\n");

            // Calentamiento (no se mide): activa el JIT antes de las pruebas.
            int[] warmBase = generateRandom(2000);
            for (int ai = 0; ai < ALGORITHM_COUNT; ++ai) {
                int[] warm = warmBase.clone();
                CLEAN[ai].sort(warm);
            }

            for (int n : SIZES) {
                int[] base = generateRandom(n);
                int[] ordered = base.clone();
                Arrays.sort(ordered);
                int[] inverse = ordered.clone();
                for (int i = 0, j = inverse.length - 1; i < j; ++i, --j) swap(inverse, i, j);
                int[][] sources = {base, ordered, inverse};

                for (int ai = 0; ai < ALGORITHM_COUNT; ++ai) {
                    for (int ti = 0; ti < 3; ++ti) {
                        if (shouldTimeout(ai, n, ti)) {
                            out.write(row(ALGORITHMS[ai], n, TYPES[ti], "0.000000", 0, 0, "timeout"));
                            continue;
                        }

                        try {
                            double[] samples = new double[3];
                            boolean valid = true;
                            for (int rep = 0; rep < 3; ++rep) {
                                int[] timed = sources[ti].clone();
                                samples[rep] = measureTime(ai, timed);
                                if (!isSorted(timed)) {
                                    valid = false;
                                    break;
                                }
                            }
                            if (!valid) {
                                out.write(row(ALGORITHMS[ai], n, TYPES[ti], "0.000000", 0, 0, "error"));
                                continue;
                            }
                            Arrays.sort(samples);
                            double elapsed = samples[1];
                            String elapsedText = String.format(Locale.ROOT, "%.6f", elapsed);

                            Counter counter = new Counter();
                            int[] counted = sources[ti].clone();
                            COUNTED[ai].sort(counted, counter);

                            if (!isSorted(counted)) {
                                out.write(row(ALGORITHMS[ai], n, TYPES[ti], elapsedText, 0, 0, "error"));
                                continue;
                            }

                            out.write(row(ALGORITHMS[ai], n, TYPES[ti], elapsedText,
                                    counter.comparisons, counter.swaps, "ok"));
                        } catch (Throwable t) {
                            out.write(row(ALGORITHMS[ai], n, TYPES[ti], "0.000000", 0, 0, "error"));
                        }
                    }
                }
            }
        } catch (IOException e) {
            System.err.println("Error escribiendo resultados: " + e.getMessage());
            return;
        }

        System.out.println("Resultados escritos en " + outputPath);
    }
}
