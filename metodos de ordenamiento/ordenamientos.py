# BUBBLE SORT
# Cómo funciona: Compara elementos adyacentes e intercambia si están en orden incorrecto.
# Repite hasta que no haya intercambios. Cada pasada coloca el mayor al final.
# Complejidad: Mejor O(n), Promedio O(n^2), Peor O(n^2) | Estable: Sí
def bubble_sort(arr):
    copia = list(arr)
    n = len(copia)
    for i in range(n - 1):
        intercambiado = False
        for j in range(n - i - 1):
            if copia[j] > copia[j + 1]:
                copia[j], copia[j + 1] = copia[j + 1], copia[j]
                intercambiado = True
        if not intercambiado:
            break
    return copia

# SELECTION SORT
# Cómo funciona: Busca el elemento mínimo en la parte no ordenada y lo coloca al inicio.
# Repite para cada posición. No depende de intercambios adyacentes.
# Complejidad: Mejor O(n^2), Promedio O(n^2), Peor O(n^2) | Estable: No
def selection_sort(arr):
    copia = list(arr)
    n = len(copia)
    for i in range(n - 1):
        min_index = i
        for j in range(i + 1, n):
            if copia[j] < copia[min_index]:
                min_index = j
        if min_index != i:
            copia[i], copia[min_index] = copia[min_index], copia[i]
    return copia

# INSERTION SORT
# Cómo funciona: Toma cada elemento y lo inserta en la posición correcta en la parte ya ordenada.
# Eficiente para arreglos pequeños o parcialmente ordenados.
# Complejidad: Mejor O(n), Promedio O(n^2), Peor O(n^2) | Estable: Sí
def insertion_sort(arr):
    copia = list(arr)
    n = len(copia)
    for i in range(1, n):
        key = copia[i]
        j = i - 1
        while j >= 0 and copia[j] > key:
            copia[j + 1] = copia[j]
            j -= 1
        copia[j + 1] = key
    return copia

# MERGE SORT
# Cómo funciona: Divide recursivamente el arreglo en mitades hasta elementos individuales.
# Luego fusiona las mitades ordenadas usando un arreglo auxiliar.
# Complejidad: Mejor O(n log n), Promedio O(n log n), Peor O(n log n) | Estable: Sí
def merge_sort(arr):
    copia = list(arr)
    if len(copia) <= 1:
        return copia
    merge_sort_recursive(copia, 0, len(copia) - 1)
    return copia

def merge_sort_recursive(arr, left, right):
    if left < right:
        mid = (left + right) // 2
        merge_sort_recursive(arr, left, mid)
        merge_sort_recursive(arr, mid + 1, right)
        merge(arr, left, mid, right)

def merge(arr, left, mid, right):
    n1 = mid - left + 1
    n2 = right - mid
    L = arr[left:mid + 1]
    R = arr[mid + 1:right + 1]
    
    i = 0  # L
    j = 0  # R
    k = left  # arr
    while i < len(L) and j < len(R):
        if L[i] <= R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1
    while i < len(L):
        arr[k] = L[i]
        i += 1
        k += 1
    while j < len(R):
        arr[k] = R[j]
        j += 1
        k += 1

# SHELL SORT
# Cómo funciona: Ordenamiento por inserción con saltos (gap). Usa secuencia n/2, n/4, ..., 1.
# Reduce el número de intercambios comparado con insertion sort simple.
# Complejidad: Mejor O(n log^2 n), Promedio O(n^(3/2)), Peor O(n^2) | Estable: No
def shell_sort(arr):
    copia = list(arr)
    n = len(copia)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = copia[i]
            j = i
            while j >= gap and copia[j - gap] > temp:
                copia[j] = copia[j - gap]
                j -= gap
            copia[j] = temp
        gap //= 2
    return copia

# BUCKET SORT
# Cómo funciona: Distribuye elementos en cubetas según rango, ordena cada cubeta con insertion sort.
# Para enteros no negativos. Eficiente cuando valores están distribuidos uniformemente.
# Complejidad: Mejor O(n+k), Promedio O(n+k), Peor O(n^2) | Estable: Sí
def bucket_sort(arr):
    copia = list(arr)
    n = len(copia)
    if n <= 1:
        return copia
    
    max_val = max(copia)
    min_val = min(copia)
    
    bucket_count = n
    buckets = [[] for _ in range(bucket_count)]
    
    for i in range(n):
        if max_val == min_val:
            bucket_index = 0
        else:
            bucket_index = int((copia[i] - min_val) * (bucket_count - 1) / (max_val - min_val + 1))
        if bucket_index < 0:
            bucket_index = 0
        if bucket_index >= bucket_count:
            bucket_index = bucket_count - 1
        buckets[bucket_index].append(copia[i])
    
    # Ordenar cada cubeta con insertion sort
    for i in range(bucket_count):
        buckets[i] = insertion_sort_list(buckets[i])
    
    # Concatenar
    index = 0
    for i in range(bucket_count):
        for j in range(len(buckets[i])):
            copia[index] = buckets[i][j]
            index += 1
    return copia

