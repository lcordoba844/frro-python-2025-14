def maximo_encadenado(a: float, b: float, c: float) -> float:
    if a < b < c: return c
    if a < b > c: return b
    if b < a > c: return a
    

assert maximo_encadenado(1, 10, 5) == 10
assert maximo_encadenado(4, 9, 18) == 18
assert maximo_encadenado(24, 9, 18) == 24


###############################################################################


def maximo_cuadruple(a: float, b: float, c: float, d: float) -> float:
    return max(a, b, c, d)

assert maximo_cuadruple(1, 10, 5, -5) == 10
assert maximo_cuadruple(4, 9, 18, 6) == 18
assert maximo_cuadruple(24, 9, 18, 20) == 24
assert maximo_cuadruple(24, 9, 18, 30) == 30


###############################################################################


def maximo_arbitrario(*args) -> float:
    return max(args)

# NO MODIFICAR - INICIO
assert maximo_arbitrario(1, 10, 5, -5) == 10
assert maximo_arbitrario(4, 9, 18, 6) == 18
assert maximo_arbitrario(24, 9, 18, 20) == 24
assert maximo_arbitrario(24, 9, 18, 30) == 30
# NO MODIFICAR - FIN


###############################################################################


def maximo_recursivo(*args) -> float:
    # Base case: if there's only one argument, return it
    if len(args) == 1:
        return args[0]
    # Recursive case: compare the first argument with the max of the rest
    first = args[0]
    rest_max = maximo_recursivo(*args[1:])  # Recurse with remaining args
    return first if first > rest_max else rest_max
    


# NO MODIFICAR - INICIO
assert maximo_recursivo(1, 10, 5, -5) == 10
assert maximo_recursivo(4, 9, 18, 6) == 18
assert maximo_recursivo(24, 9, 18, 20) == 24
assert maximo_recursivo(24, 9, 18, 30) == 30
# NO MODIFICAR - FIN