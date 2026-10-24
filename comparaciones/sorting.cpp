// Benchmark de 9 algoritmos de ordenamiento en C++.
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
// Compilar con: g++ -O2 -std=c++17 -o sorting_cpp.exe sorting.cpp

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

const string LANGUAGE = "cpp";
const int SIZES[] = {100, 1000, 10000, 100000, 1000000};
const string TYPES[] = {"aleatorio", "ordenado", "inverso"};
const string ALGORITHMS[] = {"Bubble Sort",  "Selection Sort", "Insertion Sort",
                             "Merge Sort",   "Shell Sort",     "Bucket Sort",
                             "Quick Sort",   "Radix Sort",     "Heap Sort"};
const int ALGORITHM_COUNT = 9;
const int VALUE_LIMIT = 1000001;
const uint32_t RANDOM_SEED = 123456789u;

struct Counter {
    long long comparisons = 0;
    long long swaps = 0;
};

static inline void swap_values(vector<int>& a, int i, int j) {
    int tmp = a[i];
    a[i] = a[j];
    a[j] = tmp;
}

// ---------------------------------------------------------------------------
// Generacion reproducible de datos (LCG identico en los 5 lenguajes)
// ---------------------------------------------------------------------------
vector<int> generate_random(int n) {
    vector<int> values(n);
    uint32_t state = RANDOM_SEED;
    for (int i = 0; i < n; ++i) {
        state = state * 1664525u + 1013904223u;
        values[i] = static_cast<int>(state % VALUE_LIMIT);
    }
    return values;
}

bool is_sorted(const vector<int>& values) {
    for (size_t i = 1; i < values.size(); ++i) {
        if (values[i - 1] > values[i]) return false;
    }
    return true;
}

// ---------------------------------------------------------------------------
// Version sin contadores (solo para medir tiempo)
// ---------------------------------------------------------------------------
void bubble_sort(vector<int>& a) {
    int end = static_cast<int>(a.size()) - 1;
    while (end > 0) {
        bool swapped = false;
        for (int i = 0; i < end; ++i) {
            if (a[i] > a[i + 1]) {
                swap_values(a, i, i + 1);
                swapped = true;
            }
        }
        if (!swapped) break;
        --end;
    }
}

void selection_sort(vector<int>& a) {
    int n = static_cast<int>(a.size());
    for (int i = 0; i < n - 1; ++i) {
        int m = i;
        for (int j = i + 1; j < n; ++j) {
            if (a[j] < a[m]) m = j;
        }
        if (m != i) swap_values(a, i, m);
    }
}

void insertion_sort(vector<int>& a) {
    int n = static_cast<int>(a.size());
    for (int i = 1; i < n; ++i) {
        int j = i;
        while (j > 0) {
            if (a[j - 1] <= a[j]) break;
            swap_values(a, j - 1, j);
            --j;
        }
    }
}

void merge_sort_rec(vector<int>& a, vector<int>& aux, int lo, int hi) {
    if (lo >= hi) return;
    int mid = lo + (hi - lo) / 2;
    merge_sort_rec(a, aux, lo, mid);
    merge_sort_rec(a, aux, mid + 1, hi);
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

void merge_sort(vector<int>& a) {
    int n = static_cast<int>(a.size());
    if (n < 2) return;
    vector<int> aux(n);
    merge_sort_rec(a, aux, 0, n - 1);
}

void shell_sort(vector<int>& a) {
    int n = static_cast<int>(a.size());
    int gap = 1;
    while (gap < n / 3) gap = gap * 3 + 1;
    while (gap >= 1) {
        for (int i = gap; i < n; ++i) {
            int j = i;
            while (j >= gap) {
                if (a[j - gap] <= a[j]) break;
                swap_values(a, j - gap, j);
                j -= gap;
            }
        }
        gap /= 3;
    }
}

void bucket_sort(vector<int>& a) {
    int n = static_cast<int>(a.size());
    if (n < 2) return;
    int buckets_count = min(n, 100000);
    vector<vector<int>> buckets(buckets_count);
    for (int value : a) {
        int idx = static_cast<int>(static_cast<long long>(value) * buckets_count / VALUE_LIMIT);
        buckets[idx].push_back(value);
    }
    int k = 0;
    for (auto& bucket : buckets) {
        int m = static_cast<int>(bucket.size());
        for (int i = 1; i < m; ++i) {
            int key = bucket[i];
            int j = i - 1;
            while (j >= 0 && bucket[j] > key) {
                bucket[j + 1] = bucket[j];
                --j;
            }
            bucket[j + 1] = key;
        }
        for (int value : bucket) a[k++] = value;
    }
}

void quick_sort_rec(vector<int>& a, int lo, int hi) {
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] < a[lo]) swap_values(a, lo, mid);
        if (a[hi] < a[lo]) swap_values(a, lo, hi);
        if (a[hi] < a[mid]) swap_values(a, mid, hi);
        swap_values(a, mid, hi);
        int pivot = a[hi];
        int i = lo;
        for (int j = lo; j < hi; ++j) {
            if (a[j] < pivot) {
                swap_values(a, i, j);
                ++i;
            }
        }
        swap_values(a, i, hi);
        int p = i;
        if (p - lo < hi - p) {
            quick_sort_rec(a, lo, p - 1);
            lo = p + 1;
        } else {
            quick_sort_rec(a, p + 1, hi);
            hi = p - 1;
        }
    }
}

