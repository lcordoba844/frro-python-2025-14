# SignLearn: Juego Interactivo para Aprender Lengua de Señas

## Descripción del Proyecto

**SignLearn** es un juego educativo interactivo diseñado para que los niños aprendan y practiquen el lenguaje de señas de manera divertida y dinámica.
A través de la cámara, el sistema muestra en pantalla una letra o seña que el niño debe imitar con sus manos. Utilizando **visión por computadora (OpenCV)** y un **modelo de inteligencia artificial entrenado para reconocer gestos**, el juego evalúa la precisión y el tiempo de ejecución del gesto.

Cada intento se registra en la base de datos, permitiendo analizar el progreso individual, ofrecer retroalimentación automática y mantener un historial de desempeño.
El sistema incorpora elementos de **gamificación**, como puntos, niveles y logros, para incentivar el aprendizaje y la práctica constante.

El objetivo principal de *SignLearn* es fomentar el aprendizaje visual y corporal del lenguaje de señas, reforzando la memoria y la motricidad fina a través del juego.

---

## Modelo de Dominio

**Entidades Principales:**

1. **Usuario**

   * Representa al jugador (niño o usuario registrado).
   * Guarda información básica: nombre, edad, usuario, contraseña (encriptada).
   * Se relaciona con las partidas o sesiones de juego que ha realizado.

2. **SesionJuego**

   * Registra cada sesión o ronda de práctica del usuario.
   * Contiene información sobre:

     * Fecha y hora de la sesión.
     * Nivel o dificultad.
     * Tiempo promedio por seña.
     * Precisión promedio.
     * Puntaje total obtenido.
     * Resultado (por ejemplo, “superado” o “a mejorar”).
   * Cada sesión pertenece a un único usuario.

3. **DesempeñoSeña**

   * Representa el análisis de una seña específica durante una sesión.
   * Guarda la seña mostrada, la precisión obtenida, el tiempo de reacción y si fue reconocida correctamente.
   * Está vinculada a una sesión de juego.

---

## Reglas de Negocio

1. **RN01 – Validación de señas**

   * El sistema solo considera una seña “correcta” si la precisión de la detección (según el modelo IA) supera el umbral del 80%.

2. **RN02 – Asignación de puntos**

   * El puntaje de cada seña depende de:

     * Precisión (mayor precisión = más puntos).
     * Tiempo (menor tiempo = bonificación).
   * Si el jugador supera el 90% de precisión promedio en la sesión, obtiene puntos extra.

3. **RN03 – Progresión de niveles**

   * Para avanzar de nivel, el usuario debe completar al menos 10 señas con una precisión promedio mayor o igual al 85%.

4. **RN04 – Retroalimentación**

   * Al finalizar cada sesión, el sistema genera un reporte visual que muestra:

     * Porcentaje de aciertos.
     * Señales que necesitan mejorar.
     * Progreso respecto a sesiones anteriores.

5. **RN05 – Registro y seguridad**

   * Todas las contraseñas deben almacenarse en formato cifrado (hash SHA256 o bcrypt).
   * Los datos del usuario y su progreso deben mantenerse privados.

---

## Casos de Uso

| **CU**   | **Nombre del Caso de Uso**        | **Descripción**                                                                                                                    |
| :------- | :-------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| **CU01** | Registro de Usuario               | Permite que un nuevo jugador se registre en el sistema ingresando su nombre, edad, usuario y contraseña.                           |
| **CU02** | Inicio de Sesión                  | Permite que el usuario autenticado acceda al juego y a su historial de progreso.                                                   |
| **CU03** | Iniciar Juego / Sesión            | El usuario inicia una nueva sesión de práctica. Se muestran las señas y se activa la cámara para el reconocimiento.                |
| **CU04** | Detección y Evaluación de Señales | El sistema utiliza OpenCV y el modelo de IA para comparar la seña del usuario con la seña objetivo, calculando precisión y tiempo. |
| **CU05** | Cálculo de Puntuación y Nivel     | El sistema calcula los puntos obtenidos según precisión y tiempo, y determina si el jugador avanza de nivel.                       |
| **CU06** | Almacenamiento de Resultados      | Al finalizar la sesión, se guarda el puntaje, precisión promedio, nivel y fecha en la base de datos.                               |
| **CU07** | Visualización de Progreso         | El usuario puede consultar un resumen de sus sesiones pasadas con estadísticas y evolución de desempeño.                           |

---

## Bosquejo de Arquitectura

El sistema se desarrollará con una **arquitectura en 3 capas**:

1. **Capa de Presentación**

   * Implementada con **Flask** o **Streamlit** (según la interfaz elegida).
   * Gestiona la interacción del usuario, mostrando señas, niveles y resultados.
   * Controla la cámara y los elementos de gamificación.

2. **Capa de Negocio**

   * Implementada en **Python**.
   * Contiene la lógica del juego: cálculo de precisión, puntuación, detección de errores y avance de nivel.
   * Utiliza **OpenCV** y **TensorFlow/PyTorch** (modelo IA para reconocimiento de señas).
   * Incluye tests unitarios con **Pytest**.

3. **Capa de Datos**

   * Base de datos **SQLite** (simple y portable).
   * ORM: **SQLAlchemy** para mapear clases Python a tablas.
   * Se almacenan usuarios, sesiones de juego y desempeño por seña.

---

## Stack Tecnológico

| Componente                         | Tecnología           | Descripción                                                          |
| ---------------------------------- | -------------------- | -------------------------------------------------------------------- |
| **Frontend / UI**                  | Flask / Streamlit    | Interfaz web para interactuar con el juego y mostrar los resultados. |
| **Visión por Computadora**         | OpenCV               | Captura y procesamiento de imágenes en tiempo real.                  |
| **IA / Reconocimiento de Señales** | TensorFlow o PyTorch | Modelo preentrenado que detecta gestos y calcula precisión.          |
| **Backend / Lógica de Negocio**    | Python 3.9+          | Contiene toda la lógica del juego y comunicación con el modelo IA.   |
| **Base de Datos**                  | SQLite + SQLAlchemy  | Almacenamiento de usuarios y sesiones.                               |
| **Testing**                        | Pytest               | Pruebas unitarias de reglas de negocio y detección.                  |

---

¿Querés que te lo deje también con los diagramas tipo el del modelo de dominio (para hacerlo igual que el ejemplo de Q-Sec)?
Puedo generarte el **diagrama UML** del dominio y el **de arquitectura** listos para entregar.
