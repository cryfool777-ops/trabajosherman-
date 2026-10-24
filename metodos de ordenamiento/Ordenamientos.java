import java.util.*;
import java.util.function.Function;

public class Ordenamientos {
    
    // BUBBLE SORT
    // Cómo funciona: Compara elementos adyacentes e intercambia si están en orden incorrecto.
    // Repite hasta que no haya intercambios. Cada pasada coloca el mayor al final.
    // Complejidad: Mejor O(n), Promedio O(n^2), Peor O(n^2) | Estable: Sí
    public static int[] bubbleSort(int[] arr) {
        int[] copia = Arrays.copyOf(arr, arr.length);
        int n = copia.length;
        for (int i = 0; i < n - 1; i++) {
            boolean intercambiado = false;
            for (int j = 0; j < n - i - 1; j++) {
                if (copia[j] > copia[j + 1]) {
                    int temp = copia[j];
                    copia[j] = copia[j + 1];
                    copia[j + 1] = temp;
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
    public static int[] selectionSort(int[] arr) {
        int[] copia = Arrays.copyOf(arr, arr.length);
        int n = copia.length;
        for (int i = 0; i < n - 1; i++) {
            int minIndex = i;
            for (int j = i + 1; j < n; j++) {
                if (copia[j] < copia[minIndex])
                    minIndex = j;
            }
            if (minIndex != i) {
                int temp = copia[i];
                copia[i] = copia[minIndex];
                copia[minIndex] = temp;
            }
        }
        return copia;
    }
    
    // INSERTION SORT
    // Cómo funciona: Toma cada elemento y lo inserta en la posición correcta en la parte ya ordenada.
    // Eficiente para arreglos pequeños o parcialmente ordenados.
    // Complejidad: Mejor O(n), Promedio O(n^2), Peor O(n^2) | Estable: Sí
    public static int[] insertionSort(int[] arr) {
        int[] copia = Arrays.copyOf(arr, arr.length);
        int n = copia.length;
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
    private static void merge(int[] arr, int left, int mid, int right) {
        int n1 = mid - left + 1;
        int n2 = right - mid;
        int[] L = new int[n1];
        int[] R = new int[n2];
        
        System.arraycopy(arr, left, L, 0, n1);
        System.arraycopy(arr, mid + 1, R, 0, n2);
        
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
    
    private static void mergeSortRecursive(int[] arr, int left, int right) {
        if (left < right) {
            int mid = (left + right) / 2;
            mergeSortRecursive(arr, left, mid);
            mergeSortRecursive(arr, mid + 1, right);
            merge(arr, left, mid, right);
        }
    }
    
    public static int[] mergeSort(int[] arr) {
        int[] copia = Arrays.copyOf(arr, arr.length);
        if (copia.length <= 1) return copia;
        mergeSortRecursive(copia, 0, copia.length - 1);
        return copia;
    }
    
    // SHELL SORT
    // Cómo funciona: Ordenamiento por inserción con saltos (gap). Usa secuencia n/2, n/4, ..., 1.
    // Reduce el número de intercambios comparado con insertion sort simple.
    // Complejidad: Mejor O(n log^2 n), Promedio O(n^(3/2)), Peor O(n^2) | Estable: No
    public static int[] shellSort(int[] arr) {
        int[] copia = Arrays.copyOf(arr, arr.length);
        int n = copia.length;
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
    private static int[] insertionSortArray(int[] arr) {
        int[] copia = Arrays.copyOf(arr, arr.length);
        int n = copia.length;
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
    
    public static int[] bucketSort(int[] arr) {
        int[] copia = Arrays.copyOf(arr, arr.length);
        int n = copia.length;
        if (n <= 1) return copia;
        
        int maxVal = copia[0], minVal = copia[0];
        for (int i = 1; i < n; i++) {
            if (copia[i] > maxVal) maxVal = copia[i];
            if (copia[i] < minVal) minVal = copia[i];
        }
        
        int bucketCount = n;
        ArrayList<Integer>[] buckets = new ArrayList[bucketCount];
        for (int i = 0; i < bucketCount; i++)
            buckets[i] = new ArrayList<Integer>();
        
        for (int i = 0; i < n; i++) {
            int bucketIndex = (int)((copia[i] - minVal) * (bucketCount - 1) / (maxVal - minVal + 1));
            if (bucketIndex < 0) bucketIndex = 0;
            if (bucketIndex >= bucketCount) bucketIndex = bucketCount - 1;
            buckets[bucketIndex].add(copia[i]);
        }
        
        int index = 0;
        for (int i = 0; i < bucketCount; i++) {
            int[] bucketArray = new int[buckets[i].size()];
            for (int j = 0; j < buckets[i].size(); j++)
                bucketArray[j] = buckets[i].get(j);
            bucketArray = insertionSortArray(bucketArray);
            for (int j = 0; j < bucketArray.length; j++)
                copia[index++] = bucketArray[j];
        }
        return copia;
    }
    
    // QUICK SORT
    // Cómo funciona: Elige pivote (mediana de tres), divide en menores y mayores, ordena recursivamente.
    // Usa mediana de tres para evitar peor caso en arreglos ordenados/inversos.
    // Complejidad: Mejor O(n log n), Promedio O(n log n), Peor O(n^2) | Estable: No
    private static void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
    
    private static int partition(int[] arr, int left, int right) {
        int mid = (left + right) / 2;
        if (arr[mid] < arr[left]) swap(arr, left, mid);
        if (arr[right] < arr[left]) swap(arr, left, right);
        if (arr[right] < arr[mid]) swap(arr, mid, right);
        swap(arr, mid, right - 1);
        
        int pivot = arr[right - 1];
        int i = left;
        for (int j = left; j <= right - 2; j++) {
            if (arr[j] <= pivot) {
                swap(arr, i, j);
                i++;
            }
        }
        swap(arr, i, right - 1);
        return i;
    }
    
    private static void quickSortRecursive(int[] arr, int left, int right) {
        if (left < right) {
            int pivotIndex = partition(arr, left, right);
            quickSortRecursive(arr, left, pivotIndex - 1);
            quickSortRecursive(arr, pivotIndex + 1, right);
        }
    }
    
    public static int[] quickSort(int[] arr) {
        int[] copia = Arrays.copyOf(arr, arr.length);
        if (copia.length <= 1) return copia;
        quickSortRecursive(copia, 0, copia.length - 1);
        return copia;
    }
    
    // RADIX SORT
    // Cómo funciona: Ordena por dígitos de LSD a MSD, usando counting sort por cada dígito (base 10).
    // Para enteros no negativos.
    // Complejidad: Mejor O(d(n+k)), Promedio O(d(n+k)), Peor O(d(n+k)) | Estable: Sí
    private static void countingSortByDigit(int[] arr, int exp) {
        int n = arr.length;
        int[] output = new int[n];
        int[] count = new int[10];
        
        for (int i = 0; i < n; i++)
            count[(arr[i] / exp) % 10]++;
        
        for (int i = 1; i < 10; i++)
            count[i] += count[i - 1];
        
        for (int i = n - 1; i >= 0; i--) {
            output[count[(arr[i] / exp) % 10] - 1] = arr[i];
            count[(arr[i] / exp) % 10]--;
        }
        
        System.arraycopy(output, 0, arr, 0, n);
    }
    
    public static int[] radixSort(int[] arr) {
        int[] copia = Arrays.copyOf(arr, arr.length);
        int n = copia.length;
        if (n <= 1) return copia;
        
        int maxVal = copia[0];
        for (int i = 1; i < n; i++)
            if (copia[i] > maxVal) maxVal = copia[i];
        
        for (int exp = 1; maxVal / exp > 0; exp *= 10) {
            countingSortByDigit(copia, exp);
        }
        return copia;
    }
    
    // HEAP SORT
    // Cómo funciona: Construye un max-heap sobre el arreglo, extrae el máximo repetidamente al final.
    // Trabaja sobre el mismo arreglo.
    // Complejidad: Mejor O(n log n), Promedio O(n log n), Peor O(n log n) | Estable: No
    private static void heapify(int[] arr, int n, int i) {
        int largest = i;
        int left = 2 * i + 1;
        int right = 2 * i + 2;
        
        if (left < n && arr[left] > arr[largest])
            largest = left;
        if (right < n && arr[right] > arr[largest])
            largest = right;
        
        if (largest != i) {
            swap(arr, i, largest);
            heapify(arr, n, largest);
        }
    }
    
    public static int[] heapSort(int[] arr) {
        int[] copia = Arrays.copyOf(arr, arr.length);
        int n = copia.length;
        if (n <= 1) return copia;
        
        for (int i = n / 2 - 1; i >= 0; i--)
            heapify(copia, n, i);
        
        for (int i = n - 1; i > 0; i--) {
            swap(copia, 0, i);
            heapify(copia, i, 0);
        }
        return copia;
    }
    
    private static void imprimirArray(String nombre, int[] arr) {
        System.out.print(nombre + ": [");
        for (int i = 0; i < arr.length; i++) {
            System.out.print(arr[i]);
            if (i < arr.length - 1) System.out.print(", ");
        }
        System.out.println("]");
    }
    
    private static boolean estaOrdenado(int[] arr) {
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] < arr[i - 1]) return false;
        }
        return true;
    }
    
    private static int[] generarAleatorio(int tamano, int semilla) {
        Random rnd = new Random(semilla);
        int[] arr = new int[tamano];
        for (int i = 0; i < tamano; i++)
            arr[i] = rnd.nextInt(100);
        return arr;
    }
    
    private static void probarAlgoritmo(String nombre, int[] original, Function<int[], int[]> algoritmo) {
        System.out.println("\n=== " + nombre + " ===");
        imprimirArray("Antes", original);
        int[] resultado = algoritmo.apply(original);
        imprimirArray("Después", resultado);
        System.out.println(estaOrdenado(resultado) ? "OK" : "ERROR");
    }
    
    public static void main(String[] args) {
        System.out.println("========================================");
        System.out.println("   ALGORITMOS DE ORDENAMIENTO - Java");
        System.out.println("========================================");
        
        int[] ejemplo = {64, 34, 25, 12, 22, 11, 90, 5};
        
        System.out.println("\n--- PRUEBA 1: Arreglo de ejemplo fijo ---");
        probarAlgoritmo("Bubble Sort", ejemplo, Ordenamientos::bubbleSort);
        probarAlgoritmo("Selection Sort", ejemplo, Ordenamientos::selectionSort);
        probarAlgoritmo("Insertion Sort", ejemplo, Ordenamientos::insertionSort);
        probarAlgoritmo("Merge Sort", ejemplo, Ordenamientos::mergeSort);
        probarAlgoritmo("Shell Sort", ejemplo, Ordenamientos::shellSort);
        probarAlgoritmo("Bucket Sort", ejemplo, Ordenamientos::bucketSort);
        probarAlgoritmo("Quick Sort", ejemplo, Ordenamientos::quickSort);
        probarAlgoritmo("Radix Sort", ejemplo, Ordenamientos::radixSort);
        probarAlgoritmo("Heap Sort", ejemplo, Ordenamientos::heapSort);
        
        System.out.println("\n\n--- PRUEBA 2: Arreglo aleatorio (20 elementos, semilla fija) ---");
        int[] aleatorio = generarAleatorio(20, 12345);
        probarAlgoritmo("Bubble Sort", aleatorio, Ordenamientos::bubbleSort);
        probarAlgoritmo("Selection Sort", aleatorio, Ordenamientos::selectionSort);
        probarAlgoritmo("Insertion Sort", aleatorio, Ordenamientos::insertionSort);
        probarAlgoritmo("Merge Sort", aleatorio, Ordenamientos::mergeSort);
        probarAlgoritmo("Shell Sort", aleatorio, Ordenamientos::shellSort);
        probarAlgoritmo("Bucket Sort", aleatorio, Ordenamientos::bucketSort);
        probarAlgoritmo("Quick Sort", aleatorio, Ordenamientos::quickSort);
        probarAlgoritmo("Radix Sort", aleatorio, Ordenamientos::radixSort);
        probarAlgoritmo("Heap Sort", aleatorio, Ordenamientos::heapSort);
        
        System.out.println("\n\n--- PRUEBA 3: Arreglo ya ordenado ---");
        int[] ordenado = {1, 2, 3, 4, 5, 6, 7, 8};
        probarAlgoritmo("Bubble Sort", ordenado, Ordenamientos::bubbleSort);
        probarAlgoritmo("Selection Sort", ordenado, Ordenamientos::selectionSort);
        probarAlgoritmo("Insertion Sort", ordenado, Ordenamientos::insertionSort);
        probarAlgoritmo("Merge Sort", ordenado, Ordenamientos::mergeSort);
        probarAlgoritmo("Shell Sort", ordenado, Ordenamientos::shellSort);
        probarAlgoritmo("Bucket Sort", ordenado, Ordenamientos::bucketSort);
        probarAlgoritmo("Quick Sort", ordenado, Ordenamientos::quickSort);
        probarAlgoritmo("Radix Sort", ordenado, Ordenamientos::radixSort);
        probarAlgoritmo("Heap Sort", ordenado, Ordenamientos::heapSort);
        
        System.out.println("\n\n--- PRUEBA 4: Arreglo inverso ---");
        int[] inverso = {8, 7, 6, 5, 4, 3, 2, 1};
        probarAlgoritmo("Bubble Sort", inverso, Ordenamientos::bubbleSort);
        probarAlgoritmo("Selection Sort", inverso, Ordenamientos::selectionSort);
        probarAlgoritmo("Insertion Sort", inverso, Ordenamientos::insertionSort);
        probarAlgoritmo("Merge Sort", inverso, Ordenamientos::mergeSort);
        probarAlgoritmo("Shell Sort", inverso, Ordenamientos::shellSort);
        probarAlgoritmo("Bucket Sort", inverso, Ordenamientos::bucketSort);
        probarAlgoritmo("Quick Sort", inverso, Ordenamientos::quickSort);
        probarAlgoritmo("Radix Sort", inverso, Ordenamientos::radixSort);
        probarAlgoritmo("Heap Sort", inverso, Ordenamientos::heapSort);
        
        System.out.println("\n\n--- PRUEBA 5: Casos borde ---");
        int[] vacio = {};
        System.out.println("\n=== Arreglo vacío ===");
        imprimirArray("Antes", vacio);
        System.out.println("Bubble Sort - " + (estaOrdenado(bubbleSort(vacio)) ? "OK" : "ERROR"));
        System.out.println("Quick Sort - " + (estaOrdenado(quickSort(vacio)) ? "OK" : "ERROR"));
        System.out.println("Merge Sort - " + (estaOrdenado(mergeSort(vacio)) ? "OK" : "ERROR"));
        
        int[] unElemento = {42};
        System.out.println("\n=== Un elemento ===");
        imprimirArray("Antes", unElemento);
        System.out.println("Bubble Sort - " + (estaOrdenado(bubbleSort(unElemento)) ? "OK" : "ERROR"));
        System.out.println("Heap Sort - " + (estaOrdenado(heapSort(unElemento)) ? "OK" : "ERROR"));
        
        int[] repetidos = {5, 2, 8, 2, 9, 5, 1, 5};
        System.out.println("\n=== Elementos repetidos ===");
        imprimirArray("Antes", repetidos);
        probarAlgoritmo("Bubble Sort", repetidos, Ordenamientos::bubbleSort);
        probarAlgoritmo("Quick Sort", repetidos, Ordenamientos::quickSort);
        probarAlgoritmo("Merge Sort", repetidos, Ordenamientos::mergeSort);
        probarAlgoritmo("Radix Sort", repetidos, Ordenamientos::radixSort);
    }
}
