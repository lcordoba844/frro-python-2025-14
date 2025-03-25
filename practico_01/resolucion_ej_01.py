"""Ejercicio1"""
def maximo_basico(x: float, y: float) -> float:
    if x >= y:
        return x
    else:
        return y

assert maximo_basico(10, 5) == 10
assert maximo_basico(9, 18) == 18

def maximo_libreria(a: float, b:float) -> float:
  return max(a, b)
  
assert maximo_libreria(10, 5) == 10
assert maximo_libreria(9, 18) == 18

def maximo_ternario(a:float, b:float) -> float:
  return a if a >= b else b
  
assert maximo_ternario(10,5) == 10
assert maximo_ternario(9, 18) == 18


""" https://colab.research.google.com/drive/1GiI3Q-QAm6-rvqEOQ2CcukxkPIDa6nPi#scrollTo=HBKhbossZZRo """