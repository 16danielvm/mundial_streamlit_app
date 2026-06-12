# Quiniela Mundial 2026 - Streamlit

Aplicación web simple para registrar predicciones de partidos, bloquear pronósticos cuando inicia el partido, capturar resultados reales y calcular automáticamente una tabla de clasificación.

## Requisitos

Necesitas tener Python instalado.

Instala las dependencias:

```bash
pip install -r requirements.txt
```

Ejecuta la aplicación:

```bash
streamlit run app.py
```

<!-- ## Clave de administrador

La clave inicial es:

```text
admin123
```

Puedes cambiarla dentro del archivo `app.py`, en la variable `ADMIN_PIN`.

## Base de datos

La app crea automáticamente un archivo llamado:

```text
quiniela_mundial.db
```

Ahí se guardan usuarios, partidos, predicciones y resultados. -->

## Puntuación

- Marcador exacto: 3 puntos.
- Acertar ganador o empate sin marcador exacto: 1 punto.
- Fallar resultado: 0 puntos.

## Horario

La app usa la zona horaria:

```text
America/Mexico_City
```

Las predicciones se bloquean automáticamente cuando llega la hora de inicio del partido.
