import streamlit as st
import pandas as pd
import numpy_financial as npf

# Configuración de la página
st.set_page_config(page_title="Simulador Financiero Educativo", layout="wide")

# --- ESTILOS ---
st.title("📊 Simulador de Negocio Educativo (Versión Beta)")
st.sidebar.header("Configuración de Escenarios")

# --- INPUTS (Tus variables solicitadas) ---
with st.sidebar:
    st.subheader("🏗️ Infraestructura")
    m2_totales = st.number_input("Metros Cuadrados Totales", value=500)
    inv_m2 = st.slider("Inversión por m2 ($)", 500, 5000, 1200)
    canon_m2 = st.slider("Arriendo mensual por m2 ($)", 10, 100, 30)
    
    st.subheader("👨‍🏫 Operación")
    tarifa = st.number_input("Tarifa Mensual Estudiante ($)", value=350)
    est_grupo = st.slider("Estudiantes por Grupo", 10, 40, 25)
    relacion_tecnica = st.slider("Relación (Estudiantes/Maestro)", 10, 30, 20)
    jornada = st.selectbox("Jornada", ["Única", "Doble"])
    mult_jornada = 2 if jornada == "Doble" else 1

    st.subheader("📈 Ocupación proyectada (%)")
    ocu_y1 = st.slider("Año 1", 0, 100, 30) / 100
    ocu_y2 = st.slider("Año 2", 0, 100, 50) / 100
    ocu_y3 = st.slider("Año 3", 0, 100, 70) / 100
    ocu_y4 = st.slider("Año 4", 0, 100, 85) / 100
    ocu_y5 = st.slider("Año 5", 0, 100, 95) / 100
    ocupaciones = [ocu_y1, ocu_y2, ocu_y3, ocu_y4, ocu_y5]

# --- LÓGICA FINANCIERA (DUMMY) ---
inv_inicial = m2_totales * inv_m2
capacidad_max = (m2_totales / 1.5) * mult_jornada # 1.5m2 por niño aprox

flujos = [-inv_inicial]
datos_tabla = []

for i, ocu in enumerate(ocupaciones):
    num_est = capacidad_max * ocu
    ingresos = num_est * tarifa * 10 # 10 meses
    
    # Costos simplificados
    num_maestros = num_est / relacion_tecnica
    costo_maestros = num_maestros * 2500 * 12 # Sueldo promedio dummy
    arriendo_anual = m2_totales * canon_m2 * 12
    
    utilidad_bruta = ingresos - costo_maestros
    ebitda = utilidad_bruta - arriendo_anual
    utilidad_neta = ebitda * 0.65 # Menos 35% impuestos
    
    flujos.append(utilidad_neta)
    datos_tabla.append({
        "Año": i+1,
        "Estudiantes": int(num_est),
        "Ingresos": ingresos,
        "EBITDA": ebitda,
        "Utilidad Neta": utilidad_neta,
        "Margen Neto": f"{(utilidad_neta/ingresos if ingresos > 0 else 0):.1%}"
    })

# --- INDICADORES ---
tir = npf.irr(flujos)
vna = npf.npv(0.12, flujos)

col1, col2, col3, col4 = st.columns(4)
col1.metric("TIR", f"{tir:.2%}")
col2.metric("VNA (12%)", f"${vna:,.0f}")
col3.metric("Inversión", f"${inv_inicial:,.0f}")
col4.metric("Payback", "3.2 Años") # Dummy static

# --- VISUALIZACIÓN ---
st.subheader("Proyección Financiera a 5 Años")
df = pd.DataFrame(datos_tabla)
st.dataframe(df.style.format({"Ingresos": "${:,.0f}", "EBITDA": "${:,.0f}", "Utilidad Neta": "${:,.0f}"}), use_container_width=True)

st.line_chart(df.set_index("Año")[["Ingresos", "EBITDA", "Utilidad Neta"]])

st.success("✅ App lista. Cambia los sliders a la izquierda para ver el recalculo.")