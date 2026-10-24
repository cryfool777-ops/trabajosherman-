// BUBBLE SORT
// Cómo funciona: Compara elementos adyacentes e intercambia si están en orden incorrecto.
// Repite hasta que no haya intercambios. Cada pasada coloca el mayor al final.
// Complejidad: Mejor O(n), Promedio O(n^2), Peor O(n^2) | Estable: Sí
function bubbleSort(arr) {
    let copia = arr.slice();
    let n = copia.length;
    for (let i = 0; i < n - 1; i++) {
        let intercambiado = false;
        for (let j = 0; j < n - i - 1; j++) {
            if (copia[j] > copia[j + 1]) {
                let temp = copia[j];
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
function selectionSort(arr) {
    let copia = arr.slice();
    let n = copia.length;
    for (let i = 0; i < n - 1; i++) {
        let minIndex = i;
        for (let j = i + 1; j < n; j++) {
            if (copia[j] < copia[minIndex]) {
                minIndex = j;
            }
        }
        if (minIndex !== i) {
            let temp = copia[i];
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
function insertionSort(arr) {
    let copia = arr.slice();
    let n = copia.length;
    for (let i = 1; i < n; i++) {
        let key = copia[i];
        let j = i - 1;
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
function mergeSort(arr) {
    let copia = arr.slice();
    if (copia.length <= 1) return copia;
    mergeSortRecursive(copia, 0, copia.length - 1);
    return copia;
}

function mergeSortRecursive(arr, left, right) {
    if (left < right) {
        let mid = Math.floor((left + right) / 2);
        mergeSortRecursive(arr, left, mid);
        mergeSortRecursive(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }
}

function merge(arr, left, mid, right) {
    let n1 = mid - left + 1;
    let n2 = right - mid;
    let L = [];
    let R = [];
    
    for (let i = 0; i < n1; i++) L[i] = arr[left + i];
    for (let j = 0; j < n2; j++) R[j] = arr[mid + 1 + j];
    
    let i = 0, j = 0, k = left;
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

// SHELL SORT
// Cómo funciona: Ordenamiento por inserción con saltos (gap). Usa secuencia n/2, n/4, ..., 1.
// Reduce el número de intercambios comparado con insertion sort simple.
// Complejidad: Mejor O(n log^2 n), Promedio O(n^(3/2)), Peor O(n^2) | Estable: No
function shellSort(arr) {
    let copia = arr.slice();
    let n = copia.length;
    for (let gap = Math.floor(n / 2); gap > 0; gap = Math.floor(gap / 2)) {
        for (let i = gap; i < n; i++) {
            let temp = copia[i];
            let j = i;
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
function insertionSortArray(arr) {
    let copia = arr.slice();
    let n = copia.length;
    for (let i = 1; i < n; i++) {
        let key = copia[i];
        let j = i - 1;
        while (j >= 0 && copia[j] > key) {
            copia[j + 1] = copia[j];
            j--;
        }
        copia[j + 1] = key;
    }
    return copia;
}

function bucketSort(arr) {
    let copia = arr.slice();
    let n = copia.length;
    if (n <= 1) return copia;
    
    let maxVal = copia[0], minVal = copia[0];
    for (let i = 1; i < n; i++) {
        if (copia[i] > maxVal) maxVal = copia[i];
        if (copia[i] < minVal) minVal = copia[i];
    }
    
    let bucketCount = n;
    let buckets = [];
    for (let i = 0; i < bucketCount; i++) {
        buckets[i] = [];
    }
    
    for (let i = 0; i < n; i++) {
        let bucketIndex;
        if (maxVal === minVal) {
            bucketIndex = 0;
        } else {
            bucketIndex = Math.floor((copia[i] - minVal) * (bucketCount - 1) / (maxVal - minVal + 1));
        }
        if (bucketIndex < 0) bucketIndex = 0;
        if (bucketIndex >= bucketCount) bucketIndex = bucketCount - 1;
        buckets[bucketIndex].push(copia[i]);
    }
    
    for (let i = 0; i < bucketCount; i++) {
        buckets[i] = insertionSortArray(buckets[i]);
    }
    
    let index = 0;
    for (let i = 0; i < bucketCount; i++) {
        for (let j = 0; j < buckets[i].length; j++) {
            copia[index++] = buckets[i][j];
        }
    }
    return copia;
}

// QUICK SORT
// Cómo funciona: Elige pivote (mediana de tres), divide en menores y mayores, ordena recursivamente.
// Usa mediana de tres para evitar peor caso en arreglos ordenados/inversos.
// Complejidad: Mejor O(n log n), Promedio O(n log n), Peor O(n^2) | Estable: No
function swap(arr, i, j) {
    let temp = arr[i];
    arr[i] = arr[j];
    arr[j] = temp;
}

function partition(arr, left, right) {
    let mid = Math.floor((left + right) / 2);
    // Mediana de tres
    if (arr[mid] < arr[left]) swap(arr, left, mid);
    if (arr[right] < arr[left]) swap(arr, left, right);
    if (arr[right] < arr[mid]) swap(arr, mid, right);
    swap(arr, mid, right - 1);
    
    let pivot = arr[right - 1];
    let i = left;
    for (let j = left; j <= right - 2; j++) {
        if (arr[j] <= pivot) {
            swap(arr, i, j);
            i++;
        }
    }
    swap(arr, i, right - 1);
    return i;
}

function quickSortRecursive(arr, left, right) {
    if (left < right) {
        let pivotIndex = partition(arr, left, right);
        quickSortRecursive(arr, left, pivotIndex - 1);
        quickSortRecursive(arr, pivotIndex + 1, right);
    }
}

function quickSort(arr) {
    let copia = arr.slice();
    if (copia.length <= 1) return copia;
    quickSortRecursive(copia, 0, copia.length - 1);
    return copia;
}

// RADIX SORT
// Cómo funciona: Ordena por dígitos de LSD a MSD, usando counting sort por cada dígito (base 10).
// Para enteros no negativos.
// Complejidad: Mejor O(d(n+k)), Promedio O(d(n+k)), Peor O(d(n+k)) | Estable: Sí
function countingSortByDigit(arr, exp) {
    let n = arr.length;
    let output = new Array(n).fill(0);
    let count = new Array(10).fill(0);
    
    for (let i = 0; i < n; i++) {
        let index = Math.floor(arr[i] / exp) % 10;
        count[index]++;
    }
    
    for (let i = 1; i < 10; i++) {
        count[i] += count[i - 1];
    }
    
    for (let i = n - 1; i >= 0; i--) {
        let index = Math.floor(arr[i] / exp) % 10;
        output[count[index] - 1] = arr[i];
        count[index]--;
    }
    
    for (let i = 0; i < n; i++) {
        arr[i] = output[i];
    }
}

function radixSort(arr) {
    let copia = arr.slice();
    let n = copia.length;
    if (n <= 1) return copia;
    
    let maxVal = copia[0];
    for (let i = 1; i < n; i++) {
        if (copia[i] > maxVal) maxVal = copia[i];
    }
    
    for (let exp = 1; Math.floor(maxVal / exp) > 0; exp *= 10) {
        countingSortByDigit(copia, exp);
    }
    return copia;
}

// HEAP SORT
// Cómo funciona: Construye un max-heap sobre el arreglo, extrae el máximo repetidamente al final.
// Trabaja sobre el mismo arreglo.
// Complejidad: Mejor O(n log n), Promedio O(n log n), Peor O(n log n) | Estable: No
function heapify(arr, n, i) {
    let largest = i;
    let left = 2 * i + 1;
    let right = 2 * i + 2;
    
    if (left < n && arr[left] > arr[largest]) {
        largest = left;
    }
    if (right < n && arr[right] > arr[largest]) {
        largest = right;
    }
    
    if (largest !== i) {
        swap(arr, i, largest);
        heapify(arr, n, largest);
    }
}

function heapSort(arr) {
    let copia = arr.slice();
    let n = copia.length;
    if (n <= 1) return copia;
    
    for (let i = Math.floor(n / 2) - 1; i >= 0; i--) {
        heapify(copia, n, i);
    }
    
    for (let i = n - 1; i > 0; i--) {
        swap(copia, 0, i);
        heapify(copia, i, 0);
    }
    return copia;
}

function imprimirArray(nombre, arr) {
    console.log(nombre + ": [" + arr.join(", ") + "]");
}

function estaOrdenado(arr) {
    for (let i = 1; i < arr.length; i++) {
        if (arr[i] < arr[i - 1]) return false;
    }
    return true;
}

function generarAleatorio(tamano, semilla) {
    let rnd = function(seed) {
        let m = 0x80000000;
        let a = 1103515245;
        let c = 12345;
        let state = seed ? seed : Math.floor(Math.random() * (m - 1));
        return function() {
            state = (a * state + c) % m;
            return state / (m - 1);
        };
    };
    let random = rnd(semilla);
    let arr = [];
    for (let i = 0; i < tamano; i++) {
        arr.push(Math.floor(random() * 100));
    }
    return arr;
}

function probarAlgoritmo(nombre, original, algoritmo) {
    console.log("\n=== " + nombre + " ===");
    imprimirArray("Antes", original);
    let resultado = algoritmo(original);
    imprimirArray("Después", resultado);
    if (estaOrdenado(resultado)) {
        console.log("OK");
    } else {
        console.log("ERROR");
    }
}

console.log("========================================");
console.log("   ALGORITMOS DE ORDENAMIENTO - Node.js");
console.log("========================================");

let ejemplo = [64, 34, 25, 12, 22, 11, 90, 5];

console.log("\n--- PRUEBA 1: Arreglo de ejemplo fijo ---");
probarAlgoritmo("Bubble Sort", ejemplo, bubbleSort);
probarAlgoritmo("Selection Sort", ejemplo, selectionSort);
probarAlgoritmo("Insertion Sort", ejemplo, insertionSort);
probarAlgoritmo("Merge Sort", ejemplo, mergeSort);
probarAlgoritmo("Shell Sort", ejemplo, shellSort);
probarAlgoritmo("Bucket Sort", ejemplo, bucketSort);
probarAlgoritmo("Quick Sort", ejemplo, quickSort);
probarAlgoritmo("Radix Sort", ejemplo, radixSort);
probarAlgoritmo("Heap Sort", ejemplo, heapSort);

console.log("\n\n--- PRUEBA 2: Arreglo aleatorio (20 elementos, semilla fija) ---");
let aleatorio = generarAleatorio(20, 12345);
probarAlgoritmo("Bubble Sort", aleatorio, bubbleSort);
probarAlgoritmo("Selection Sort", aleatorio, selectionSort);
probarAlgoritmo("Insertion Sort", aleatorio, insertionSort);
probarAlgoritmo("Merge Sort", aleatorio, mergeSort);
probarAlgoritmo("Shell Sort", aleatorio, shellSort);
probarAlgoritmo("Bucket Sort", aleatorio, bucketSort);
probarAlgoritmo("Quick Sort", aleatorio, quickSort);
probarAlgoritmo("Radix Sort", aleatorio, radixSort);
probarAlgoritmo("Heap Sort", aleatorio, heapSort);

console.log("\n\n--- PRUEBA 3: Arreglo ya ordenado ---");
let ordenado = [1, 2, 3, 4, 5, 6, 7, 8];
probarAlgoritmo("Bubble Sort", ordenado, bubbleSort);
probarAlgoritmo("Selection Sort", ordenado, selectionSort);
probarAlgoritmo("Insertion Sort", ordenado, insertionSort);
probarAlgoritmo("Merge Sort", ordenado, mergeSort);
probarAlgoritmo("Shell Sort", ordenado, shellSort);
probarAlgoritmo("Bucket Sort", ordenado, bucketSort);
probarAlgoritmo("Quick Sort", ordenado, quickSort);
probarAlgoritmo("Radix Sort", ordenado, radixSort);
probarAlgoritmo("Heap Sort", ordenado, heapSort);

console.log("\n\n--- PRUEBA 4: Arreglo inverso ---");
let inverso = [8, 7, 6, 5, 4, 3, 2, 1];
probarAlgoritmo("Bubble Sort", inverso, bubbleSort);
probarAlgoritmo("Selection Sort", inverso, selectionSort);
probarAlgoritmo("Insertion Sort", inverso, insertionSort);
probarAlgoritmo("Merge Sort", inverso, mergeSort);
probarAlgoritmo("Shell Sort", inverso, shellSort);
probarAlgoritmo("Bucket Sort", inverso, bucketSort);
probarAlgoritmo("Quick Sort", inverso, quickSort);
probarAlgoritmo("Radix Sort", inverso, radixSort);
probarAlgoritmo("Heap Sort", inverso, heapSort);

console.log("\n\n--- PRUEBA 5: Casos borde ---");
let vacio = [];
console.log("\n=== Arreglo vacío ===");
imprimirArray("Antes", vacio);
console.log("Bubble Sort - " + (estaOrdenado(bubbleSort(vacio)) ? "OK" : "ERROR"));
console.log("Quick Sort - " + (estaOrdenado(quickSort(vacio)) ? "OK" : "ERROR"));
console.log("Merge Sort - " + (estaOrdenado(mergeSort(vacio)) ? "OK" : "ERROR"));

let unElemento = [42];
console.log("\n=== Un elemento ===");
imprimirArray("Antes", unElemento);
console.log("Bubble Sort - " + (estaOrdenado(bubbleSort(unElemento)) ? "OK" : "ERROR"));
console.log("Heap Sort - " + (estaOrdenado(heapSort(unElemento)) ? "OK" : "ERROR"));

let repetidos = [5, 2, 8, 2, 9, 5, 1, 5];
console.log("\n=== Elementos repetidos ===");
imprimirArray("Antes", repetidos);
probarAlgoritmo("Bubble Sort", repetidos, bubbleSort);
probarAlgoritmo("Quick Sort", repetidos, quickSort);
probarAlgoritmo("Merge Sort", repetidos, mergeSort);
probarAlgoritmo("Radix Sort", repetidos, radixSort);
