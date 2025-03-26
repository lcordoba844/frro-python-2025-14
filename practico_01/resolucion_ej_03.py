#Ejercicio 3-1

from typing import Union

def operacion_basica(a: float, b: float, multiplicar: bool) -> Union[float, str]:
    return a*b if multiplicar == True else a/b if b != 0 else "Operación no válida"


# NO MODIFICAR - INICIO
assert operacion_basica(1, 1, True) == 1
assert operacion_basica(1, 1, False) == 1
assert operacion_basica(25, 5, True) == 125
assert operacion_basica(25, 5, False) == 5
assert operacion_basica(0, 5, True) == 0
assert operacion_basica(0, 5, False) == 0
assert operacion_basica(1, 0, True) == 0
assert operacion_basica(1, 0, False) == "Operación no válida"
# NO MODIFICAR - FIN

#Ejercicio 3-2
def operacion_multiple(a: float, b: float, multiplicar: bool) -> Union[float, str]:
    if multiplicar == True:
      return a*b
    elif multiplicar == False and b != 0:
      return a/b
    else:
      return "Operación no válida"

# NO MODIFICAR - INICIO
assert operacion_multiple(1, 1, True) == 1
assert operacion_multiple(1, 1, False) == 1
assert operacion_multiple(25, 5, True) == 125
assert operacion_multiple(25, 5, False) == 5
assert operacion_multiple(0, 5, True) == 0
assert operacion_multiple(0, 5, False) == 0
assert operacion_multiple(1, 0, True) == 0
assert operacion_multiple(1, 0, False) == "Operación no válida"
# NO MODIFICAR - FIN

