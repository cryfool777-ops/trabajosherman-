using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Text;

// Benchmark de 9 algoritmos de ordenamiento en C#.
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
//
// Compilar con: dotnet build -c Release

internal static class Sorting
{
    private const string Language = "csharp";
    private static readonly int[] Sizes = { 100, 1000, 10000, 100000, 1000000 };
    private static readonly string[] Types = { "aleatorio", "ordenado", "inverso" };
    private static readonly string[] Algorithms =
    {
        "Bubble Sort", "Selection Sort", "Insertion Sort",
        "Merge Sort", "Shell Sort", "Bucket Sort",
        "Quick Sort", "Radix Sort", "Heap Sort"
    };
    private const int AlgorithmCount = 9;
    private const int ValueLimit = 1000001;
    private const uint RandomSeed = 123456789u;

    private sealed class Counter
    {
        public long Comparisons;
        public long Swaps;
    }

    private static void Swap(int[] a, int i, int j)
    {
        int tmp = a[i];
        a[i] = a[j];
        a[j] = tmp;
    }

    // -----------------------------------------------------------------------
    // Generacion reproducible de datos (LCG identico en los 5 lenguajes)
    // -----------------------------------------------------------------------
    private static int[] GenerateRandom(int n)
    {
        int[] values = new int[n];
        uint state = RandomSeed;
        unchecked
        {
            for (int i = 0; i < n; ++i)
            {
                state = state * 1664525u + 1013904223u;
                values[i] = (int)(state % ValueLimit);
            }
        }
        return values;
    }

    private static bool IsSorted(int[] values)
    {
        for (int i = 1; i < values.Length; ++i)
        {
            if (values[i - 1] > values[i]) return false;
        }
        return true;
    }

    // -----------------------------------------------------------------------
    // Version sin contadores (solo para medir tiempo)
    // -----------------------------------------------------------------------
    private static void BubbleSort(int[] a)
    {
        int end = a.Length - 1;
        while (end > 0)
        {
            bool swapped = false;
            for (int i = 0; i < end; ++i)
            {
                if (a[i] > a[i + 1])
                {
                    Swap(a, i, i + 1);
                    swapped = true;
                }
            }
            if (!swapped) break;
            --end;
        }
    }

    private static void SelectionSort(int[] a)
    {
        int n = a.Length;
        for (int i = 0; i < n - 1; ++i)
        {
            int m = i;
            for (int j = i + 1; j < n; ++j)
            {
                if (a[j] < a[m]) m = j;
            }
            if (m != i) Swap(a, i, m);
        }
    }

    private static void InsertionSort(int[] a)
    {
        int n = a.Length;
        for (int i = 1; i < n; ++i)
        {
            int j = i;
            while (j > 0)
            {
                if (a[j - 1] <= a[j]) break;
                Swap(a, j - 1, j);
                --j;
            }
        }
    }

    private static void MergeSortRec(int[] a, int[] aux, int lo, int hi)
    {
        if (lo >= hi) return;
        int mid = lo + (hi - lo) / 2;
        MergeSortRec(a, aux, lo, mid);
        MergeSortRec(a, aux, mid + 1, hi);
        for (int i = lo; i <= hi; ++i) aux[i] = a[i];
        int p = lo, q = mid + 1, k = lo;
        while (p <= mid && q <= hi)
        {
            if (aux[p] <= aux[q])
            {
                a[k] = aux[p];
                ++p;
            }
            else
            {
                a[k] = aux[q];
                ++q;
            }
            ++k;
        }
        while (p <= mid)
        {
            a[k] = aux[p];
            ++p;
            ++k;
        }
        while (q <= hi)
        {
            a[k] = aux[q];
            ++q;
            ++k;
        }
    }

    private static void MergeSort(int[] a)
    {
        int n = a.Length;
        if (n < 2) return;
        int[] aux = new int[n];
        MergeSortRec(a, aux, 0, n - 1);
    }

