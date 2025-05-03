"""Base de Datos SQL - Baja"""

import datetime
import sqlite3
from practico_04.ejercicio_01 import reset_tabla
from practico_04.ejercicio_02 import agregar_persona


def borrar_persona(id_persona):
    """Implementar la funcion borrar_persona, que elimina un registro en la 
    tabla Persona. Devuelve un booleano en base a si encontro el registro y lo 
    borro o no."""
    pass # Completar
    conn = sqlite3.connect("mi_base.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Persona WHERE IdPersona = ?", (id_persona,))
    persona = cursor.fetchone()

    if persona:
        cursor.execute("DELETE FROM Persona WHERE IdPersona = ?", (id_persona,))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False


# NO MODIFICAR - INICIO
@reset_tabla
def pruebas():
    assert borrar_persona(agregar_persona('juan perez', datetime.datetime(1988, 5, 15), 32165498, 180))
    assert borrar_persona(12345) is False

if __name__ == '__main__':
    pruebas()
# NO MODIFICAR - FIN