void quick_sort(vector<int>& a) {
    int n = static_cast<int>(a.size());
    if (n > 1) quick_sort_rec(a, 0, n - 1);
}

void radix_sort(vector<int>& a) {
    int n = static_cast<int>(a.size());
    if (n < 2) return;
    vector<int> temp(n);
    vector<int>* src = &a;
    vector<int>* dst = &temp;
    const int shifts[] = {0, 8, 16};
    for (int shift : shifts) {
        int count[256] = {0};
        for (int value : *src) ++count[(value >> shift) & 255];
        int total = 0;
        for (int i = 0; i < 256; ++i) {
            int x = count[i];
            count[i] = total;
            total += x;
        }
        for (int value : *src) {
            int digit = (value >> shift) & 255;
            (*dst)[count[digit]++] = value;
        }
        swap(src, dst);
    }
    if (src != &a) a = *src;
}

void sift_down(vector<int>& a, int root, int n) {
    while (true) {
        int child = 2 * root + 1;
        if (child >= n) break;
        if (child + 1 < n && a[child + 1] > a[child]) ++child;
        if (a[root] >= a[child]) break;
        swap_values(a, root, child);
        root = child;
    }
}

void heap_sort(vector<int>& a) {
    int n = static_cast<int>(a.size());
    for (int start = n / 2 - 1; start >= 0; --start) sift_down(a, start, n);
    for (int end = n - 1; end > 0; --end) {
        swap_values(a, 0, end);
        sift_down(a, 0, end);
    }
}

// ---------------------------------------------------------------------------
// Versiones instrumentadas (solo para contar)
// ---------------------------------------------------------------------------
void bubble_sort_count(vector<int>& a, Counter& c) {
    int end = static_cast<int>(a.size()) - 1;
    while (end > 0) {
        bool swapped = false;
        for (int i = 0; i < end; ++i) {
            ++c.comparisons;
            if (a[i] > a[i + 1]) {
                swap_values(a, i, i + 1);
                ++c.swaps;
                swapped = true;
            }
        }
        if (!swapped) break;
        --end;
    }
}

void selection_sort_count(vector<int>& a, Counter& c) {
    int n = static_cast<int>(a.size());
    for (int i = 0; i < n - 1; ++i) {
        int m = i;
        for (int j = i + 1; j < n; ++j) {
            ++c.comparisons;
            if (a[j] < a[m]) m = j;
        }
        if (m != i) {
            swap_values(a, i, m);
            ++c.swaps;
        }
    }
}

void insertion_sort_count(vector<int>& a, Counter& c) {
    int n = static_cast<int>(a.size());
    for (int i = 1; i < n; ++i) {
        int j = i;
        while (j > 0) {
            ++c.comparisons;
            if (a[j - 1] <= a[j]) break;
            swap_values(a, j - 1, j);
            ++c.swaps;
            --j;
        }
    }
}

