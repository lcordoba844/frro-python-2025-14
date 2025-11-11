# SignLearn: Juego Interactivo para Aprender Lengua de Señas

## Descripción del Proyecto

**SignLearn** es un juego educativo interactivo diseñado para que los niños aprendan y practiquen el lenguaje de señas de manera divertida y dinámica.
A través de la cámara, el sistema muestra en pantalla una letra o seña que el niño debe imitar con sus manos. Utilizando **visión por computadora (OpenCV)** y **MediaPipe**, el juego evalua gestos manuales en tiempo real y proporciona los resultados reconocidos junto con los puntos de referencia de las manos detectadas.

Cada intento se registra en la base de datos, permitiendo analizar el progreso individual, ofrecer retroalimentación automática y mantener un historial de desempeño.
El sistema incorpora elementos de **gamificación**, como puntos, niveles y logros, para incentivar el aprendizaje y la práctica constante.

El objetivo principal de *SignLearn* es fomentar el aprendizaje visual y corporal del lenguaje de señas, reforzando la memoria y la motricidad fina a través del juego.

---

## Modelo de Dominio

**Entidades Principales:**

1. **Usuario**

   * Representa al jugador sin necesidad de registrarse.
   * Guarda unicamente su nombre.
   * Se relaciona con las partidas o sesiones de juego que ha realizado.

2. **SesionJuego**

   * Registra cada sesión o ronda de práctica del usuario.
   * Contiene información sobre:

     * Fecha y hora de la sesión.
     * Puntaje total obtenido.
     * Resultado (en valor numérico entero).
   * Cada sesión pertenece a un único usuario.

---

## Reglas de Negocio

1. **RN01| – Registro de puntajes válidos**
* Solo se podrán registrar puntajes cuando el jugador haya completado una partida.
* Cada registro debe incluir: nombre del jugador, puntaje obtenido y fecha y hora exacta de finalización.
* Los nombres se limitan a 30 caracteres y no pueden quedar vacíos.

1. **RN02 – Orden y visualización del ranking**
* El sistema debe mostrar los puntajes en orden descendente por puntaje y, en caso de empate, por fecha ascendente
* El usuario puede elegir la cantidad de resultados visibles (Top 10, 20 o 50) y filtrar por nombre.

3. **RN03 – Integridad del juego en ejecución**
* Solo puede haber una instancia activa del juego en un mismo dispositivo al mismo tiempo.
* Si el juego ya está en ejecución, el botón “Jugar” no debe lanzar una nueva partida hasta que la actual finalice o se detenga.
---

## Casos de Uso

| **CU**   | **Nombre del Caso de Uso**        | **Descripción**                                                                                                                    |
| :------- | :-------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| **CU01** | Inicio de Sesión                  | Permite que el usuario acceda al juego sin necesidad de registro.   |                                              

| **CU02** | Iniciar Juego / Sesión            | El usuario inicia una nueva sesión de práctica. Se activa la cámara para el reconocimiento.    |            

| **CU03** | Detección y Evaluación de Señales | El sistema utiliza OpenCV y realiza calculo de distancias entre los puntos de la mano. |

| **CU04** | Cálculo de Puntuación y Nivel     | El sistema calcula los puntos obtenidos segun la cantidad de letras seguidas que va acertando el usuario y esto aumenta el bonus por acertar la siguiente  |
        
| **CU05** | Almacenamiento de Resultados      | Al finalizar la sesión, se guarda el nombre, el puntaje y la fecha de finalización en la base de datos.                               |
| **CU06** | Visualización de Progreso         | El usuario puede consultar un resumen de sus sesiones pasadas.                           |

---

## Bosquejo de Arquitectura

El sistema se desarrollará con una **arquitectura en 3 capas**:

1. **Capa de Presentación**

   * Implementada con **Flask**.
   * Gestiona la interacción del usuario y los resultados.
   * Controla la cámara y los elementos de gamificación.

2. **Capa de Negocio**

   * Implementada en **Python**.
   * Contiene la lógica del juego: cálculo de distancias, puntuación y detección de errores.
   * Utiliza **OpenCV**.

3. **Capa de Datos**

   * Base de datos **SQLite** (simple y portable).
   * ORM: **SQLAlchemy** para mapear clases Python a tablas.
   * Se almacenan usuarios, puntajes y fechas.

---

## Stack Tecnológico

| Componente                         | Tecnología           | Descripción                                                          |
| ---------------------------------- | -------------------- | -------------------------------------------------------------------- |
| **Frontend / UI**                  | Flask                | Interfaz web para interactuar con el juego y mostrar los resultados. |
| **Visión por Computadora**         | OpenCV               | Captura y procesamiento de imágenes en tiempo real.                  |
| **Reconocimiento de Señas**        | MediaPipe            | Reconocer gestos manuales en tiempo real y proporciona los resultados reconocidos junto con los puntos de referencia de las manos detectadas                                                                                       |
| **Backend / Lógica de Negocio**    | Python 3.9+          | Contiene toda la lógica del juego.                                   |
| **Base de Datos**                  | SQLite + SQLAlchemy  | Almacenamiento de usuarios y sesiones.                               |

---
