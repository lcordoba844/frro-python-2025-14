"""Base de Datos SQL - Crear y Borrar Tablas"""

import sqlite3
import datetime

def crear_tabla():
    """Implementar la funcion crear_tabla, que cree una tabla Persona con:
        - IdPersona: Int() (autoincremental)
        - Nombre: Char(30)
        - FechaNacimiento: Date()
        - DNI: Int()
        - Altura: Int()
    """
    pass # Completar
    conexion = sqlite3.connect("mi_base.db")
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Persona (
            IdPersona INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT(30),
            FechaNacimiento TEXT(30),
            DNI INTEGER,
            Altura INTEGER
        )
    ''')
    conexion.commit()
    conexion.close()





def borrar_tabla():
    """Implementar la funcion borrar_tabla, que borra la tabla creada 
    anteriormente."""
    pass # Completar
    conexion = sqlite3.connect("mi_base.db")
    cursor = conexion.cursor()
    cursor.execute('DROP TABLE IF EXISTS Persona')
    conexion.commit()
    conexion.close()



# NO MODIFICAR - INICIO
def reset_tabla(func):
    def func_wrapper():
        crear_tabla()
        func()
        borrar_tabla()
    return func_wrapper
# NO MODIFICAR - FIN
