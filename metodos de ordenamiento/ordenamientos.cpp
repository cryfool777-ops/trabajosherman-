#include <iostream>
#include <vector>
#include <algorithm>
#include <random>
#include <chrono>
#include <string>
#include <cstdlib>
#include <cmath>
#include <list>

using namespace std;

// BUBBLE SORT
// Cómo funciona: Compara elementos adyacentes e intercambia si están en orden incorrecto.
// Repite hasta que no haya intercambios. Cada pasada coloca el mayor al final.
// Complejidad: Mejor O(n), Promedio O(n^2), Peor O(n^2) | Estable: Sí
vector<int> BubbleSort(const vector<int> &arr) {
    vector<int> copia = arr;
    int n = copia.size();
    for (int i = 0; i < n - 1; i++) {
        bool intercambiado = false;
        for (int j = 0; j < n - i - 1; j++) {
            if (copia[j] > copia[j + 1]) {
                swap(copia[j], copia[j + 1]);
                intercambiado = true;
            }
        }
        if (!intercambiado) break;
    }
    return copia;
}

// SELECTION SORT
// Cómo funciona: Busca el elemento mínimo en la parte no ordenada y lo coloca al inicio.
// Repite para cada posición. No depende de intercambios adyacentes.
// Complejidad: Mejor O(n^2), Promedio O(n^2), Peor O(n^2) | Estable: No
vector<int> SelectionSort(const vector<int> &arr) {
    vector<int> copia = arr;
    int n = copia.size();
    for (int i = 0; i < n - 1; i++) {
        int minIndex = i;
        for (int j = i + 1; j < n; j++) {
            if (copia[j] < copia[minIndex])
                minIndex = j;
        }
        if (minIndex != i) {
            swap(copia[i], copia[minIndex]);
        }
    }
    return copia;
}

// INSERTION SORT
// Cómo funciona: Toma cada elemento y lo inserta en la posición correcta en la parte ya ordenada.
// Eficiente para arreglos pequeños o parcialmente ordenados.
// Complejidad: Mejor O(n), Promedio O(n^2), Peor O(n^2) | Estable: Sí
vector<int> InsertionSort(const vector<int> &arr) {
    vector<int> copia = arr;
    int n = copia.size();
    for (int i = 1; i < n; i++) {
        int key = copia[i];
        int j = i - 1;
        while (j >= 0 && copia[j] > key) {
            copia[j + 1] = copia[j];
            j--;
        }
        copia[j + 1] = key;
    }
    return copia;
}

// MERGE SORT
// Cómo funciona: Divide recursivamente el arreglo en mitades hasta elementos individuales.
// Luego fusiona las mitades ordenadas usando un arreglo auxiliar.
// Complejidad: Mejor O(n log n), Promedio O(n log n), Peor O(n log n) | Estable: Sí
void Merge(vector<int> &arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    vector<int> L(n1), R(n2);
    
    for (int i = 0; i < n1; i++) L[i] = arr[left + i];
    for (int j = 0; j < n2; j++) R[j] = arr[mid + 1 + j];
    
    int i = 0, j = 0, k = left;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k++] = L[i++];
        } else {
            arr[k++] = R[j++];
        }
    }
    while (i < n1) arr[k++] = L[i++];
    while (j < n2) arr[k++] = R[j++];
}

void MergeSortRecursive(vector<int> &arr, int left, int right) {
    if (left < right) {
        int mid = (left + right) / 2;
        MergeSortRecursive(arr, left, mid);
        MergeSortRecursive(arr, mid + 1, right);
        Merge(arr, left, mid, right);
    }
}

vector<int> MergeSort(const vector<int> &arr) {
    vector<int> copia = arr;
    if (copia.size() <= 1) return copia;
    MergeSortRecursive(copia, 0, copia.size() - 1);
    return copia;
}

// SHELL SORT
// Cómo funciona: Ordenamiento por inserción con saltos (gap). Usa secuencia n/2, n/4, ..., 1.
// Reduce el número de intercambios comparado con insertion sort simple.
// Complejidad: Mejor O(n log^2 n), Promedio O(n^(3/2)), Peor O(n^2) | Estable: No
vector<int> ShellSort(const vector<int> &arr) {
    vector<int> copia = arr;
    int n = copia.size();
    for (int gap = n / 2; gap > 0; gap /= 2) {
        for (int i = gap; i < n; i++) {
            int temp = copia[i];
            int j = i;
            while (j >= gap && copia[j - gap] > temp) {
                copia[j] = copia[j - gap];
                j -= gap;
            }
            copia[j] = temp;
        }
    }
    return copia;
}

