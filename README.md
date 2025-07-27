# Aplicación Web de Control de Velocidad Vehicular

Esta aplicación permite evaluar automáticamente si un vehículo cumple con los tiempos mínimos de traslado entre puntos de control establecidos, utilizando registros exportados desde Microsoft Forms (formato Excel).

## ✅ Objetivo

Detectar si un vehículo cumple con el tiempo mínimo de traslado por tramo, según los registros de control de velocidad en faena. El resultado indica:

- 🟩 **Cumple**
- 🟥 **No cumple**
- 🟨 **Registro incompleto**
- 🟨 **Tramo no definido**

## 📥 Entrada

Archivo Excel (.xlsx) exportado desde Microsoft Forms, con columnas como:

- Fecha
- Hora (Formato hh:mm)
- Punto de control (A, B, C, D, E)
- Sentido del Tránsito (IDA o REGRESO)
- PPU (Placa Patente Única)

## 🧠 Lógica de Evaluación

1. Asignación de kilometrajes:
   - A: km 0
   - B: km 4
   - C: km 8.8
   - D: km 19
   - E: km 23.5

2. Tiempos mínimos por tramo (con 5% de tolerancia):

| Tramo | Distancia | Velocidad | Tiempo mínimo |
|-------|-----------|-----------|----------------|
| A-B / B-A | 4.0 km | 50 km/h | 4 min 33 seg |
| B-C / C-B | 4.8 km | 50 km/h | 5 min 27 seg |
| C-D / D-C | 10.2 km | 80 km/h | 7 min 17 seg |
| D-E / E-D | 4.5 km | 80 km/h | 3 min 13 seg |
| A-E / E-A | 23.5 km | Mixto | 20 min 30 seg |

3. Evaluación por agrupación de:
   - PPU
   - Fecha
   - Sentido del Tránsito

4. Se detectan pares válidos de registros (inicio y fin) y se calcula el tiempo transcurrido.

5. Se compara con el tiempo mínimo requerido (sumando subtramos si es necesario).

## 🎨 Interfaz

- Subida de archivo Excel
- Visualización de resultados con colores
- Opción para descargar resultados en Excel

## 🚀 Despliegue en Streamlit Cloud

1. Sube este repositorio a GitHub.
2. Ve a [https://streamlit.io/cloud](https://streamlit.io/cloud).
3. Crea una nueva app seleccionando `control_velocidad_app.py`.
4. ¡Listo! Obtendrás un link público para usar la app.

## 📦 Requisitos

Instalaciones necesarias (ver `requirements.txt`):

- streamlit
- pandas
- openpyxl

## 👤 Autor

Luis Soto  
Proyecto: Control de Velocidad – Faena Aurora