    private static void ShellSort(int[] a)
    {
        int n = a.Length;
        int gap = 1;
        while (gap < n / 3) gap = gap * 3 + 1;
        while (gap >= 1)
        {
            for (int i = gap; i < n; ++i)
            {
                int j = i;
                while (j >= gap)
                {
                    if (a[j - gap] <= a[j]) break;
                    Swap(a, j - gap, j);
                    j -= gap;
                }
            }
            gap /= 3;
        }
    }

    private static void BucketSort(int[] a)
    {
        int n = a.Length;
        if (n < 2) return;
        int bucketsCount = Math.Min(n, 100000);
        List<int>[] buckets = new List<int>[bucketsCount];
        for (int i = 0; i < bucketsCount; ++i) buckets[i] = new List<int>();
        for (int i = 0; i < n; ++i)
        {
            int value = a[i];
            int idx = (int)((long)value * bucketsCount / ValueLimit);
            buckets[idx].Add(value);
        }
        int k = 0;
        foreach (List<int> bucket in buckets)
        {
            int m = bucket.Count;
            for (int i = 1; i < m; ++i)
            {
                int key = bucket[i];
                int j = i - 1;
                while (j >= 0 && bucket[j] > key)
                {
                    bucket[j + 1] = bucket[j];
                    --j;
                }
                bucket[j + 1] = key;
            }
            foreach (int value in bucket) a[k++] = value;
        }
    }