def insertion_sort_list(lst):
    result = list(lst)
    n = len(result)
    for i in range(1, n):
        key = result[i]
        j = i - 1
        while j >= 0 and result[j] > key:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = key
    return result

# QUICK SORT
# Cómo funciona: Elige pivote (mediana de tres), divide en menores y mayores, ordena recursivamente.
# Usa mediana de tres para evitar peor caso en arreglos ordenados/inversos.
# Complejidad: Mejor O(n log n), Promedio O(n log n), Peor O(n^2) | Estable: No
def quick_sort(arr):
    copia = list(arr)
    if len(copia) <= 1:
        return copia
    quick_sort_recursive(copia, 0, len(copia) - 1)
    return copia

def quick_sort_recursive(arr, left, right):
    if left < right:
        pivot_index = partition(arr, left, right)
        quick_sort_recursive(arr, left, pivot_index - 1)
        quick_sort_recursive(arr, pivot_index + 1, right)

def partition(arr, left, right):
    mid = (left + right) // 2
    # Mediana de tres
    if arr[mid] < arr[left]:
        arr[left], arr[mid] = arr[mid], arr[left]
    if arr[right] < arr[left]:
        arr[left], arr[right] = arr[right], arr[left]
    if arr[right] < arr[mid]:
        arr[mid], arr[right] = arr[right], arr[mid]
    # Poner pivote al final-1
    arr[mid], arr[right - 1] = arr[right - 1], arr[mid]
    
    pivot = arr[right - 1]
    i = left
    for j in range(left, right - 1):
        if arr[j] <= pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[right - 1] = arr[right - 1], arr[i]
    return i

# RADIX SORT
# Cómo funciona: Ordena por dígitos de LSD a MSD, usando counting sort por cada dígito (base 10).
# Para enteros no negativos.
# Complejidad: Mejor O(d(n+k)), Promedio O(d(n+k)), Peor O(d(n+k)) | Estable: Sí
def radix_sort(arr):
    copia = list(arr)
    n = len(copia)
    if n <= 1:
        return copia
    
    max_val = max(copia)
    exp = 1
    while max_val // exp > 0:
        counting_sort_by_digit(copia, exp)
        exp *= 10
    return copia

