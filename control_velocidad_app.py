
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime, timedelta

# Diccionario de kilometrajes por punto
km_map = {
    'A': 0.0,
    'B': 4.0,
    'C': 8.8,
    'D': 19.0,
    'E': 23.5
}

# Tiempos mínimos por subtramo con 5% de tolerancia (en segundos)
min_times = {
    ('A', 'B'): 273,  # 4 min 33 seg
    ('B', 'C'): 327,  # 5 min 27 seg
    ('C', 'D'): 437,  # 7 min 17 seg
    ('D', 'E'): 193,  # 3 min 13 seg
}
# Agregar tramos inversos
min_times.update({(b, a): t for (a, b), t in min_times.items()})

# Tramos compuestos
min_times[('A', 'C')] = min_times[('A', 'B')] + min_times[('B', 'C')]
min_times[('C', 'A')] = min_times[('C', 'B')] + min_times[('B', 'A')]
min_times[('A', 'D')] = min_times[('A', 'C')] + min_times[('C', 'D')]
min_times[('D', 'A')] = min_times[('D', 'C')] + min_times[('C', 'A')]
min_times[('A', 'E')] = min_times[('A', 'D')] + min_times[('D', 'E')]
min_times[('E', 'A')] = min_times[('E', 'D')] + min_times[('D', 'A')]

min_times[('B', 'D')] = min_times[('B', 'C')] + min_times[('C', 'D')]
min_times[('D', 'B')] = min_times[('D', 'C')] + min_times[('C', 'B')]
min_times[('B', 'E')] = min_times[('B', 'D')] + min_times[('D', 'E')]
min_times[('E', 'B')] = min_times[('E', 'D')] + min_times[('D', 'B')]

min_times[('C', 'E')] = min_times[('C', 'D')] + min_times[('D', 'E')]
min_times[('E', 'C')] = min_times[('E', 'D')] + min_times[('D', 'C')]

# Función para extraer letra del punto
def extraer_punto(punto_str):
    for letra in km_map.keys():
        if f"Punto {letra}" in punto_str:
            return letra
    return None

# Función para calcular segundos entre dos horas
def calcular_segundos(hora_inicio, hora_fin):
    formato = "%H:%M:%S"
    t1 = datetime.strptime(hora_inicio, formato)
    t2 = datetime.strptime(hora_fin, formato)
    return int((t2 - t1).total_seconds())

# Función principal de evaluación
def evaluar_cumplimiento(df):
    resultados = []
    df['Punto'] = df['Punto de control'].apply(extraer_punto)
    df['Hora'] = pd.to_datetime(df['Hora (Formato hh:mm:ss)'], format="%H:%M:%S").dt.time

    df = df.dropna(subset=['PPU (Placa Patente Unica)', 'Punto', 'Hora', 'Fecha'])

    for (ppu, fecha, sentido), grupo in df.groupby(['PPU (Placa Patente Unica)', 'Fecha', 'Sentido del Tránsito']):
        grupo = grupo.sort_values('Hora')
        if len(grupo) < 2:
            resultados.append([ppu, fecha, sentido, None, None, None, None, None, None, '🟨 Registro incompleto'])
            continue

        inicio = grupo.iloc[0]
        fin = grupo.iloc[-1]
        p_ini = inicio['Punto']
        p_fin = fin['Punto']
        h_ini = inicio['Hora'].strftime("%H:%M:%S")
        h_fin = fin['Hora'].strftime("%H:%M:%S")
        segundos = calcular_segundos(h_ini, h_fin)

        tramo = (p_ini, p_fin)
        if tramo in min_times:
            minimo = min_times[tramo]
            cumple = '✅ Cumple' if segundos >= minimo else '🟥 No cumple'
            resultados.append([ppu, fecha, sentido, p_ini, p_fin, h_ini, h_fin,
                               f"{segundos//60} min {segundos%60} seg",
                               f"{minimo//60} min {minimo%60} seg",
                               cumple])
        else:
            resultados.append([ppu, fecha, sentido, p_ini, p_fin, h_ini, h_fin,
                               f"{segundos//60} min {segundos%60} seg",
                               '—', '🟨 Tramo no definido'])

    columnas = ['PPU', 'Fecha', 'Sentido', 'Punto inicio', 'Punto fin',
                'Hora inicio', 'Hora fin', 'Tiempo transcurrido',
                'Tiempo mínimo requerido', 'Resultado']
    return pd.DataFrame(resultados, columns=columnas)

# Interfaz Streamlit
st.title("🚗 Control de Velocidad Vehicular - Faena Aurora")
st.write("Sube un archivo Excel exportado desde Microsoft Forms para evaluar el cumplimiento de tiempos mínimos entre puntos de control.")

archivo = st.file_uploader("📤 Subir archivo Excel (.xlsx)", type=["xlsx"])

if archivo:
    try:
        df = pd.read_excel(archivo, sheet_name=0, engine='openpyxl')
        resultados = evaluar_cumplimiento(df)

        st.success("✅ Evaluación completada")
        st.dataframe(resultados.style.applymap(
            lambda x: 'background-color: lightgreen' if '✅' in str(x)
            else 'background-color: lightcoral' if '🟥' in str(x)
            else 'background-color: khaki' if '🟨' in str(x)
            else ''
        , subset=['Resultado']))

        # Descargar resultados
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            resultados.to_excel(writer, index=False, sheet_name='Resultados')
        datos_excel = output.getvalue()

        st.download_button(
            label="📥 Descargar resultados en Excel",
            data=datos_excel,
            file_name="resultados_control_velocidad.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