    private static void QuickSortRec(int[] a, int lo, int hi)
    {
        while (lo < hi)
        {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] < a[lo]) Swap(a, lo, mid);
            if (a[hi] < a[lo]) Swap(a, lo, hi);
            if (a[hi] < a[mid]) Swap(a, mid, hi);
            Swap(a, mid, hi);
            int pivot = a[hi];
            int i = lo;
            for (int j = lo; j < hi; ++j)
            {
                if (a[j] < pivot)
                {
                    Swap(a, i, j);
                    ++i;
                }
            }
            Swap(a, i, hi);
            int p = i;
            if (p - lo < hi - p)
            {
                QuickSortRec(a, lo, p - 1);
                lo = p + 1;
            }
            else
            {
                QuickSortRec(a, p + 1, hi);
                hi = p - 1;
            }
        }
    }

    private static void QuickSort(int[] a)
    {
        if (a.Length > 1) QuickSortRec(a, 0, a.Length - 1);
    }

    private static void RadixSort(int[] a)
    {
        int n = a.Length;
        if (n < 2) return;
        int[] temp = new int[n];
        int[] src = a;
        int[] dst = temp;
        foreach (int shift in new[] { 0, 8, 16 })
        {
            int[] count = new int[256];
            foreach (int value in src) ++count[(value >> shift) & 255];
            int total = 0;
            for (int i = 0; i < 256; ++i)
            {
                int x = count[i];
                count[i] = total;
                total += x;
            }
            for (int i = 0; i < n; ++i)
            {
                int value = src[i];
                int digit = (value >> shift) & 255;
                dst[count[digit]++] = value;
            }
            int[] t = src;
            src = dst;
            dst = t;
        }
        if (!ReferenceEquals(src, a)) Array.Copy(src, a, n);
    }

    private static void SiftDown(int[] a, int root, int n)
    {
        while (true)
        {
            int child = 2 * root + 1;
            if (child >= n) break;
            if (child + 1 < n && a[child + 1] > a[child]) ++child;
            if (a[root] >= a[child]) break;
            Swap(a, root, child);
            root = child;
        }
    }

    private static void HeapSort(int[] a)
    {
        int n = a.Length;
        for (int start = n / 2 - 1; start >= 0; --start) SiftDown(a, start, n);
        for (int end = n - 1; end > 0; --end)
        {
            Swap(a, 0, end);
            SiftDown(a, 0, end);
        }
    }

    // -----------------------------------------------------------------------
    // Versiones instrumentadas (solo para contar)
    // -----------------------------------------------------------------------
    private static void BubbleSortCount(int[] a, Counter c)
    {
        int end = a.Length - 1;
        while (end > 0)
        {
            bool swapped = false;
            for (int i = 0; i < end; ++i)
            {
                ++c.Comparisons;
                if (a[i] > a[i + 1])
                {
                    Swap(a, i, i + 1);
                    ++c.Swaps;
                    swapped = true;
                }
            }
            if (!swapped) break;
            --end;
        }
    }

    private static void SelectionSortCount(int[] a, Counter c)
    {
        int n = a.Length;
        for (int i = 0; i < n - 1; ++i)
        {
            int m = i;
            for (int j = i + 1; j < n; ++j)
            {
                ++c.Comparisons;
                if (a[j] < a[m]) m = j;
            }
            if (m != i)
            {
                Swap(a, i, m);
                ++c.Swaps;
            }
        }
    }

    private static void InsertionSortCount(int[] a, Counter c)
    {
        int n = a.Length;
        for (int i = 1; i < n; ++i)
        {
            int j = i;
            while (j > 0)
            {
                ++c.Comparisons;
                if (a[j - 1] <= a[j]) break;
                Swap(a, j - 1, j);
                ++c.Swaps;
                --j;
            }
        }
    }

    private static void MergeSortRecCount(int[] a, int[] aux, int lo, int hi, Counter c)
    {
        if (lo >= hi) return;
        int mid = lo + (hi - lo) / 2;
        MergeSortRecCount(a, aux, lo, mid, c);
        MergeSortRecCount(a, aux, mid + 1, hi, c);
        for (int i = lo; i <= hi; ++i)
        {
            aux[i] = a[i];
            ++c.Swaps;
        }
        int p = lo, q = mid + 1, k = lo;
        while (p <= mid && q <= hi)
        {
            ++c.Comparisons;
            if (aux[p] <= aux[q])
            {
                a[k] = aux[p];
                ++p;
            }
            else
            {
                a[k] = aux[q];
                ++q;
            }
            ++c.Swaps;
            ++k;
        }
        while (p <= mid)
        {
            a[k] = aux[p];
            ++p;
            ++k;
            ++c.Swaps;
        }
        while (q <= hi)
        {
            a[k] = aux[q];
            ++q;
            ++k;
            ++c.Swaps;
        }
    }

    private static void MergeSortCount(int[] a, Counter c)
    {
        int n = a.Length;
        if (n < 2) return;
        int[] aux = new int[n];
        MergeSortRecCount(a, aux, 0, n - 1, c);
    }

    private static void ShellSortCount(int[] a, Counter c)
    {
        int n = a.Length;
        int gap = 1;
        while (gap < n / 3) gap = gap * 3 + 1;
        while (gap >= 1)
        {
            for (int i = gap; i < n; ++i)
            {
                int j = i;
                while (j >= gap)
                {
                    ++c.Comparisons;
                    if (a[j - gap] <= a[j]) break;
                    Swap(a, j - gap, j);
                    ++c.Swaps;
                    j -= gap;
                }
            }
            gap /= 3;
        }
    }

    private static void BucketSortCount(int[] a, Counter c)
    {
        int n = a.Length;
        if (n < 2) return;
        int bucketsCount = Math.Min(n, 100000);
        List<int>[] buckets = new List<int>[bucketsCount];
        for (int i = 0; i < bucketsCount; ++i) buckets[i] = new List<int>();
        for (int i = 0; i < n; ++i)
        {
            int value = a[i];
            int idx = (int)((long)value * bucketsCount / ValueLimit);
            buckets[idx].Add(value);
        }
        int k = 0;
        foreach (List<int> bucket in buckets)
        {
            int m = bucket.Count;
            for (int i = 1; i < m; ++i)
            {
                int key = bucket[i];
                int j = i - 1;
                while (j >= 0)
                {
                    ++c.Comparisons;
                    if (bucket[j] <= key) break;
                    bucket[j + 1] = bucket[j];
                    ++c.Swaps;
                    --j;
                }
                bucket[j + 1] = key;
                ++c.Swaps;
            }
            foreach (int value in bucket)
            {
                a[k++] = value;
                ++c.Swaps;
            }
        }
    }

    private static void QuickSortRecCount(int[] a, int lo, int hi, Counter c)
    {
        while (lo < hi)
        {
            int mid = lo + (hi - lo) / 2;
            ++c.Comparisons;
            if (a[mid] < a[lo])
            {
                Swap(a, lo, mid);
                ++c.Swaps;
            }
            ++c.Comparisons;
            if (a[hi] < a[lo])
            {
                Swap(a, lo, hi);
                ++c.Swaps;
            }
            ++c.Comparisons;
            if (a[hi] < a[mid])
            {
                Swap(a, mid, hi);
                ++c.Swaps;
            }
            Swap(a, mid, hi);
            ++c.Swaps;
            int pivot = a[hi];
            int i = lo;
            for (int j = lo; j < hi; ++j)
            {
                ++c.Comparisons;
                if (a[j] < pivot)
                {
                    Swap(a, i, j);
                    ++c.Swaps;
                    ++i;
                }
            }
            Swap(a, i, hi);
            ++c.Swaps;
            int p = i;
            if (p - lo < hi - p)
            {
                QuickSortRecCount(a, lo, p - 1, c);
                lo = p + 1;
            }
            else
            {
                QuickSortRecCount(a, p + 1, hi, c);
                hi = p - 1;
            }
        }
    }

    private static void QuickSortCount(int[] a, Counter c)
    {
        if (a.Length > 1) QuickSortRecCount(a, 0, a.Length - 1, c);
    }

    private static void RadixSortCount(int[] a, Counter c)
    {
        int n = a.Length;
        if (n < 2) return;
        int[] temp = new int[n];
        int[] src = a;
        int[] dst = temp;
        foreach (int shift in new[] { 0, 8, 16 })
        {
            int[] count = new int[256];
            foreach (int value in src) ++count[(value >> shift) & 255];
            int total = 0;
            for (int i = 0; i < 256; ++i)
            {
                int x = count[i];
                count[i] = total;
                total += x;
            }
            for (int i = 0; i < n; ++i)
            {
                int value = src[i];
                int digit = (value >> shift) & 255;
                dst[count[digit]++] = value;
                ++c.Swaps;
            }
            int[] t = src;
            src = dst;
            dst = t;
        }
        if (!ReferenceEquals(src, a))
        {
            for (int i = 0; i < n; ++i)
            {
                a[i] = src[i];
                ++c.Swaps;
            }
        }
    }

    private static void SiftDownCount(int[] a, int root, int n, Counter c)
    {
        while (true)
        {
            int child = 2 * root + 1;
            if (child >= n) break;
            if (child + 1 < n)
            {
                ++c.Comparisons;
                if (a[child + 1] > a[child]) ++child;
            }
            ++c.Comparisons;
            if (a[root] >= a[child]) break;
            Swap(a, root, child);
            ++c.Swaps;
            root = child;
        }
    }

    private static void HeapSortCount(int[] a, Counter c)
    {
        int n = a.Length;
        for (int start = n / 2 - 1; start >= 0; --start) SiftDownCount(a, start, n, c);
        for (int end = n - 1; end > 0; --end)
        {
            Swap(a, 0, end);
            ++c.Swaps;
            SiftDownCount(a, 0, end, c);
        }
    }

    // -----------------------------------------------------------------------
    // Dispatch y programa principal
    // -----------------------------------------------------------------------
    private static readonly Action<int[]>[] Clean =
    {
        BubbleSort, SelectionSort, InsertionSort,
        MergeSort, ShellSort, BucketSort,
        QuickSort, RadixSort, HeapSort
    };

    private static readonly Action<int[], Counter>[] Counted =
    {
        BubbleSortCount, SelectionSortCount, InsertionSortCount,
        MergeSortCount, ShellSortCount, BucketSortCount,
        QuickSortCount, RadixSortCount, HeapSortCount
    };

    private static double MeasureTime(int algorithmIndex, int[] a)
    {
        Stopwatch sw = Stopwatch.StartNew();
        Clean[algorithmIndex](a);
        sw.Stop();
        return sw.Elapsed.TotalMilliseconds;
    }

    private static bool ShouldTimeout(int algorithmIndex, int n, int typeIndex)
    {
        if (algorithmIndex > 2) return false;
        if (n < 100000) return false;
        bool orderedInput = (typeIndex == 1);
        if (algorithmIndex == 1) return n >= 1000000;
        if (orderedInput) return false;
        return n >= 1000000;
    }

    private static string Row(string algorithm, int n, string type, string time,
        long comparisons, long swaps, string state)
    {
        return string.Join(",", Language, algorithm, n.ToString(CultureInfo.InvariantCulture),
            type, time, comparisons.ToString(CultureInfo.InvariantCulture),
            swaps.ToString(CultureInfo.InvariantCulture), state);
    }

    private static void Main()
    {
        string outputPath = "resultados_csharp.csv";
        using StreamWriter writer = new StreamWriter(outputPath, false, new UTF8Encoding(false));
        writer.Write("lenguaje,algoritmo,tamano,tipo_arreglo,tiempo_ms,comparaciones,intercambios,estado\n");

        // Calentamiento (no se mide): activa el JIT antes de las pruebas.
        int[] warmBase = GenerateRandom(2000);
        for (int ai = 0; ai < AlgorithmCount; ++ai)
        {
            int[] warm = (int[])warmBase.Clone();
            Clean[ai](warm);
        }

        foreach (int n in Sizes)
        {
            int[] baseArray = GenerateRandom(n);
            int[] ordered = (int[])baseArray.Clone();
            Array.Sort(ordered);
            int[] inverse = (int[])ordered.Clone();
            Array.Reverse(inverse);
            int[][] sources = { baseArray, ordered, inverse };

            for (int ai = 0; ai < AlgorithmCount; ++ai)
            {
                for (int ti = 0; ti < 3; ++ti)
                {
                    if (ShouldTimeout(ai, n, ti))
                    {
                        writer.Write(Row(Algorithms[ai], n, Types[ti], "0.000000", 0, 0, "timeout") + "\n");
                        continue;
                    }

                    try
                    {
                        double[] samples = new double[3];
                        bool valid = true;
                        for (int rep = 0; rep < 3; ++rep)
                        {
                            int[] timed = (int[])sources[ti].Clone();
                            samples[rep] = MeasureTime(ai, timed);
                            if (!IsSorted(timed))
                            {
                                valid = false;
                                break;
                            }
                        }
                        if (!valid)
                        {
                            writer.Write(Row(Algorithms[ai], n, Types[ti], "0.000000", 0, 0, "error") + "\n");
                            continue;
                        }
                        Array.Sort(samples);
                        double elapsed = samples[1];
                        string elapsedText = elapsed.ToString("F6", CultureInfo.InvariantCulture);

                        Counter counter = new Counter();
                        int[] counted = (int[])sources[ti].Clone();
                        Counted[ai](counted, counter);

                        if (!IsSorted(counted))
                        {
                            writer.Write(Row(Algorithms[ai], n, Types[ti], elapsedText, 0, 0, "error") + "\n");
                            continue;
                        }

                        writer.Write(Row(Algorithms[ai], n, Types[ti], elapsedText,
                            counter.Comparisons, counter.Swaps, "ok") + "\n");
                    }
                    catch (Exception)
                    {
                        writer.Write(Row(Algorithms[ai], n, Types[ti], "0.000000", 0, 0, "error") + "\n");
                    }
                }
            }
        }

        writer.Flush();
        Console.WriteLine("Resultados escritos en " + outputPath);
    }
}
