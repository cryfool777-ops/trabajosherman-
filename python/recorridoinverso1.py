#recorrido inverso se uso el slicing para invertir la lista que es la parte [::-1] entonces despues se hace un
# for para recorrer la lista invertida y se imprime cada elemento de la lista invertida pero tambien se cambia en vez de poner como 
#ahorita el nombre de la lista invertida se pone el mismo nombre de la lista invertida en el for para que se pueda recorrer y se imprima 
# cada elemento de la lista invertida El inicio y el final vacíos (:) significan "utiliza toda la lista".
# El paso -1 recorre la lista en orden inverso.
vencidas = [1, 8, 9, 10]
vencidas.insert(0, 2)


for vencidas in vencidas:
 print(vencidas)

