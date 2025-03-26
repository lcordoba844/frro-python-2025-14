# Ejercicio 6-1

from typing import List, Union


def numeros_al_final_basico(lista: List[Union[float, str]]) -> List[Union[float, str]]:
    for e in lista[:]:
        if isinstance(e, (int, float)):
            lista.remove(e)
            lista.append(e)
    return lista
    

# NO MODIFICAR - INICIO
assert numeros_al_final_basico([3, "a", 1, "b", 10, "j"]) == ["a", "b", "j", 3, 1, 10]
# NO MODIFICAR - FIN





#Ejercicio 6-2

def numeros_al_final_comprension(lista: List[Union[float, str]]) -> List[Union[float, str]]:

    numeros = [x for x in lista if isinstance(x, (int, float))]
    letras = [x for x in lista if not isinstance(x, (int, float))]
    return letras + numeros

# NO MODIFICAR - INICIO
assert numeros_al_final_comprension([3, "a", 1, "b", 10, "j"]) == ["a", "b", "j", 3, 1, 10]
# NO MODIFICAR - FIN





# Ejercicio 6-3

def numeros_al_final_sorted(lista: List[Union[float, str]]) -> List[Union[float, str]]:
    return sorted(lista, key=lambda x:isinstance(x, (int, float)))
    

# NO MODIFICAR - INICIO
assert numeros_al_final_sorted([3, "a", 1, "b", 10, "j"]) == ["a", "b", "j", 3, 1, 10]
# NO MODIFICAR - FIN
