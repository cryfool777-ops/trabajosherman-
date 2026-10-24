import bisect

mi_lista = [10, 20, 30, 40, 50, 60, 70, 80, 90]
objetivo = 70

# Encuentra el índice correspondiente usando búsqueda binaria
indice = bisect.bisect_left(mi_lista, objetivo)

# Verificamos si el elemento realmente está en esa posición
if indice < len(mi_lista) and mi_lista[indice] == objetivo:
    print(f"Encontrado en el índice: {indice}")
else:
    print("No encontrado.")

