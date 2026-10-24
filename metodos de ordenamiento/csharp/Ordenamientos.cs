using System;
using System.Collections.Generic;
using System.Linq;

class Program
{
    // BUBBLE SORT
    // Cómo funciona: Compara elementos adyacentes e intercambia si están en orden incorrecto.
    // Repite hasta que no haya intercambios. Cada pasada coloca el mayor al final.
    // Complejidad: Mejor O(n), Promedio O(n^2), Peor O(n^2) | Estable: Sí
    static int[] BubbleSort(int[] arr)
    {
        int[] copia = (int[])arr.Clone();
        int n = copia.Length;
        for (int i = 0; i < n - 1; i++)
        {
            bool intercambiado = false;
            for (int j = 0; j < n - i - 1; j++)
            {
                if (copia[j] > copia[j + 1])
                {
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
    static int[] SelectionSort(int[] arr)
    {
        int[] copia = (int[])arr.Clone();
        int n = copia.Length;
        for (int i = 0; i < n - 1; i++)
        {
            int minIndex = i;
            for (int j = i + 1; j < n; j++)
            {
                if (copia[j] < copia[minIndex])
                    minIndex = j;
            }
            if (minIndex != i)
            {
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
    static int[] InsertionSort(int[] arr)
    {
        int[] copia = (int[])arr.Clone();
        int n = copia.Length;
        for (int i = 1; i < n; i++)
        {
            int key = copia[i];
            int j = i - 1;
            while (j >= 0 && copia[j] > key)
            {
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
    static int[] MergeSort(int[] arr)
    {
        int[] copia = (int[])arr.Clone();
        if (copia.Length <= 1) return copia;
        MergeSortRecursive(copia, 0, copia.Length - 1);
        return copia;
    }

    static void MergeSortRecursive(int[] arr, int left, int right)
    {
        if (left < right)
        {
            int mid = (left + right) / 2;
            MergeSortRecursive(arr, left, mid);
            MergeSortRecursive(arr, mid + 1, right);
            Merge(arr, left, mid, right);
        }
    }

    static void Merge(int[] arr, int left, int mid, int right)
    {
        int n1 = mid - left + 1;
        int n2 = right - mid;
        int[] L = new int[n1];
        int[] R = new int[n2];
        
        Array.Copy(arr, left, L, 0, n1);
        Array.Copy(arr, mid + 1, R, 0, n2);
        
        int i = 0, j = 0, k = left;
        while (i < n1 && j < n2)
        {
            if (L[i] <= R[j])
            {
                arr[k++] = L[i++];
            }
            else
            {
                arr[k++] = R[j++];
            }
        }
        while (i < n1) arr[k++] = L[i++];
        while (j < n2) arr[k++] = R[j++];
    }

    // SHELL SORT
    // Cómo funciona: Ordenamiento por inserción con saltos (gap). Usa secuencia n/2, n/4, ..., 1.
    // Reduce el número de intercambios comparado con insertion sort simple.
    // Complejidad: Mejor O(n log^2 n), Promedio O(n^(3/2)), Peor O(n^2) | Estable: No
    static int[] ShellSort(int[] arr)
    {
        int[] copia = (int[])arr.Clone();
        int n = copia.Length;
        for (int gap = n / 2; gap > 0; gap /= 2)
        {
            for (int i = gap; i < n; i++)
            {
                int temp = copia[i];
                int j = i;
                while (j >= gap && copia[j - gap] > temp)
                {
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
    // Complejidad: Mejor O(n+k), Promedio O(n+k), Peor O(n^2) | Estable: Sí (con insertion sort estable)
    static int[] BucketSort(int[] arr)
    {
        int[] copia = (int[])arr.Clone();
        int n = copia.Length;
        if (n <= 1) return copia;
        
        int max = copia[0], min = copia[0];
        for (int i = 1; i < n; i++)
        {
            if (copia[i] > max) max = copia[i];
            if (copia[i] < min) min = copia[i];
        }
        
        int bucketCount = n;
        List<int>[] buckets = new List<int>[bucketCount];
        for (int i = 0; i < bucketCount; i++)
            buckets[i] = new List<int>();
        
        for (int i = 0; i < n; i++)
        {
            int bucketIndex = (int)((copia[i] - min) * (bucketCount - 1) / (max - min + 1));
            if (bucketIndex < 0) bucketIndex = 0;
            if (bucketIndex >= bucketCount) bucketIndex = bucketCount - 1;
            buckets[bucketIndex].Add(copia[i]);
        }
        
        // Ordenar cada cubeta con insertion sort
        for (int i = 0; i < bucketCount; i++)
        {
            buckets[i] = InsertionSortList(buckets[i]);
        }
        
        // Concatenar
        int index = 0;
        for (int i = 0; i < bucketCount; i++)
        {
            for (int j = 0; j < buckets[i].Count; j++)
            {
                copia[index++] = buckets[i][j];
            }
        }
        return copia;
    }
    
    static List<int> InsertionSortList(List<int> list)
    {
        List<int> result = new List<int>(list);
        int n = result.Count;
        for (int i = 1; i < n; i++)
        {
            int key = result[i];
            int j = i - 1;
            while (j >= 0 && result[j] > key)
            {
                result[j + 1] = result[j];
                j--;
            }
            result[j + 1] = key;
        }
        return result;
    }

    // QUICK SORT
    // Cómo funciona: Elige pivote (mediana de tres), divide en menores y mayores, ordena recursivamente.
    // Usa mediana de tres para evitar peor caso en arreglos ordenados/inversos.
    // Complejidad: Mejor O(n log n), Promedio O(n log n), Peor O(n^2) | Estable: No
    static int[] QuickSort(int[] arr)
    {
        int[] copia = (int[])arr.Clone();
        if (copia.Length <= 1) return copia;
        QuickSortRecursive(copia, 0, copia.Length - 1);
        return copia;
    }

    static void QuickSortRecursive(int[] arr, int left, int right)
    {
        if (left < right)
        {
            int pivotIndex = Partition(arr, left, right);
            QuickSortRecursive(arr, left, pivotIndex - 1);
            QuickSortRecursive(arr, pivotIndex + 1, right);
        }
    }

    static int Partition(int[] arr, int left, int right)
    {
        // Mediana de tres
        int mid = (left + right) / 2;
        if (arr[mid] < arr[left]) Swap(arr, left, mid);
        if (arr[right] < arr[left]) Swap(arr, left, right);
        if (arr[right] < arr[mid]) Swap(arr, mid, right);
        Swap(arr, mid, right - 1);
        
        int pivot = arr[right - 1];
        int i = left;
        for (int j = left; j <= right - 2; j++)
        {
            if (arr[j] <= pivot)
            {
                Swap(arr, i, j);
                i++;
            }
        }
        Swap(arr, i, right - 1);
        return i;
    }

    static void Swap(int[] arr, int i, int j)
    {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }

    // RADIX SORT
    // Cómo funciona: Ordena por dígitos de LSD a MSD, usando counting sort por cada dígito (base 10).
    // Para enteros no negativos.
    // Complejidad: Mejor O(d(n+k)), Promedio O(d(n+k)), Peor O(d(n+k)) | Estable: Sí
    static int[] RadixSort(int[] arr)
    {
        int[] copia = (int[])arr.Clone();
        int n = copia.Length;
        if (n <= 1) return copia;
        
        int max = copia[0];
        for (int i = 1; i < n; i++)
            if (copia[i] > max) max = copia[i];
        
        for (int exp = 1; max / exp > 0; exp *= 10)
        {
            CountingSortByDigit(copia, exp);
        }
        return copia;
    }

    static void CountingSortByDigit(int[] arr, int exp)
    {
        int n = arr.Length;
        int[] output = new int[n];
        int[] count = new int[10];
        
        for (int i = 0; i < n; i++)
            count[(arr[i] / exp) % 10]++;
        
        for (int i = 1; i < 10; i++)
            count[i] += count[i - 1];
        
        for (int i = n - 1; i >= 0; i--)
        {
            output[count[(arr[i] / exp) % 10] - 1] = arr[i];
            count[(arr[i] / exp) % 10]--;
        }
        
        for (int i = 0; i < n; i++)
            arr[i] = output[i];
    }

    // HEAP SORT
    // Cómo funciona: Construye un max-heap sobre el arreglo, extrae el máximo repetidamente al final.
    // Trabaja sobre el mismo arreglo.
    // Complejidad: Mejor O(n log n), Promedio O(n log n), Peor O(n log n) | Estable: No
    static int[] HeapSort(int[] arr)
    {
        int[] copia = (int[])arr.Clone();
        int n = copia.Length;
        if (n <= 1) return copia;
        
        // Construir max-heap
        for (int i = n / 2 - 1; i >= 0; i--)
            Heapify(copia, n, i);
        
        // Extraer elementos
        for (int i = n - 1; i > 0; i--)
        {
            Swap(copia, 0, i);
            Heapify(copia, i, 0);
        }
        return copia;
    }

    static void Heapify(int[] arr, int n, int i)
    {
        int largest = i;
        int left = 2 * i + 1;
        int right = 2 * i + 2;
        
        if (left < n && arr[left] > arr[largest])
            largest = left;
        if (right < n && arr[right] > arr[largest])
            largest = right;
        
        if (largest != i)
        {
            Swap(arr, i, largest);
            Heapify(arr, n, largest);
        }
    }

    static void ImprimirArray(string nombre, int[] arr)
    {
        Console.Write(nombre + ": [");
        for (int i = 0; i < arr.Length; i++)
        {
            Console.Write(arr[i]);
            if (i < arr.Length - 1) Console.Write(", ");
        }
        Console.WriteLine("]");
    }

    static bool EstaOrdenado(int[] arr)
    {
        for (int i = 1; i < arr.Length; i++)
        {
            if (arr[i] < arr[i - 1]) return false;
        }
        return true;
    }

    static int[] GenerarAleatorio(int tamano, int semilla)
    {
        Random rnd = new Random(semilla);
        int[] arr = new int[tamano];
        for (int i = 0; i < tamano; i++)
            arr[i] = rnd.Next(0, 100);
        return arr;
    }

    static void ProbarAlgoritmo(string nombre, int[] original, Func<int[], int[]> algoritmo)
    {
        Console.WriteLine($"\n=== {nombre} ===");
        ImprimirArray("Antes", original);
        int[] resultado = algoritmo(original);
        ImprimirArray("Después", resultado);
        Console.WriteLine(EstaOrdenado(resultado) ? "OK" : "ERROR");
    }

    static void Main()
    {
        Console.WriteLine("========================================");
        Console.WriteLine("   ALGORITMOS DE ORDENAMIENTO - C#");
        Console.WriteLine("========================================");
        
        int[] ejemplo = { 64, 34, 25, 12, 22, 11, 90, 5 };
        
        Console.WriteLine("\n--- PRUEBA 1: Arreglo de ejemplo fijo ---");
        ProbarAlgoritmo("Bubble Sort", ejemplo, BubbleSort);
        ProbarAlgoritmo("Selection Sort", ejemplo, SelectionSort);
        ProbarAlgoritmo("Insertion Sort", ejemplo, InsertionSort);
        ProbarAlgoritmo("Merge Sort", ejemplo, MergeSort);
        ProbarAlgoritmo("Shell Sort", ejemplo, ShellSort);
        ProbarAlgoritmo("Bucket Sort", ejemplo, BucketSort);
        ProbarAlgoritmo("Quick Sort", ejemplo, QuickSort);
        ProbarAlgoritmo("Radix Sort", ejemplo, RadixSort);
        ProbarAlgoritmo("Heap Sort", ejemplo, HeapSort);
        
        Console.WriteLine("\n\n--- PRUEBA 2: Arreglo aleatorio (20 elementos, semilla fija) ---");
        int[] aleatorio = GenerarAleatorio(20, 12345);
        ProbarAlgoritmo("Bubble Sort", aleatorio, BubbleSort);
        ProbarAlgoritmo("Selection Sort", aleatorio, SelectionSort);
        ProbarAlgoritmo("Insertion Sort", aleatorio, InsertionSort);
        ProbarAlgoritmo("Merge Sort", aleatorio, MergeSort);
        ProbarAlgoritmo("Shell Sort", aleatorio, ShellSort);
        ProbarAlgoritmo("Bucket Sort", aleatorio, BucketSort);
        ProbarAlgoritmo("Quick Sort", aleatorio, QuickSort);
        ProbarAlgoritmo("Radix Sort", aleatorio, RadixSort);
        ProbarAlgoritmo("Heap Sort", aleatorio, HeapSort);
        
        Console.WriteLine("\n\n--- PRUEBA 3: Arreglo ya ordenado ---");
        int[] ordenado = { 1, 2, 3, 4, 5, 6, 7, 8 };
        ProbarAlgoritmo("Bubble Sort", ordenado, BubbleSort);
        ProbarAlgoritmo("Selection Sort", ordenado, SelectionSort);
        ProbarAlgoritmo("Insertion Sort", ordenado, InsertionSort);
        ProbarAlgoritmo("Merge Sort", ordenado, MergeSort);
        ProbarAlgoritmo("Shell Sort", ordenado, ShellSort);
        ProbarAlgoritmo("Bucket Sort", ordenado, BucketSort);
        ProbarAlgoritmo("Quick Sort", ordenado, QuickSort);
        ProbarAlgoritmo("Radix Sort", ordenado, RadixSort);
        ProbarAlgoritmo("Heap Sort", ordenado, HeapSort);
        
        Console.WriteLine("\n\n--- PRUEBA 4: Arreglo inverso ---");
        int[] inverso = { 8, 7, 6, 5, 4, 3, 2, 1 };
        ProbarAlgoritmo("Bubble Sort", inverso, BubbleSort);
        ProbarAlgoritmo("Selection Sort", inverso, SelectionSort);
        ProbarAlgoritmo("Insertion Sort", inverso, InsertionSort);
        ProbarAlgoritmo("Merge Sort", inverso, MergeSort);
        ProbarAlgoritmo("Shell Sort", inverso, ShellSort);
        ProbarAlgoritmo("Bucket Sort", inverso, BucketSort);
        ProbarAlgoritmo("Quick Sort", inverso, QuickSort);
        ProbarAlgoritmo("Radix Sort", inverso, RadixSort);
        ProbarAlgoritmo("Heap Sort", inverso, HeapSort);
        
        Console.WriteLine("\n\n--- PRUEBA 5: Casos borde ---");
        int[] vacio = { };
        Console.WriteLine("\n=== Arreglo vacío ===");
        ImprimirArray("Antes", vacio);
        Console.WriteLine("Bubble Sort - " + (EstaOrdenado(BubbleSort(vacio)) ? "OK" : "ERROR"));
        Console.WriteLine("Quick Sort - " + (EstaOrdenado(QuickSort(vacio)) ? "OK" : "ERROR"));
        Console.WriteLine("Merge Sort - " + (EstaOrdenado(MergeSort(vacio)) ? "OK" : "ERROR"));
        
        int[] unElemento = { 42 };
        Console.WriteLine("\n=== Un elemento ===");
        ImprimirArray("Antes", unElemento);
        Console.WriteLine("Bubble Sort - " + (EstaOrdenado(BubbleSort(unElemento)) ? "OK" : "ERROR"));
        Console.WriteLine("Heap Sort - " + (EstaOrdenado(HeapSort(unElemento)) ? "OK" : "ERROR"));
        
        int[] repetidos = { 5, 2, 8, 2, 9, 5, 1, 5 };
        Console.WriteLine("\n=== Elementos repetidos ===");
        ImprimirArray("Antes", repetidos);
        ProbarAlgoritmo("Bubble Sort", repetidos, BubbleSort);
        ProbarAlgoritmo("Quick Sort", repetidos, QuickSort);
        ProbarAlgoritmo("Merge Sort", repetidos, MergeSort);
        ProbarAlgoritmo("Radix Sort", repetidos, RadixSort);
    }
}