// BUCKET SORT
// Cómo funciona: Distribuye elementos en cubetas según rango, ordena cada cubeta con insertion sort.
// Para enteros no negativos. Eficiente cuando valores están distribuidos uniformemente.
// Complejidad: Mejor O(n+k), Promedio O(n+k), Peor O(n^2) | Estable: Sí
vector<int> InsertionSortVector(const vector<int> &arr) {
    vector<int> copia = arr;
    int n = copia.size();
    for (int i = 1; i < n; i++) {
        int key = copia[i];
        int j = i - 1;
        while (j >= 0 && copia[j] > key) {
            copia[j + 1] = copia[j];
            j--;
        }
        copia[j + 1] = key;
    }
    return copia;
}

vector<int> BucketSort(const vector<int> &arr) {
    vector<int> copia = arr;
    int n = copia.size();
    if (n <= 1) return copia;
    
    int maxVal = copia[0], minVal = copia[0];
    for (int i = 1; i < n; i++) {
        if (copia[i] > maxVal) maxVal = copia[i];
        if (copia[i] < minVal) minVal = copia[i];
    }
    
    int bucketCount = n;
    vector<vector<int> > buckets(bucketCount);
    
    for (int i = 0; i < n; i++) {
        int bucketIndex = (int)((copia[i] - minVal) * (bucketCount - 1) / (maxVal - minVal + 1));
        if (bucketIndex < 0) bucketIndex = 0;
        if (bucketIndex >= bucketCount) bucketIndex = bucketCount - 1;
        buckets[bucketIndex].push_back(copia[i]);
    }
    
    for (int i = 0; i < bucketCount; i++) {
        buckets[i] = InsertionSortVector(buckets[i]);
    }
    
    int index = 0;
    for (int i = 0; i < bucketCount; i++) {
        for (size_t j = 0; j < buckets[i].size(); j++) {
            copia[index++] = buckets[i][j];
        }
    }
    return copia;
}

// QUICK SORT
// Cómo funciona: Elige pivote (mediana de tres), divide en menores y mayores, ordena recursivamente.
// Usa mediana de tres para evitar peor caso en arreglos ordenados/inversos.
// Complejidad: Mejor O(n log n), Promedio O(n log n), Peor O(n^2) | Estable: No
void SwapVec(vector<int> &arr, int i, int j) {
    int temp = arr[i];
    arr[i] = arr[j];
    arr[j] = temp;
}

int Partition(vector<int> &arr, int left, int right) {
    int mid = (left + right) / 2;
    if (arr[mid] < arr[left]) SwapVec(arr, left, mid);
    if (arr[right] < arr[left]) SwapVec(arr, left, right);
    if (arr[right] < arr[mid]) SwapVec(arr, mid, right);
    SwapVec(arr, mid, right - 1);
    
    int pivot = arr[right - 1];
    int i = left;
    for (int j = left; j <= right - 2; j++) {
        if (arr[j] <= pivot) {
            SwapVec(arr, i, j);
            i++;
        }
    }
    SwapVec(arr, i, right - 1);
    return i;
}

void QuickSortRecursive(vector<int> &arr, int left, int right) {
    if (left < right) {
        int pivotIndex = Partition(arr, left, right);
        QuickSortRecursive(arr, left, pivotIndex - 1);
        QuickSortRecursive(arr, pivotIndex + 1, right);
    }
}

vector<int> QuickSort(const vector<int> &arr) {
    vector<int> copia = arr;
    if (copia.size() <= 1) return copia;
    QuickSortRecursive(copia, 0, copia.size() - 1);
    return copia;
}

// RADIX SORT
// Cómo funciona: Ordena por dígitos de LSD a MSD, usando counting sort por cada dígito (base 10).
// Para enteros no negativos.
// Complejidad: Mejor O(d(n+k)), Promedio O(d(n+k)), Peor O(d(n+k)) | Estable: Sí
void CountingSortByDigitVec(vector<int> &arr, int exp) {
    int n = arr.size();
    vector<int> output(n);
    vector<int> count(10, 0);
    
    for (int i = 0; i < n; i++)
        count[(arr[i] / exp) % 10]++;
    
    for (int i = 1; i < 10; i++)
        count[i] += count[i - 1];
    
    for (int i = n - 1; i >= 0; i--) {
        output[count[(arr[i] / exp) % 10] - 1] = arr[i];
        count[(arr[i] / exp) % 10]--;
    }
    
    for (int i = 0; i < n; i++)
        arr[i] = output[i];
}