def counting_sort_by_digit(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    
    for i in range(n):
        index = (arr[i] // exp) % 10
        count[index] += 1
    
    for i in range(1, 10):
        count[i] += count[i - 1]
    
    for i in range(n - 1, -1, -1):
        index = (arr[i] // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1
    
    for i in range(n):
        arr[i] = output[i]

# HEAP SORT
# Cómo funciona: Construye un max-heap sobre el arreglo, extrae el máximo repetidamente al final.
# Trabaja sobre el mismo arreglo.
# Complejidad: Mejor O(n log n), Promedio O(n log n), Peor O(n log n) | Estable: No
def heap_sort(arr):
    copia = list(arr)
    n = len(copia)
    if n <= 1:
        return copia
    
    # Construir max-heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(copia, n, i)
    
    # Extraer elementos
    for i in range(n - 1, 0, -1):
        copia[0], copia[i] = copia[i], copia[0]
        heapify(copia, i, 0)
    return copia

def heapify(arr, n, i):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2
    
    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right
    
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)

def imprimir_array(nombre, arr):
    print(f"{nombre}: [{', '.join(map(str, arr))}]")

def esta_ordenado(arr):
    for i in range(1, len(arr)):
        if arr[i] < arr[i - 1]:
            return False
    return True

def generar_aleatorio(tamano, semilla):
    import random
    rnd = random.Random(semilla)
    return [rnd.randint(0, 100) for _ in range(tamano)]

def probar_algoritmo(nombre, original, algoritmo):
    print(f"\n=== {nombre} ===")
    imprimir_array("Antes", original)
    resultado = algoritmo(original)
    imprimir_array("Después", resultado)
    if esta_ordenado(resultado):
        print("OK")
    else:
        print("ERROR")

if __name__ == "__main__":
    print("========================================")
    print("   ALGORITMOS DE ORDENAMIENTO - Python")
    print("========================================")
    
    ejemplo = [64, 34, 25, 12, 22, 11, 90, 5]
    
    print("\n--- PRUEBA 1: Arreglo de ejemplo fijo ---")
    probar_algoritmo("Bubble Sort", ejemplo, bubble_sort)
    probar_algoritmo("Selection Sort", ejemplo, selection_sort)
    probar_algoritmo("Insertion Sort", ejemplo, insertion_sort)
    probar_algoritmo("Merge Sort", ejemplo, merge_sort)
    probar_algoritmo("Shell Sort", ejemplo, shell_sort)
    probar_algoritmo("Bucket Sort", ejemplo, bucket_sort)
    probar_algoritmo("Quick Sort", ejemplo, quick_sort)
    probar_algoritmo("Radix Sort", ejemplo, radix_sort)
    probar_algoritmo("Heap Sort", ejemplo, heap_sort)
    
    print("\n\n--- PRUEBA 2: Arreglo aleatorio (20 elementos, semilla fija) ---")
    aleatorio = generar_aleatorio(20, 12345)
    probar_algoritmo("Bubble Sort", aleatorio, bubble_sort)
    probar_algoritmo("Selection Sort", aleatorio, selection_sort)
    probar_algoritmo("Insertion Sort", aleatorio, insertion_sort)
    probar_algoritmo("Merge Sort", aleatorio, merge_sort)
    probar_algoritmo("Shell Sort", aleatorio, shell_sort)
    probar_algoritmo("Bucket Sort", aleatorio, bucket_sort)
    probar_algoritmo("Quick Sort", aleatorio, quick_sort)
    probar_algoritmo("Radix Sort", aleatorio, radix_sort)
    probar_algoritmo("Heap Sort", aleatorio, heap_sort)
    
    print("\n\n--- PRUEBA 3: Arreglo ya ordenado ---")
    ordenado = [1, 2, 3, 4, 5, 6, 7, 8]
    probar_algoritmo("Bubble Sort", ordenado, bubble_sort)
    probar_algoritmo("Selection Sort", ordenado, selection_sort)
    probar_algoritmo("Insertion Sort", ordenado, insertion_sort)
    probar_algoritmo("Merge Sort", ordenado, merge_sort)
    probar_algoritmo("Shell Sort", ordenado, shell_sort)
    probar_algoritmo("Bucket Sort", ordenado, bucket_sort)
    probar_algoritmo("Quick Sort", ordenado, quick_sort)
    probar_algoritmo("Radix Sort", ordenado, radix_sort)
    probar_algoritmo("Heap Sort", ordenado, heap_sort)
    
    print("\n\n--- PRUEBA 4: Arreglo inverso ---")
    inverso = [8, 7, 6, 5, 4, 3, 2, 1]
    probar_algoritmo("Bubble Sort", inverso, bubble_sort)
    probar_algoritmo("Selection Sort", inverso, selection_sort)
    probar_algoritmo("Insertion Sort", inverso, insertion_sort)
    probar_algoritmo("Merge Sort", inverso, merge_sort)
    probar_algoritmo("Shell Sort", inverso, shell_sort)
    probar_algoritmo("Bucket Sort", inverso, bucket_sort)
    probar_algoritmo("Quick Sort", inverso, quick_sort)
    probar_algoritmo("Radix Sort", inverso, radix_sort)
    probar_algoritmo("Heap Sort", inverso, heap_sort)
    
    print("\n\n--- PRUEBA 5: Casos borde ---")
    vacio = []
    print("\n=== Arreglo vacío ===")
    imprimir_array("Antes", vacio)
    print("Bubble Sort - " + ("OK" if esta_ordenado(bubble_sort(vacio)) else "ERROR"))
    print("Quick Sort - " + ("OK" if esta_ordenado(quick_sort(vacio)) else "ERROR"))
    print("Merge Sort - " + ("OK" if esta_ordenado(merge_sort(vacio)) else "ERROR"))
    
    un_elemento = [42]
    print("\n=== Un elemento ===")
    imprimir_array("Antes", un_elemento)
    print("Bubble Sort - " + ("OK" if esta_ordenado(bubble_sort(un_elemento)) else "ERROR"))
    print("Heap Sort - " + ("OK" if esta_ordenado(heap_sort(un_elemento)) else "ERROR"))
    
    repetidos = [5, 2, 8, 2, 9, 5, 1, 5]
    print("\n=== Elementos repetidos ===")
    imprimir_array("Antes", repetidos)
    probar_algoritmo("Bubble Sort", repetidos, bubble_sort)
    probar_algoritmo("Quick Sort", repetidos, quick_sort)
    probar_algoritmo("Merge Sort", repetidos, merge_sort)
    probar_algoritmo("Radix Sort", repetidos, radix_sort)
