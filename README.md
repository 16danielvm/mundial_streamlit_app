# ⚽ Quiniela Mundial 2026

Aplicación web desarrollada con **Streamlit** para organizar una quiniela del Mundial de Fútbol 2026, permitiendo a los participantes registrar sus pronósticos, competir por puntos y seguir en tiempo real la clasificación general.

## 🌐 Aplicación en línea

**https://quiniela-mundial-2026-sin-pample.streamlit.app/**

---

## 📖 Descripción

La aplicación permite a los usuarios crear una cuenta, iniciar sesión y registrar sus predicciones para cada partido del Mundial 2026.

Los puntos se asignan automáticamente una vez que los resultados oficiales son registrados:

* ✅ **3 puntos** por acertar el marcador exacto.
* ✅ **1 punto** por acertar únicamente el resultado (ganador o empate).
* ❌ **0 puntos** en caso contrario.

Las predicciones permanecen abiertas únicamente hasta el inicio del partido, garantizando la equidad entre los participantes.

---

## 🚀 Funcionalidades

### 👤 Gestión de usuarios

* Registro de usuarios.
* Inicio de sesión.
* Cambio de contraseña.
* Restablecimiento de contraseña por parte del administrador mediante contraseñas temporales.

### ⚽ Predicciones

* Registro y modificación de pronósticos.
* Bloqueo automático una vez iniciado el partido.
* Horarios adaptados automáticamente a la zona horaria del usuario.

### 📅 Calendario del Mundial

* Calendario completo de los partidos.
* Visualización de fecha, hora, estadio y fase.
* Estado de las predicciones (abiertas o cerradas).
* Banderas de las selecciones participantes.

### 🏆 Clasificación general

* Tabla de posiciones actualizada automáticamente.
* Número de predicciones realizadas.
* Marcadores exactos obtenidos.
* Resultados acertados.

### 👀 Predicciones de todos

* Visualización de las predicciones realizadas por todos los participantes.

### 🏅 Logros y medallas

La aplicación reconoce distintos hitos entre los participantes:

* 👑 **Rey del Marcador**
* 🎯 **Nostradamus**
* 🔥 **Enrachado**
* 💀 **Mufa Oficial**
* 🫏 **0 Ball Knowledge**

### ⭐ MVP por fecha

Se determina automáticamente el mejor jugador de cada jornada, considerando:

1. Mayor cantidad de puntos.
2. Mayor número de marcadores exactos.
3. Mayor cantidad de aciertos.
4. Menor número de predicciones realizadas.

En caso de empate, se reconocen múltiples MVP.

### 📊 Estadísticas personales

Cada usuario dispone de estadísticas individuales:

* Puntos totales.
* Posición en la clasificación.
* Porcentaje de acierto.
* Marcadores exactos.
* Resultados acertados.
* Mejor y peor racha.
* MVP obtenidos.
* Medallas conseguidas.
* Distribución de puntos.
* Evolución de puntos.
* Historial completo de predicciones.

### 👑 Panel de administración

Permite:

* Añadir partidos manualmente.
* Registrar resultados.
* Recalcular automáticamente los puntos.
* Gestionar usuarios.
* Restablecer contraseñas.
* Actualizar resultados mediante integración con APIs externas (Football-Data).

---

## 🔄 Sistema de puntuación

| Situación             | Puntos |
| --------------------- | -----: |
| Marcador exacto       |      3 |
| Resultado acertado    |      1 |
| Pronóstico incorrecto |      0 |

---

## 🌎 Soporte de zonas horarias

La aplicación detecta automáticamente la zona horaria del navegador del usuario y muestra los horarios correspondientes a su ubicación, permitiendo la participación de usuarios de distintos países.

---

## 🛠️ Tecnologías utilizadas

* Python
* Streamlit
* PostgreSQL
* Supabase
* Pandas
* Psycopg2
* Requests
* Bcrypt

---

## 🔐 Seguridad

* Contraseñas almacenadas mediante hash utilizando **bcrypt**.
* Variables sensibles gestionadas mediante **Streamlit Secrets**.
* Base de datos alojada en **Supabase PostgreSQL**.
* Acceso restringido al panel de administración.

---

## ⚽ Inspiración

La aplicación nació como una forma de compartir la emoción del Mundial de Fútbol 2026 y competir entre amigos mediante una quiniela interactiva con estadísticas, logros y clasificación en tiempo real.

---

# ¡Que ruede el balón y que gane el mejor pronosticador! 🏆⚽