void merge_sort_rec_count(vector<int>& a, vector<int>& aux, int lo, int hi, Counter& c) {
    if (lo >= hi) return;
    int mid = lo + (hi - lo) / 2;
    merge_sort_rec_count(a, aux, lo, mid, c);
    merge_sort_rec_count(a, aux, mid + 1, hi, c);
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

void merge_sort_count(vector<int>& a, Counter& c) {
    int n = static_cast<int>(a.size());
    if (n < 2) return;
    vector<int> aux(n);
    merge_sort_rec_count(a, aux, 0, n - 1, c);
}

void shell_sort_count(vector<int>& a, Counter& c) {
    int n = static_cast<int>(a.size());
    int gap = 1;
    while (gap < n / 3) gap = gap * 3 + 1;
    while (gap >= 1) {
        for (int i = gap; i < n; ++i) {
            int j = i;
            while (j >= gap) {
                ++c.comparisons;
                if (a[j - gap] <= a[j]) break;
                swap_values(a, j - gap, j);
                ++c.swaps;
                j -= gap;
            }
        }
        gap /= 3;
    }
}

void bucket_sort_count(vector<int>& a, Counter& c) {
    int n = static_cast<int>(a.size());
    if (n < 2) return;
    int buckets_count = min(n, 100000);
    vector<vector<int>> buckets(buckets_count);
    for (int value : a) {
        int idx = static_cast<int>(static_cast<long long>(value) * buckets_count / VALUE_LIMIT);
        buckets[idx].push_back(value);
    }
    int k = 0;
    for (auto& bucket : buckets) {
        int m = static_cast<int>(bucket.size());
        for (int i = 1; i < m; ++i) {
            int key = bucket[i];
            int j = i - 1;
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
        for (int value : bucket) {
            a[k++] = value;
            ++c.swaps;
        }
    }
}

void quick_sort_rec_count(vector<int>& a, int lo, int hi, Counter& c) {
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        ++c.comparisons;
        if (a[mid] < a[lo]) {
            swap_values(a, lo, mid);
            ++c.swaps;
        }
        ++c.comparisons;
        if (a[hi] < a[lo]) {
            swap_values(a, lo, hi);
            ++c.swaps;
        }
        ++c.comparisons;
        if (a[hi] < a[mid]) {
            swap_values(a, mid, hi);
            ++c.swaps;
        }
        swap_values(a, mid, hi);
        ++c.swaps;
        int pivot = a[hi];
        int i = lo;
        for (int j = lo; j < hi; ++j) {
            ++c.comparisons;
            if (a[j] < pivot) {
                swap_values(a, i, j);
                ++c.swaps;
                ++i;
            }
        }
        swap_values(a, i, hi);
        ++c.swaps;
        int p = i;
        if (p - lo < hi - p) {
            quick_sort_rec_count(a, lo, p - 1, c);
            lo = p + 1;
        } else {
            quick_sort_rec_count(a, p + 1, hi, c);
            hi = p - 1;
        }
    }
}

void quick_sort_count(vector<int>& a, Counter& c) {
    int n = static_cast<int>(a.size());
    if (n > 1) quick_sort_rec_count(a, 0, n - 1, c);
}

void radix_sort_count(vector<int>& a, Counter& c) {
    int n = static_cast<int>(a.size());
    if (n < 2) return;
    vector<int> temp(n);
    vector<int>* src = &a;
    vector<int>* dst = &temp;
    const int shifts[] = {0, 8, 16};
    for (int shift : shifts) {
        int count[256] = {0};
        for (int value : *src) ++count[(value >> shift) & 255];
        int total = 0;
        for (int i = 0; i < 256; ++i) {
            int x = count[i];
            count[i] = total;
            total += x;
        }
        for (int value : *src) {
            int digit = (value >> shift) & 255;
            (*dst)[count[digit]++] = value;
            ++c.swaps;
        }
        swap(src, dst);
    }
    if (src != &a) {
        for (int i = 0; i < n; ++i) {
            a[i] = (*src)[i];
            ++c.swaps;
        }
    }
}

void sift_down_count(vector<int>& a, int root, int n, Counter& c) {
    while (true) {
        int child = 2 * root + 1;
        if (child >= n) break;
        if (child + 1 < n) {
            ++c.comparisons;
            if (a[child + 1] > a[child]) ++child;
        }
        ++c.comparisons;
        if (a[root] >= a[child]) break;
        swap_values(a, root, child);
        ++c.swaps;
        root = child;
    }
}

void heap_sort_count(vector<int>& a, Counter& c) {
    int n = static_cast<int>(a.size());
    for (int start = n / 2 - 1; start >= 0; --start) sift_down_count(a, start, n, c);
    for (int end = n - 1; end > 0; --end) {
        swap_values(a, 0, end);
        ++c.swaps;
        sift_down_count(a, 0, end, c);
    }
}

// ---------------------------------------------------------------------------
// Dispatch y programa principal
// ---------------------------------------------------------------------------
using CleanFn = void (*)(vector<int>&);
using CountedFn = void (*)(vector<int>&, Counter&);

CleanFn CLEAN[] = {bubble_sort,    selection_sort, insertion_sort, merge_sort,
                   shell_sort,    bucket_sort,    quick_sort,     radix_sort,
                   heap_sort};
CountedFn COUNTED[] = {bubble_sort_count,    selection_sort_count, insertion_sort_count,
                       merge_sort_count,     shell_sort_count,     bucket_sort_count,
                       quick_sort_count,     radix_sort_count,     heap_sort_count};

double measure_time(int algorithm_index, vector<int>& a) {
    auto start = chrono::steady_clock::now();
    CLEAN[algorithm_index](a);
    auto end = chrono::steady_clock::now();
    return chrono::duration<double, milli>(end - start).count();
}

bool should_timeout(int algorithm_index, int n, int type_index) {
    if (algorithm_index > 2) return false;  // solo Bubble, Selection, Insertion
    if (n < 100000) return false;
    bool ordered_input = (type_index == 1);
    if (algorithm_index == 1) return n >= 1000000;  // Selection siempre O(n^2)
    if (ordered_input) return false;                // Bubble/Insertion O(n)
    return n >= 1000000;
}

int main() {
    ofstream out("resultados_cpp.csv");
    if (!out) {
        cerr << "No se pudo crear resultados_cpp.csv" << endl;
        return 1;
    }

    out << "lenguaje,algoritmo,tamano,tipo_arreglo,tiempo_ms,comparaciones,intercambios,estado\n";
    out << fixed << setprecision(6);

    // Calentamiento (no se mide): activa caches antes de las pruebas.
    vector<int> warm_base = generate_random(2000);
    for (int ai = 0; ai < ALGORITHM_COUNT; ++ai) {
        vector<int> warm = warm_base;
        CLEAN[ai](warm);
    }

    for (int n : SIZES) {
        vector<int> base = generate_random(n);
        vector<int> ordered = base;
        sort(ordered.begin(), ordered.end());
        vector<int> inverse(ordered.rbegin(), ordered.rend());
        vector<int>* sources[] = {&base, &ordered, &inverse};

        for (int ai = 0; ai < ALGORITHM_COUNT; ++ai) {
            for (int ti = 0; ti < 3; ++ti) {
                if (should_timeout(ai, n, ti)) {
                    out << LANGUAGE << ',' << ALGORITHMS[ai] << ',' << n << ','
                        << TYPES[ti] << ",0.000000,0,0,timeout\n";
                    continue;
                }

                try {
                    double samples[3];
                    bool valid = true;
                    for (int rep = 0; rep < 3; ++rep) {
                        vector<int> timed = *sources[ti];
                        samples[rep] = measure_time(ai, timed);
                        if (!is_sorted(timed)) {
                            valid = false;
                            break;
                        }
                    }
                    if (!valid) {
                        out << LANGUAGE << ',' << ALGORITHMS[ai] << ',' << n << ','
                            << TYPES[ti] << ",0.000000,0,0,error\n";
                        continue;
                    }
                    sort(samples, samples + 3);
                    double elapsed = samples[1];

                    Counter counter;
                    vector<int> counted = *sources[ti];
                    COUNTED[ai](counted, counter);
                    if (!is_sorted(counted)) {
                        out << LANGUAGE << ',' << ALGORITHMS[ai] << ',' << n << ','
                            << TYPES[ti] << ',' << elapsed << ",0,0,error\n";
                        continue;
                    }

                    out << LANGUAGE << ',' << ALGORITHMS[ai] << ',' << n << ','
                        << TYPES[ti] << ',' << elapsed << ',' << counter.comparisons
                        << ',' << counter.swaps << ",ok\n";
                } catch (...) {
                    out << LANGUAGE << ',' << ALGORITHMS[ai] << ',' << n << ','
                        << TYPES[ti] << ",0.000000,0,0,error\n";
                }
            }
        }
    }

    out.close();
    cout << "Resultados escritos en resultados_cpp.csv" << endl;
    return 0;
}