vector<int> RadixSort(const vector<int> &arr) {
    vector<int> copia = arr;
    int n = copia.size();
    if (n <= 1) return copia;
    
    int maxVal = copia[0];
    for (int i = 1; i < n; i++)
        if (copia[i] > maxVal) maxVal = copia[i];
    
    for (int exp = 1; maxVal / exp > 0; exp *= 10) {
        CountingSortByDigitVec(copia, exp);
    }
    return copia;
}

// HEAP SORT
// Cómo funciona: Construye un max-heap sobre el arreglo, extrae el máximo repetidamente al final.
// Trabaja sobre el mismo arreglo.
// Complejidad: Mejor O(n log n), Promedio O(n log n), Peor O(n log n) | Estable: No
void Heapify(vector<int> &arr, int n, int i) {
    int largest = i;
    int left = 2 * i + 1;
    int right = 2 * i + 2;
    
    if (left < n && arr[left] > arr[largest])
        largest = left;
    if (right < n && arr[right] > arr[largest])
        largest = right;
    
    if (largest != i) {
        SwapVec(arr, i, largest);
        Heapify(arr, n, largest);
    }
}

vector<int> HeapSort(const vector<int> &arr) {
    vector<int> copia = arr;
    int n = copia.size();
    if (n <= 1) return copia;
    
    for (int i = n / 2 - 1; i >= 0; i--)
        Heapify(copia, n, i);
    
    for (int i = n - 1; i > 0; i--) {
        SwapVec(copia, 0, i);
        Heapify(copia, i, 0);
    }
    return copia;
}

void ImprimirArray(const string &nombre, const vector<int> &arr) {
    cout << nombre << ": [";
    for (size_t i = 0; i < arr.size(); i++) {
        cout << arr[i];
        if (i < arr.size() - 1) cout << ", ";
    }
    cout << "]" << endl;
}

bool EstaOrdenado(const vector<int> &arr) {
    for (size_t i = 1; i < arr.size(); i++) {
        if (arr[i] < arr[i - 1]) return false;
    }
    return true;
}

vector<int> GenerarAleatorio(int tamano, int semilla) {
    vector<int> arr(tamano);
    mt19937 rng(semilla);
    uniform_int_distribution<int> dist(0, 100);
    for (int i = 0; i < tamano; i++)
        arr[i] = dist(rng);
    return arr;
}

void ProbarAlgoritmo(const string &nombre, const vector<int> &original, vector<int>(*algoritmo)(const vector<int>&)) {
    cout << "\n=== " << nombre << " ===" << endl;
    ImprimirArray("Antes", original);
    vector<int> resultado = algoritmo(original);
    ImprimirArray("Después", resultado);
    if (EstaOrdenado(resultado)) cout << "OK" << endl;
    else cout << "ERROR" << endl;
}

int main() {
    cout << "========================================" << endl;
    cout << "   ALGORITMOS DE ORDENAMIENTO - C++" << endl;
    cout << "========================================" << endl;
    
    vector<int> ejemplo = {64, 34, 25, 12, 22, 11, 90, 5};
    
    cout << "\n--- PRUEBA 1: Arreglo de ejemplo fijo ---" << endl;
    ProbarAlgoritmo("Bubble Sort", ejemplo, BubbleSort);
    ProbarAlgoritmo("Selection Sort", ejemplo, SelectionSort);
    ProbarAlgoritmo("Insertion Sort", ejemplo, InsertionSort);
    ProbarAlgoritmo("Merge Sort", ejemplo, MergeSort);
    ProbarAlgoritmo("Shell Sort", ejemplo, ShellSort);
    ProbarAlgoritmo("Bucket Sort", ejemplo, BucketSort);
    ProbarAlgoritmo("Quick Sort", ejemplo, QuickSort);
    ProbarAlgoritmo("Radix Sort", ejemplo, RadixSort);
    ProbarAlgoritmo("Heap Sort", ejemplo, HeapSort);
    
    cout << "\n\n--- PRUEBA 2: Arreglo aleatorio (20 elementos, semilla fija) ---" << endl;
    vector<int> aleatorio = GenerarAleatorio(20, 12345);
    ProbarAlgoritmo("Bubble Sort", aleatorio, BubbleSort);
    ProbarAlgoritmo("Selection Sort", aleatorio, SelectionSort);
    ProbarAlgoritmo("Insertion Sort", aleatorio, InsertionSort);
    ProbarAlgoritmo("Merge Sort", aleatorio, MergeSort);
    ProbarAlgoritmo("Shell Sort", aleatorio, ShellSort);
    ProbarAlgoritmo("Bucket Sort", aleatorio, BucketSort);
    ProbarAlgoritmo("Quick Sort", aleatorio, QuickSort);
    ProbarAlgoritmo("Radix Sort", aleatorio, RadixSort);
    ProbarAlgoritmo("Heap Sort", aleatorio, HeapSort);
    
    cout << "\n\n--- PRUEBA 3: Arreglo ya ordenado ---" << endl;
    vector<int> ordenado = {1, 2, 3, 4, 5, 6, 7, 8};
    ProbarAlgoritmo("Bubble Sort", ordenado, BubbleSort);
    ProbarAlgoritmo("Selection Sort", ordenado, SelectionSort);
    ProbarAlgoritmo("Insertion Sort", ordenado, InsertionSort);
    ProbarAlgoritmo("Merge Sort", ordenado, MergeSort);
    ProbarAlgoritmo("Shell Sort", ordenado, ShellSort);
    ProbarAlgoritmo("Bucket Sort", ordenado, BucketSort);
    ProbarAlgoritmo("Quick Sort", ordenado, QuickSort);
    ProbarAlgoritmo("Radix Sort", ordenado, RadixSort);
    ProbarAlgoritmo("Heap Sort", ordenado, HeapSort);
    
    cout << "\n\n--- PRUEBA 4: Arreglo inverso ---" << endl;
    vector<int> inverso = {8, 7, 6, 5, 4, 3, 2, 1};
    ProbarAlgoritmo("Bubble Sort", inverso, BubbleSort);
    ProbarAlgoritmo("Selection Sort", inverso, SelectionSort);
    ProbarAlgoritmo("Insertion Sort", inverso, InsertionSort);
    ProbarAlgoritmo("Merge Sort", inverso, MergeSort);
    ProbarAlgoritmo("Shell Sort", inverso, ShellSort);
    ProbarAlgoritmo("Bucket Sort", inverso, BucketSort);
    ProbarAlgoritmo("Quick Sort", inverso, QuickSort);
    ProbarAlgoritmo("Radix Sort", inverso, RadixSort);
    ProbarAlgoritmo("Heap Sort", inverso, HeapSort);
    
    cout << "\n\n--- PRUEBA 5: Casos borde ---" << endl;
    vector<int> vacio;
    cout << "\n=== Arreglo vacío ===" << endl;
    ImprimirArray("Antes", vacio);
    cout << "Bubble Sort - " << (EstaOrdenado(BubbleSort(vacio)) ? "OK" : "ERROR") << endl;
    cout << "Quick Sort - " << (EstaOrdenado(QuickSort(vacio)) ? "OK" : "ERROR") << endl;
    cout << "Merge Sort - " << (EstaOrdenado(MergeSort(vacio)) ? "OK" : "ERROR") << endl;
    
    vector<int> unElemento = {42};
    cout << "\n=== Un elemento ===" << endl;
    ImprimirArray("Antes", unElemento);
    cout << "Bubble Sort - " << (EstaOrdenado(BubbleSort(unElemento)) ? "OK" : "ERROR") << endl;
    cout << "Heap Sort - " << (EstaOrdenado(HeapSort(unElemento)) ? "OK" : "ERROR") << endl;
    
    vector<int> repetidos = {5, 2, 8, 2, 9, 5, 1, 5};
    cout << "\n=== Elementos repetidos ===" << endl;
    ImprimirArray("Antes", repetidos);
    ProbarAlgoritmo("Bubble Sort", repetidos, BubbleSort);
    ProbarAlgoritmo("Quick Sort", repetidos, QuickSort);
    ProbarAlgoritmo("Merge Sort", repetidos, MergeSort);
    ProbarAlgoritmo("Radix Sort", repetidos, RadixSort);
    
    return 0;
}
