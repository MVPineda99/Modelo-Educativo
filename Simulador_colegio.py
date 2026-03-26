import streamlit as st
import pandas as pd
import numpy as np
import math
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(page_title="Colegio Tipo — Modelo Financiero", layout="wide")
st.title("📊 Colegio Tipo — Modelo Financiero Independiente (COP)")
st.caption("Proyección a 12 años con perpetuidad. Todos los supuestos son editables.")

YEARS = list(range(13))
LABELS = [f"Año {y}" for y in YEARS]
CALENDARS = list(range(2026, 2039))

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR — INPUTS
# ═══════════════════════════════════════════════════════════════════

with st.sidebar.expander("🏫 Jornada", expanded=True):
    grupos_por_salon = st.selectbox("Grupos por Salón (2=Doble, 1=Única)", [2, 1], index=0)

with st.sidebar.expander("🏗️ Infraestructura y Adecuación"):
    area_total = st.number_input("Área Total (m²)", value=2500, step=100)
    salones_fisicos = st.number_input("Salones Físicos Totales", value=14, step=1)
    m2_por_salon = st.number_input("m² por Salón", value=60, step=5)
    costo_adec_m2 = st.number_input("Costo Adecuación (COP/m²) 2026", value=2600000, step=100000, format="%d")
    salones_etapa1 = st.number_input("Salones Etapa 1", value=10, step=1)
    salones_etapa2 = st.number_input("Salones Etapa 2", value=4, step=1)
    vida_util_adec = st.number_input("Vida Útil Adecuación (años)", value=10, step=1)
    inv_mobiliario = st.number_input("Inversión Mobiliario Escolar", value=120000000, step=10000000, format="%d")
    inv_equipos = st.number_input("Inversión Equipos Admin", value=50000000, step=5000000, format="%d")
    vida_util_mob = st.number_input("Vida Útil Mobiliario (años)", value=5, step=1)
    vida_util_eq = st.number_input("Vida Útil Equipos (años)", value=5, step=1)

inv_adec_e1 = salones_etapa1 * m2_por_salon * costo_adec_m2
inv_adec_e2 = salones_etapa2 * m2_por_salon * costo_adec_m2
inv_total_adec = inv_adec_e1 + inv_adec_e2

# Helper function to create grid inputs in sidebar
def grid_inputs(label, defaults, is_pct=False):
    st.markdown(f"**{label}**")
    res = []
    # Usamos columnas de 3 para que quepa bien en el sidebar
    cols = st.columns(3)
    for i in range(13):
        with cols[i % 3]:
            val = st.number_input(f"Año {i}", value=float(defaults[i]), 
                                  step=0.01 if is_pct else 1.0, 
                                  format="%.3f" if is_pct else "%.0f",
                                  key=f"{label}_{i}")
            res.append(val)
    return res

with st.sidebar.expander("🎓 Estudiantes y Ocupación"):
    alumnos_por_grupo = st.number_input("Alumnos por Grupo", value=34, step=1)
    
    preescolar = grid_inputs("Preescolar", [0,82,133,149,162,171,174,175,175,175,175,175,175])
    primaria = grid_inputs("Primaria", [0,184,300,334,364,386,392,394,394,394,394,394,394])
    secundaria = grid_inputs("Secundaria", [0,142,233,260,283,300,305,307,307,307,307,307,307])
    tasa_desercion = grid_inputs("Tasa Deserción", [0,0.08,0.06,0.05,0.04,0.04,0.03,0.03,0.03,0.03,0.03,0.03,0.03], is_pct=True)

total_alumnos = [int(preescolar[i]+primaria[i]+secundaria[i]) for i in range(13)]
salones_disp = [0]+[salones_etapa1]+[salones_fisicos]*11
capacidad_max = [s*alumnos_por_grupo*grupos_por_salon for s in salones_disp]
tasa_ocupacion = [total_alumnos[i]/capacidad_max[i] if capacidad_max[i]>0 else 0 for i in range(13)]

with st.sidebar.expander("🌐 Estudiantes Red Central"):
    est_red = grid_inputs("Estudiantes totales red", [6901,7200,8700,10200,11700,13200,14700,16200,17700,19200,20700,22200,23700])

with st.sidebar.expander("💰 Tarifas (COP)"):
    matricula_base = st.number_input("Matrícula Anual Base 2026", value=900000, step=50000, format="%d")
    pension_base = st.number_input("Pensión Mensual Base 2026", value=850000, step=50000, format="%d")
    meses_pension = st.number_input("Meses de Pensión", value=10, step=1)
    tasa_morosidad = grid_inputs("Tasa Morosidad", [0,0.08,0.06,0.05,0.05,0.04,0.04,0.03,0.03,0.03,0.03,0.03,0.03], is_pct=True)

with st.sidebar.expander("📈 Supuestos Macroeconómicos"):
    ipc = grid_inputs("IPC Proyectado", [0.063,0.048,0.037,0.035,0.033,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03], is_pct=True)
    incr_tarifa = grid_inputs("Incremento Tarifas", [0.078,0.063,0.052,0.05,0.048,0.045,0.045,0.045,0.045,0.045,0.045,0.045,0.045], is_pct=True)

with st.sidebar.expander("👔 Salarios Base (2026)"):
    smlmv = st.number_input("SMLMV 2026", value=1750905, step=50000, format="%d")
    aux_transporte = st.number_input("Auxilio Transporte Mensual", value=249095, step=10000, format="%d")
    factor_prestacional = st.number_input("Factor Prestacional", value=0.4287, step=0.01, format="%.4f")
    meses_laborados = st.number_input("Meses Laborados", value=11.1, step=0.1, format="%.1f")
    dotacion_anual = st.number_input("Dotación Anual/persona", value=400000, step=50000, format="%d")
    capacitacion_anual = st.number_input("Capacitación Anual/persona", value=300000, step=50000, format="%d")
    st.markdown("---")
    sal_mentor = st.number_input("Mentor", value=3180000, step=100000, format="%d")
    sal_mediador = st.number_input("Mediador", value=2090000, step=100000, format="%d")
    sal_mentor_ing = st.number_input("Mentor Inglés", value=5380000, step=100000, format="%d")
    sal_mentor_arte = st.number_input("Mentor Arte y Cuerpo", value=3180000, step=100000, format="%d")
    sal_mentor_terr = st.number_input("Mentor Aprend. Territorio", value=5380000, step=100000, format="%d")
    sal_orientador = st.number_input("Orientador del Cuidado", value=5380000, step=100000, format="%d")
    sal_aux_admin = st.number_input("Auxiliar Admin CdE", value=2490000, step=100000, format="%d")
    sal_lider = st.number_input("Líder Centro Experiencia", value=7670000, step=100000, format="%d")

roles_info = [
    ("Mentores", sal_mentor, True), ("Mediadores", sal_mediador, True),
    ("Mentor Inglés", sal_mentor_ing, False), ("Mentor A&C", sal_mentor_arte, True),
    ("Mentor Terr.", sal_mentor_terr, False), ("Orientador", sal_orientador, False),
    ("Aux. Admin.", sal_aux_admin, True), ("Líder CdE", sal_lider, False),
]
costo_anual_base = []
for _, sal, tiene_aux in roles_info:
    cm = sal*(1+factor_prestacional)+(aux_transporte if tiene_aux else 0)
    costo_anual_base.append(cm*meses_laborados)

with st.sidebar.expander("👥 Relaciones Técnicas"):
    ratio_mediadores = st.number_input("Alumnos por Mediador", value=49, step=1)
    ratio_mentor_ing = st.number_input("Grupos por Mentor Inglés", value=10, step=1)
    ratio_mentor_arte = st.number_input("Grupos por Mentor A&C", value=10, step=1)
    ratio_orientador = st.number_input("Alumnos por Orientador", value=800, step=50)

with st.sidebar.expander("🏢 Costos Fijos Base 2026 (COP/Año)"):
    cf_arrend = st.number_input("Arrend. Edificios", value=900000000, step=50000000, format="%d")
    cf_servicios = st.number_input("Servicios Públicos", value=125000000, step=10000000, format="%d")
    cf_aseo = st.number_input("Servicio de Aseo", value=350000000, step=25000000, format="%d")
    cf_vigilancia = st.number_input("Servicio de Vigilancia", value=175000000, step=10000000, format="%d")
    cf_telefonia = st.number_input("Telefonía e Internet", value=25000000, step=5000000, format="%d")
    cf_mantenimiento = st.number_input("Mantenimiento", value=150000000, step=10000000, format="%d")

costos_fijos_base = {"Arrend. Edificios": cf_arrend, "Servicios Públicos": cf_servicios,
    "Servicio de Aseo": cf_aseo, "Servicio de Vigilancia": cf_vigilancia,
    "Telefonía e Internet": cf_telefonia, "Mantenimiento": cf_mantenimiento}

with st.sidebar.expander("📋 Costos Per-Cápita (COP/alumno/año 2026)"):
    cp_honorarios = st.number_input("Honorarios", value=80000, step=10000, format="%d")
    cp_seguros = st.number_input("Seguros", value=20000, step=5000, format="%d")
    cp_otros_serv = st.number_input("Otros Servicios", value=90000, step=10000, format="%d")
    cp_viajes = st.number_input("Gastos de Viaje", value=10000, step=1000, format="%d")
    cp_legales = st.number_input("Gastos Legales", value=10000, step=1000, format="%d")
    cp_aseo_caf = st.number_input("Aseo y Cafetería", value=20000, step=5000, format="%d")
    cp_utiles = st.number_input("Útiles y Papelería", value=20000, step=5000, format="%d")
    cp_otros = st.number_input("Otros", value=10000, step=1000, format="%d")
    cp_arrend_equipo = st.number_input("Arrend. Equipo Base/Unidad HC", value=2430000, step=100000, format="%d")

costos_percapita_base = {"Honorarios": cp_honorarios, "Seguros": cp_seguros,
    "Otros Servicios": cp_otros_serv, "Gastos de Viaje": cp_viajes,
    "Gastos Legales": cp_legales, "Aseo y Cafetería": cp_aseo_caf,
    "Útiles y Papelería": cp_utiles, "Otros": cp_otros}

with st.sidebar.expander("🍽️ Negocios Complementarios"):
    caf_ingreso_base = st.number_input("Cafetería Ingreso/Alumno/Año", value=1200000, step=100000, format="%d")
    caf_costo_pct = st.number_input("Cafetería Costo (% Ing)", value=0.65, step=0.05, format="%.2f")
    transp_ingreso_base = st.number_input("Transporte Ingreso/Alumno/Año", value=2400000, step=100000, format="%d")
    transp_pen = grid_inputs("Transporte Penetración %", [0,0.3,0.35,0.38,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4], is_pct=True)
    transp_costo_pct = st.number_input("Transporte Costo (% Ing)", value=0.75, step=0.05, format="%.2f")
    extra_ingreso_base = st.number_input("Extracurriculares Ingreso/Al/Año", value=800000, step=50000, format="%d")
    extra_pen = grid_inputs("Extracurriculares Penetración %", [0,0.2,0.25,0.3,0.35,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4], is_pct=True)
    extra_costo_pct = st.number_input("Extracurriculares Costo (% Ing)", value=0.60, step=0.05, format="%.2f")

with st.sidebar.expander("🏛️ Gastos Admin — Red Central"):
    rc_laborales = grid_inputs("Gastos Laborales RC", [0,13751141714,7569315956,5512985122,4519269553,3951649298,3670094285,3412558526,3718323770,4052972909,4449758957,4882275528,5382708769])
    rc_honorarios = grid_inputs("Honorarios RC", [0,718548291,378423457,263155672,205873261,171797119,149334646,133517973,139272598,145275247,151536610,158067838,164880562])
    rc_iva = grid_inputs("IVA, Arriendos y Otros RC", [0,1367220526,729388190,513712626,406972275,343851089,302578931,273827432,289067381,305112350,322003420,339783720,358498526])

with st.sidebar.expander("⚙️ Otros Supuestos"):
    tasa_impuesto = st.number_input("Tasa Impuesto Renta", value=0.35, step=0.01, format="%.2f")
    capital_inicial = st.number_input("Capital Inicial (COP)", value=5000000000, step=500000000, format="%d")
    opex_ini_a0 = st.number_input("OPEX Inicial Año 0", value=80000000, step=10000000, format="%d")
    opex_ini_a1 = st.number_input("OPEX Inicial Año 1", value=40000000, step=10000000, format="%d")
    dias_cxc = st.number_input("Días Cuentas por Cobrar", value=30, step=5)
    wacc = st.number_input("WACC", value=0.171, step=0.005, format="%.3f")
    gradiente_g = st.number_input("Gradiente Crecimiento LP (g)", value=0.03, step=0.005, format="%.3f")
    capex_repo_pct = st.number_input("CAPEX Reposición (% Ingresos)", value=0.014, step=0.001, format="%.3f")

with st.sidebar.expander("🏦 Impuestos de Operación"):
    imp_oper_base = st.number_input("Impuestos Operación Año 0", value=237500000, step=10000000, format="%d")

# ═══════════════════════════════════════════════════════════════════
# CÁLCULOS (SIN CAMBIOS)
# ═══════════════════════════════════════════════════════════════════

factor_tarifa = [1.0]*13
factor_salario = [1.0]*13
factor_ipc = [1.0]*13
for y in range(1,13):
    factor_tarifa[y] = factor_tarifa[y-1]*(1+incr_tarifa[y])
    factor_salario[y] = factor_salario[y-1]*(1+incr_tarifa[y])
    factor_ipc[y] = factor_ipc[y-1]*(1+ipc[y])

grupos_totales = [0]*13
for y in range(13):
    if total_alumnos[y]>0 and salones_disp[y]>0:
        grupos_totales[y] = salones_disp[y]*grupos_por_salon

hc = {r[0]: [0]*13 for r in roles_info}
for y in range(13):
    if total_alumnos[y]==0: continue
    g = grupos_totales[y]; a = total_alumnos[y]
    hc["Mentores"][y] = g
    hc["Mediadores"][y] = max(math.ceil(a/ratio_mediadores), math.ceil(g/2), 1)
    hc["Mentor Inglés"][y] = max(math.ceil(g/ratio_mentor_ing), 1)
    hc["Mentor A&C"][y] = max(math.ceil(g/ratio_mentor_arte), 1)
    hc["Mentor Terr."][y] = 1
    hc["Orientador"][y] = max(math.ceil(a/ratio_orientador), 1)
    hc["Aux. Admin."][y] = 1
    hc["Líder CdE"][y] = 1
total_hc = [sum(hc[r][y] for r in hc) for y in range(13)]

role_keys = list(hc.keys())
nomina_rol = {r: [0.0]*13 for r in role_keys}
for y in range(13):
    for idx, r in enumerate(role_keys):
        nomina_rol[r][y] = hc[r][y]*costo_anual_base[idx]*factor_salario[y]

dotacion = [(hc["Mentores"][y]+hc["Mediadores"][y])*dotacion_anual*factor_ipc[y] for y in range(13)]
capacitacion_cost = [total_hc[y]*capacitacion_anual*factor_ipc[y] for y in range(13)]
total_nomina = [sum(nomina_rol[r][y] for r in role_keys)+dotacion[y]+capacitacion_cost[y] for y in range(13)]

matricula = [matricula_base*factor_tarifa[y] for y in range(13)]
pension = [pension_base*factor_tarifa[y] for y in range(13)]
ingreso_por_al = [matricula[y]+pension[y]*meses_pension for y in range(13)]

ing_mat = [total_alumnos[y]*matricula[y] for y in range(13)]
ing_pen = [total_alumnos[y]*pension[y]*meses_pension for y in range(13)]
total_ing = [ing_mat[y]+ing_pen[y] for y in range(13)]
prov_mor = [-total_ing[y]*tasa_morosidad[y] for y in range(13)]
ing_netos = [total_ing[y]+prov_mor[y] for y in range(13)]

costos_dir = [-total_nomina[y] for y in range(13)]
util_dir = [ing_netos[y]+costos_dir[y] for y in range(13)]

g_fijos = {k: [base*factor_ipc[y] for y in range(13)] for k,base in costos_fijos_base.items()}
g_percap = {k: [base*factor_ipc[y]*total_alumnos[y] for y in range(13)] for k,base in costos_percapita_base.items()}
arrend_eq = [cp_arrend_equipo*factor_ipc[y]*total_hc[y] for y in range(13)]
imp_oper = [imp_oper_base*factor_ipc[y] for y in range(13)]
opex_ini = [0.0]*13; opex_ini[0]=opex_ini_a0; opex_ini[1]=opex_ini_a1

tot_g_fijos = [sum(g_fijos[k][y] for k in g_fijos) for y in range(13)]
tot_g_percap = [sum(g_percap[k][y] for k in g_percap) for y in range(13)]
tot_gastos_op = [-(tot_g_fijos[y]+tot_g_percap[y]+arrend_eq[y]+imp_oper[y]) for y in range(13)]

amort_e1=[0.0]*13; amort_e2=[0.0]*13; dep_mob=[0.0]*13; dep_eq=[0.0]*13
for y in range(1,13):
    if y<=vida_util_adec: amort_e1[y]=inv_adec_e1/vida_util_adec
    if y<=vida_util_adec: amort_e2[y]=inv_adec_e2/vida_util_adec
    if y<=vida_util_mob: dep_mob[y]=inv_mobiliario/vida_util_mob
    if y<=vida_util_eq: dep_eq[y]=inv_equipos/vida_util_eq

tot_dep_op = [amort_e1[y]+amort_e2[y]+dep_mob[y] for y in range(13)]
tot_dep_adm = [dep_eq[y] for y in range(13)]
tot_dep = [tot_dep_op[y]+tot_dep_adm[y] for y in range(13)]

util_bruta = [util_dir[y]+tot_gastos_op[y]-tot_dep_op[y]-opex_ini[y] for y in range(13)]

pct_asig = [total_alumnos[y]/est_red[y] if est_red[y]>0 else 0 for y in range(13)]
tot_rc = [(rc_laborales[y]+rc_honorarios[y]+rc_iva[y])*pct_asig[y] for y in range(13)]
g_admin_rc = [-tot_rc[y] for y in range(13)]

util_oper = [util_bruta[y]+g_admin_rc[y]-tot_dep_adm[y] for y in range(13)]
ebitda = [util_oper[y]+tot_dep[y] for y in range(13)]

caf_ing = [caf_ingreso_base*factor_ipc[y]*total_alumnos[y] for y in range(13)]
transp_ing = [transp_ingreso_base*factor_ipc[y]*total_alumnos[y]*transp_pen[y] for y in range(13)]
extra_ing = [extra_ingreso_base*factor_ipc[y]*total_alumnos[y]*extra_pen[y] for y in range(13)]
contrib_nc = [caf_ing[y]*(1-caf_costo_pct)+transp_ing[y]*(1-transp_costo_pct)+extra_ing[y]*(1-extra_costo_pct) for y in range(13)]

util_ai = [util_oper[y]+contrib_nc[y] for y in range(13)]
imp_renta = [-util_ai[y]*tasa_impuesto if util_ai[y]>0 else 0 for y in range(13)]
util_neta = [util_ai[y]+imp_renta[y] for y in range(13)]

# BALANCE
cxc = [ing_netos[y]*(dias_cxc/360) if ing_netos[y]>0 else 0 for y in range(13)]
adec_bruta = [inv_adec_e1]+[inv_adec_e1+inv_adec_e2]*12
amort_acum = [0.0]*13
for y in range(1,13): amort_acum[y]=amort_acum[y-1]+amort_e1[y]+amort_e2[y]
mob_eq_bruto = inv_mobiliario+inv_equipos
dep_acum_me = [0.0]*13
for y in range(1,13): dep_acum_me[y]=dep_acum_me[y-1]+dep_mob[y]+dep_eq[y]
capex_acum = [0.0]*13
for y in range(1,13): capex_acum[y]=capex_acum[y-1]+(ing_netos[y]*capex_repo_pct if ing_netos[y]>0 else 0)
act_no_corr = [adec_bruta[y]-amort_acum[y]+mob_eq_bruto-dep_acum_me[y]+capex_acum[y] for y in range(13)]

cxp = [(abs(tot_gastos_op[y])+total_nomina[y]+abs(g_admin_rc[y]))/12 for y in range(13)]
imp_pp = [abs(imp_renta[y])/4 if imp_renta[y]<0 else 0 for y in range(13)]
tot_pas = [cxp[y]+imp_pp[y] for y in range(13)]

ut_ret = [0.0]*13; ut_ret[0]=util_neta[0]
for y in range(1,13): ut_ret[y]=ut_ret[y-1]+util_neta[y]
tot_pat = [capital_inicial+ut_ret[y] for y in range(13)]

caja = [(tot_pas[y]+tot_pat[y])-(cxc[y]+act_no_corr[y]) for y in range(13)]
act_corr = [caja[y]+cxc[y] for y in range(13)]
tot_act = [act_corr[y]+act_no_corr[y] for y in range(13)]
check_bal = [round(tot_act[y]-tot_pas[y]-tot_pat[y],2) for y in range(13)]

# FLUJO DE CAJA
d_cxc=[0.0]*13; d_cxp=[0.0]*13; d_imp=[0.0]*13
d_cxp[0]=cxp[0]
for y in range(1,13):
    d_cxc[y]=-(cxc[y]-cxc[y-1]); d_cxp[y]=cxp[y]-cxp[y-1]; d_imp[y]=imp_pp[y]-imp_pp[y-1]

fl_op = [util_neta[y]+tot_dep[y]+d_cxc[y]+d_cxp[y]+d_imp[y] for y in range(13)]

inv_e1=[0.0]*13; inv_e2=[0.0]*13; inv_me=[0.0]*13; capex_r=[0.0]*13
inv_e1[0]=-inv_adec_e1; inv_e2[1]=-inv_adec_e2; inv_me[0]=-(inv_mobiliario+inv_equipos)
for y in range(1,13): capex_r[y]=-(ing_netos[y]*capex_repo_pct if ing_netos[y]>0 else 0)
fl_inv = [inv_e1[y]+inv_e2[y]+inv_me[y]+capex_r[y] for y in range(13)]

fl_fin = [0.0]*13; fl_fin[0]=capital_inicial
fl_neto = [fl_op[y]+fl_inv[y]+fl_fin[y] for y in range(13)]
caja_ini=[0.0]*13; caja_fin=[0.0]*13; caja_fin[0]=fl_neto[0]
for y in range(1,13): caja_ini[y]=caja_fin[y-1]; caja_fin[y]=caja_ini[y]+fl_neto[y]
check_fc = [round(caja_fin[y]-caja[y],0) for y in range(13)]

fcf = [fl_op[y]+fl_inv[y] for y in range(13)]

# VALORACIÓN
vt_a12 = fcf[12]*(1+gradiente_g)/(wacc-gradiente_g) if wacc>gradiente_g else 0
fcf_vt = fcf[:]; fcf_vt[12]=fcf[12]+vt_a12
fcf_desc = [fcf_vt[y]/(1+wacc)**y for y in range(13)]
fcf_desc_acum = [0.0]*13; fcf_desc_acum[0]=fcf_desc[0]
for y in range(1,13): fcf_desc_acum[y]=fcf_desc_acum[y-1]+fcf_desc[y]
vpn_perp = fcf_desc_acum[12]

vpn_sin_vt = sum(fcf[y]/(1+wacc)**y for y in range(11))
vt_a10 = fcf[10]*(1+gradiente_g)/(wacc-gradiente_g) if wacc>gradiente_g else 0
vpn_con_vt10 = vpn_sin_vt+vt_a10/(1+wacc)**10

try:
    from scipy.optimize import brentq
    def npv_f(r,flows): return sum(f/(1+r)**t for t,f in enumerate(flows))
    tir_sin = brentq(npv_f,-0.5,5.0,args=([fcf[y] for y in range(11)],))
    fcf_10vt = [fcf[y] for y in range(11)]; fcf_10vt[10]+=vt_a10
    tir_con = brentq(npv_f,-0.5,5.0,args=(fcf_10vt,))
except: tir_sin=None; tir_con=None

fcf_acum=[0.0]*13; fcf_acum[0]=fcf[0]
for y in range(1,13): fcf_acum[y]=fcf_acum[y-1]+fcf[y]
pb_s = next((y for y in range(13) if fcf_acum[y]>0), "N/A")
pb_d = next((y for y in range(13) if fcf_desc_acum[y]>0), "N/A")

marg_dir = [util_dir[y]/ing_netos[y] if ing_netos[y]!=0 else 0 for y in range(13)]
marg_bru = [util_bruta[y]/ing_netos[y] if ing_netos[y]!=0 else 0 for y in range(13)]
marg_op = [util_oper[y]/ing_netos[y] if ing_netos[y]!=0 else 0 for y in range(13)]
marg_ebi = [ebitda[y]/ing_netos[y] if ing_netos[y]!=0 else 0 for y in range(13)]
marg_net = [util_neta[y]/ing_netos[y] if ing_netos[y]!=0 else 0 for y in range(13)]
roe = [util_neta[y]/tot_pat[y] if tot_pat[y]!=0 else 0 for y in range(13)]
roa = [util_neta[y]/tot_act[y] if tot_act[y]!=0 else 0 for y in range(13)]

# ═══════════════════════════════════════════════════════════════════
# HELPERS DE FORMATO
# ═══════════════════════════════════════════════════════════════════

def fm(v):
    if isinstance(v,str): return v
    if v==0: return "-"
    return f"{v/1e6:,.1f}"

def fp(v):
    if v==0: return "-"
    return f"{v*100:.1f}%"

def mk_df(rows):
    d={}
    for lbl,vals in rows.items():
        d[lbl]=[fm(v) if not isinstance(v,str) else v for v in vals]
    return pd.DataFrame(d, index=LABELS).T

# ═══════════════════════════════════════════════════════════════════
# VISUALIZACIÓN — 6 TABS
# ═══════════════════════════════════════════════════════════════════

tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs(["📊 Estado de Resultados","📋 Balance General",
    "💰 Flujo de Caja & Perpetuidad","📈 Indicadores & Valoración","🎯 Supuestos",
    "📄 Exportar Reporte"])

with tab1:
    st.subheader("Estado de Resultados (COP Millones)")
    edr = {
        "Ingresos Matrícula": ing_mat, "Ingresos Pensiones": ing_pen,
        "**Total Ingresos Académicos**": total_ing,
        "(-) Provisión Morosidad": prov_mor,
        "**INGRESOS NETOS**": ing_netos, "": [""]*13,
        "Total Costos Directos": costos_dir,
        "**UTILIDAD DIRECTA**": util_dir, " ": [""]*13,
        "Total Gastos Operación": tot_gastos_op,
        "Depreciación Operativa": [-tot_dep_op[y] for y in range(13)],
        "OPEX Inicial": [-opex_ini[y] for y in range(13)],
        "**UTILIDAD BRUTA**": util_bruta, "  ": [""]*13,
        "Gastos Admin (RC)": g_admin_rc,
        "Depreciación Admin": [-tot_dep_adm[y] for y in range(13)],
        "**UTILIDAD OPERATIVA**": util_oper,
        "**EBITDA**": ebitda, "   ": [""]*13,
        "Contrib. Neg. Complementarios": contrib_nc,
        "**UTIL. ANTES IMPUESTOS**": util_ai,
        "Impuesto de Renta": imp_renta,
        "**UTILIDAD NETA**": util_neta,
    }
    st.dataframe(mk_df(edr), use_container_width=True, height=700)
    st.subheader("Evolución de Márgenes")
    fig=go.Figure()
    for n,d in [("Directo",marg_dir),("Bruto",marg_bru),("Operativo",marg_op),("EBITDA",marg_ebi),("Neto",marg_net)]:
        fig.add_trace(go.Scatter(x=LABELS[1:],y=[v*100 for v in d[1:]],name=n,mode="lines+markers"))
    fig.update_layout(yaxis_title="%",height=400)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Balance General (COP Millones)")
    bg = {
        "Caja y Equivalentes": caja, "Cuentas por Cobrar": cxc,
        "**Total Activo Corriente**": act_corr, "": [""]*13,
        "Adecuación Neta": [adec_bruta[y]-amort_acum[y] for y in range(13)],
        "Mob. y Equipos Neto": [mob_eq_bruto-dep_acum_me[y] for y in range(13)],
        "Fondo CAPEX": capex_acum,
        "**Total Activo No Corriente**": act_no_corr,
        "**TOTAL ACTIVOS**": tot_act, " ": [""]*13,
        "Cuentas por Pagar": cxp, "Impuestos por Pagar": imp_pp,
        "**Total Pasivos**": tot_pas, "  ": [""]*13,
        "Capital Social": [capital_inicial]*13,
        "Utilidades Retenidas": ut_ret,
        "**Total Patrimonio**": tot_pat, "   ": [""]*13,
        "**TOTAL P + P**": [tot_pas[y]+tot_pat[y] for y in range(13)],
        "Check": check_bal,
    }
    st.dataframe(mk_df(bg), use_container_width=True, height=600)
    if all(abs(c)<1 for c in check_bal):
        st.success("✅ Balance cuadra en todos los años")
    else:
        st.error("❌ Balance NO cuadra")

with tab3:
    st.subheader("Flujo de Caja (COP Millones)")
    fc = {
        "Utilidad Neta": util_neta,
        "(+) Depreciación": tot_dep,
        "Δ CxC": d_cxc, "Δ CxP": d_cxp, "Δ Imp. por Pagar": d_imp,
        "**Flujo Operativo**": fl_op, "": [""]*13,
        "Inv. Adecuación E1": inv_e1, "Inv. Adecuación E2": inv_e2,
        "Inv. Mob. y Equipos": inv_me, "CAPEX Reposición": capex_r,
        "**Flujo Inversión**": fl_inv, " ": [""]*13,
        "Aporte Capital": fl_fin,
        "**Flujo Financiamiento**": fl_fin, "  ": [""]*13,
        "**FLUJO NETO**": fl_neto,
        "Caja Inicial": caja_ini, "**CAJA FINAL**": caja_fin,
        "Check vs Balance": check_fc,
    }
    st.dataframe(mk_df(fc), use_container_width=True, height=600)
    st.markdown("---")
    st.subheader("🔄 Perpetuidad y Valoración del FCF")
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("FCF Año 12", f"${fcf[12]/1e6:,.0f}M")
    with c2: st.metric("Valor Terminal (Perp. Año 12)", f"${vt_a12/1e6:,.0f}M")
    with c3: st.metric("FCF+VT Año 12", f"${(fcf[12]+vt_a12)/1e6:,.0f}M")
    perp = {
        "FCF Anual": fcf, "Valor Terminal": [0]*12+[vt_a12],
        "**FCF + VT**": fcf_vt, "": [""]*13,
        "FCF Descontado": fcf_desc, "FCF Desc. Acumulado": fcf_desc_acum,
    }
    st.dataframe(mk_df(perp), use_container_width=True, height=250)
    fig2=go.Figure()
    fig2.add_trace(go.Bar(x=LABELS,y=[f/1e6 for f in fcf],name="FCF Anual",marker_color="steelblue"))
    fig2.add_trace(go.Scatter(x=LABELS,y=[f/1e6 for f in fcf_acum],name="FCF Acumulado",
                              mode="lines+markers",line=dict(color="orange",width=2)))
    fig2.update_layout(title="Free Cash Flow (COP Millones)",yaxis_title="COP M",height=400)
    st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.subheader("Indicadores y Valoración")
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("VPN (Perp. 0-12+VT)", f"${vpn_perp/1e6:,.0f}M")
    with c2: st.metric("VPN (con VT, 10yr)", f"${vpn_con_vt10/1e6:,.0f}M")
    with c3: st.metric("TIR (sin VT)", f"{tir_sin*100:.1f}%" if tir_sin else "N/A")
    with c4: st.metric("TIR (con VT)", f"{tir_con*100:.1f}%" if tir_con else "N/A")
    c5,c6,c7,c8 = st.columns(4)
    with c5: st.metric("Payback Simple", f"{pb_s} años" if isinstance(pb_s,int) else pb_s)
    with c6: st.metric("Payback Descontado", f"{pb_d} años" if isinstance(pb_d,int) else pb_d)
    with c7: st.metric("WACC", f"{wacc*100:.1f}%")
    with c8: st.metric("Gradiente (g)", f"{gradiente_g*100:.1f}%")
    st.markdown("---")
    st.subheader("Indicadores Operativos")
    io = {"Total Alumnos": total_alumnos, "Capacidad Máxima": capacidad_max,
          "Ocupación": [fp(v) for v in tasa_ocupacion], "Headcount": total_hc, "Grupos": grupos_totales}
    st.dataframe(pd.DataFrame(io,index=LABELS).T, use_container_width=True, height=200)
    st.subheader("Indicadores de Rentabilidad")
    ir = {"Margen Directo": [fp(v) for v in marg_dir], "Margen Bruto": [fp(v) for v in marg_bru],
          "Margen Operativo": [fp(v) for v in marg_op], "Margen EBITDA": [fp(v) for v in marg_ebi],
          "Margen Neto": [fp(v) for v in marg_net], "ROE": [fp(v) for v in roe], "ROA": [fp(v) for v in roa]}
    st.dataframe(pd.DataFrame(ir,index=LABELS).T, use_container_width=True, height=280)
    fig3=go.Figure()
    fig3.add_trace(go.Scatter(x=LABELS[1:],y=[roe[y]*100 for y in range(1,13)],name="ROE",mode="lines+markers"))
    fig3.add_trace(go.Scatter(x=LABELS[1:],y=[roa[y]*100 for y in range(1,13)],name="ROA",mode="lines+markers"))
    fig3.update_layout(title="ROE y ROA (%)",yaxis_title="%",height=350)
    st.plotly_chart(fig3, use_container_width=True)
    st.subheader("Detalle de Valoración")
    vd = pd.DataFrame({
        "Métrica": ["VPN (sin VT, 10yr)","VT Año 10 (desc.)","VPN (con VT, 10yr)",
                    "VPN (Perpetuidad, Año 0-12 + VT)","VT Año 12 (nominal)",
                    "TIR (sin VT)","TIR (con VT)","Payback Simple","Payback Descontado"],
        "Valor": [f"${vpn_sin_vt/1e6:,.0f}M", f"${vt_a10/(1+wacc)**10/1e6:,.0f}M",
                  f"${vpn_con_vt10/1e6:,.0f}M", f"${vpn_perp/1e6:,.0f}M", f"${vt_a12/1e6:,.0f}M",
                  f"{tir_sin*100:.1f}%" if tir_sin else "N/A",
                  f"{tir_con*100:.1f}%" if tir_con else "N/A",
                  f"{pb_s} años" if isinstance(pb_s,int) else pb_s,
                  f"{pb_d} años" if isinstance(pb_d,int) else pb_d]
    }).set_index("Métrica")
    st.table(vd)

with tab5:
    st.subheader("Resumen de Supuestos")
    ca,cb = st.columns(2)
    with ca:
        st.markdown("**Infraestructura**")
        st.write(f"- Área: {area_total:,} m² | Salones: {salones_fisicos}")
        st.write(f"- Jornada: {'Doble' if grupos_por_salon==2 else 'Única'}")
        st.write(f"- Inversión Total: ${inv_total_adec/1e6:,.0f}M")
        st.markdown("**Capacidad Año 1**")
        st.write(f"- Cap: {capacidad_max[1]:,} | Al: {total_alumnos[1]:,} | Ocup: {tasa_ocupacion[1]*100:.0f}%")
    with cb:
        st.markdown("**Financieros**")
        st.write(f"- Capital: ${capital_inicial/1e6:,.0f}M | WACC: {wacc*100:.1f}% | g: {gradiente_g*100:.1f}%")
        st.write(f"- Impuesto: {tasa_impuesto*100:.0f}% | Días CxC: {dias_cxc}")
        st.markdown("**Tarifas Año 0**")
        st.write(f"- Matrícula: ${matricula_base:,.0f} | Pensión: ${pension_base:,.0f}")
    st.markdown("---")
    st.markdown("**Headcount por Rol**")
    st.dataframe(pd.DataFrame(hc,index=LABELS).T, use_container_width=True, height=300)

# ═══════════════════════════════════════════════════════════════════
# TAB 6 — EXPORTAR REPORTE PDF
# ═══════════════════════════════════════════════════════════════════

with tab6:
    st.subheader("📄 Exportar Reporte PDF")
    st.markdown("Genera un PDF con todos los estados financieros, indicadores, supuestos y valoración.")

    nombre_colegio = st.text_input("Nombre del Colegio (para el reporte)", "Colegio Tipo")
    fecha_reporte = st.date_input("Fecha del Reporte")

    if st.button("🖨️ Generar Reporte PDF", type="primary", use_container_width=True):
        try:
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.lib import colors
            from reportlab.lib.units import inch, cm
            from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                Paragraph, Spacer, PageBreak, HRFlowable)
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

            buf = BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=landscape(letter),
                leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=2*cm, bottomMargin=2*cm)

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
                fontSize=20, spaceAfter=6, textColor=colors.HexColor("#1a3c6e"))
            subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'],
                fontSize=14, spaceAfter=4, textColor=colors.HexColor("#2c5f8a"))
            section_style = ParagraphStyle('Section', parent=styles['Heading3'],
                fontSize=11, spaceAfter=4, textColor=colors.HexColor("#333333"),
                spaceBefore=10)
            normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                fontSize=8, leading=10)
            small_style = ParagraphStyle('Small', parent=styles['Normal'],
                fontSize=7, leading=9)
            right_style = ParagraphStyle('Right', parent=small_style, alignment=TA_RIGHT)
            bold_style = ParagraphStyle('Bold', parent=small_style,
                fontName='Helvetica-Bold')

            elements = []

            # --- PORTADA ---
            elements.append(Spacer(1, 2*inch))
            elements.append(Paragraph(f"MODELO FINANCIERO", title_style))
            elements.append(Paragraph(f"{nombre_colegio.upper()}", title_style))
            elements.append(Spacer(1, 0.3*inch))
            elements.append(HRFlowable(width="60%", thickness=2, color=colors.HexColor("#1a3c6e")))
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph(f"Proyección a 12 Años con Perpetuidad", subtitle_style))
            elements.append(Paragraph(f"Jornada: {'Doble' if grupos_por_salon==2 else 'Única'} | "
                f"Capital: ${capital_inicial/1e6:,.0f}M | WACC: {wacc*100:.1f}%", normal_style))
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph(f"Fecha: {fecha_reporte.strftime('%d/%m/%Y')}", normal_style))
            elements.append(Paragraph("Generado automáticamente — Modelo Financiero Colegio Tipo v2.0", small_style))
            elements.append(PageBreak())

            # --- HELPER PARA TABLAS ---
            header_color = colors.HexColor("#1a3c6e")
            alt_color = colors.HexColor("#f0f4f8")
            bold_bg = colors.HexColor("#e8eef5")

            def build_table(title, row_labels, data_rows, bold_rows=None, fmt_func=fm):
                if bold_rows is None: bold_rows = set()
                elements.append(Paragraph(title, subtitle_style))
                elements.append(Spacer(1, 0.1*inch))
                header = [""] + LABELS
                table_data = [header]
                for i, (label, vals) in enumerate(zip(row_labels, data_rows)):
                    row = [Paragraph(f"<b>{label}</b>" if i in bold_rows else label, small_style)]
                    for v in vals:
                        if isinstance(v, str) and v == "":
                            row.append("")
                        else:
                            row.append(Paragraph(fmt_func(v) if not isinstance(v,str) else v, right_style))
                    table_data.append(row)

                col_w = [2.2*cm] + [1.65*cm]*13
                t = Table(table_data, colWidths=col_w, repeatRows=1)
                style_cmds = [
                    ('BACKGROUND', (0,0), (-1,0), header_color),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 6.5),
                    ('FONTSIZE', (0,0), (-1,0), 7),
                    ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
                    ('ALIGN', (0,0), (0,-1), 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
                    ('TOPPADDING', (0,0), (-1,-1), 2),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ]
                for i in range(1, len(table_data)):
                    if (i-1) in bold_rows:
                        style_cmds.append(('BACKGROUND', (0,i), (-1,i), bold_bg))
                        style_cmds.append(('FONTNAME', (0,i), (-1,i), 'Helvetica-Bold'))
                    elif i % 2 == 0:
                        style_cmds.append(('BACKGROUND', (0,i), (-1,i), alt_color))
                t.setStyle(TableStyle(style_cmds))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))

            # --- SUPUESTOS CLAVE ---
            elements.append(Paragraph("1. SUPUESTOS PRINCIPALES", subtitle_style))
            elements.append(Spacer(1, 0.1*inch))
            sup_data = [
                ["Jornada", f"{'Doble (2 grupos/salón)' if grupos_por_salon==2 else 'Única (1 grupo/salón)'}",
                 "Capital Inicial", f"${capital_inicial/1e6:,.0f}M"],
                ["Área Total", f"{area_total:,} m²", "WACC", f"{wacc*100:.1f}%"],
                ["Salones Totales", f"{salones_fisicos}", "Gradiente (g)", f"{gradiente_g*100:.1f}%"],
                ["Inversión Total", f"${inv_total_adec/1e6:,.0f}M", "Tasa Impuesto", f"{tasa_impuesto*100:.0f}%"],
                ["Alumnos/Grupo", f"{alumnos_por_grupo}", "Días CxC", f"{dias_cxc}"],
                ["Matrícula Base", f"${matricula_base:,.0f}", "CAPEX Repos.", f"{capex_repo_pct*100:.1f}%"],
                ["Pensión Base", f"${pension_base:,.0f}", "Meses Pensión", f"{meses_pension}"],
                ["Vida Útil Adec.", f"{vida_util_adec} años", "Vida Útil Mob.", f"{vida_util_mob} años"],
            ]
            sup_t = Table(sup_data, colWidths=[4*cm, 4.5*cm, 4*cm, 4.5*cm])
            sup_t.setStyle(TableStyle([
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
                ('BACKGROUND', (0,0), (0,-1), alt_color),
                ('BACKGROUND', (2,0), (2,-1), alt_color),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            elements.append(sup_t)

            # Salarios
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph("Salarios Base Mensuales (2026)", section_style))
            sal_data = [["Rol", "Salario Base", "Aux. Transp.", "Costo Anual"]]
            for name, sal, aux in roles_info:
                cm_val = sal*(1+factor_prestacional)+(aux_transporte if aux else 0)
                sal_data.append([name, f"${sal:,.0f}", "Sí" if aux else "No", f"${cm_val*meses_laborados:,.0f}"])
            sal_t = Table(sal_data, colWidths=[4*cm, 3.5*cm, 2.5*cm, 4*cm])
            sal_t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), header_color),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 7.5),
                ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
            ]))
            elements.append(sal_t)

            # IPC y Tarifas
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph("Supuestos Macroeconómicos", section_style))
            macro_labels = ["IPC Proyectado", "Incremento Tarifas"]
            macro_data = [ipc, incr_tarifa]
            build_table("", macro_labels, macro_data, fmt_func=lambda v: fp(v) if not isinstance(v,str) else v)

            elements.append(PageBreak())

            # --- ESTADO DE RESULTADOS ---
            edr_labels = ["Ingresos Matrícula","Ingresos Pensiones","Total Ingresos Académicos",
                "(-) Provisión Morosidad","INGRESOS NETOS","","Total Costos Directos",
                "UTILIDAD DIRECTA","","Total Gastos Operación","Depreciación Operativa",
                "OPEX Inicial","UTILIDAD BRUTA","","Gastos Admin (RC)","Depreciación Admin",
                "UTILIDAD OPERATIVA","EBITDA","","Contrib. Neg. Complementarios",
                "UTIL. ANTES IMPUESTOS","Impuesto de Renta","UTILIDAD NETA"]
            edr_data = [ing_mat, ing_pen, total_ing, prov_mor, ing_netos, [""]*13,
                costos_dir, util_dir, [""]*13, tot_gastos_op,
                [-tot_dep_op[y] for y in range(13)], [-opex_ini[y] for y in range(13)],
                util_bruta, [""]*13, g_admin_rc, [-tot_dep_adm[y] for y in range(13)],
                util_oper, ebitda, [""]*13, contrib_nc, util_ai, imp_renta, util_neta]
            edr_bold = {2,4,7,12,16,17,20,22}
            build_table("2. ESTADO DE RESULTADOS (COP Millones)", edr_labels, edr_data, edr_bold)
            elements.append(PageBreak())

            # --- BALANCE GENERAL ---
            bg_labels = ["Caja y Equivalentes","Cuentas por Cobrar","Total Activo Corriente","",
                "Adecuación Neta","Mob. y Equipos Neto","Fondo CAPEX",
                "Total Activo No Corriente","TOTAL ACTIVOS","",
                "Cuentas por Pagar","Impuestos por Pagar","Total Pasivos","",
                "Capital Social","Utilidades Retenidas","Total Patrimonio","",
                "TOTAL P + P","Check"]
            bg_data = [caja, cxc, act_corr, [""]*13,
                [adec_bruta[y]-amort_acum[y] for y in range(13)],
                [mob_eq_bruto-dep_acum_me[y] for y in range(13)], capex_acum,
                act_no_corr, tot_act, [""]*13,
                cxp, imp_pp, tot_pas, [""]*13,
                [capital_inicial]*13, ut_ret, tot_pat, [""]*13,
                [tot_pas[y]+tot_pat[y] for y in range(13)], check_bal]
            bg_bold = {2,7,8,12,16,18,19}
            build_table("3. BALANCE GENERAL (COP Millones)", bg_labels, bg_data, bg_bold)
            elements.append(PageBreak())

            # --- FLUJO DE CAJA ---
            fc_labels = ["Utilidad Neta","(+) Depreciación","Δ CxC","Δ CxP","Δ Imp. por Pagar",
                "Flujo Operativo","","Inv. Adec. E1","Inv. Adec. E2","Inv. Mob. y Eq.",
                "CAPEX Reposición","Flujo Inversión","","Aporte Capital","Flujo Financiamiento",
                "","FLUJO NETO","Caja Inicial","CAJA FINAL"]
            fc_data = [util_neta, tot_dep, d_cxc, d_cxp, d_imp, fl_op, [""]*13,
                inv_e1, inv_e2, inv_me, capex_r, fl_inv, [""]*13,
                fl_fin, fl_fin, [""]*13, fl_neto, caja_ini, caja_fin]
            fc_bold = {5,11,14,16,18}
            build_table("4. FLUJO DE CAJA (COP Millones)", fc_labels, fc_data, fc_bold)

            # Perpetuidad
            elements.append(Spacer(1, 0.2*inch))
            perp_labels = ["FCF Anual","Valor Terminal","FCF + VT","",
                "FCF Descontado","FCF Desc. Acumulado"]
            perp_data = [fcf, [0]*12+[vt_a12], fcf_vt, [""]*13, fcf_desc, fcf_desc_acum]
            perp_bold = {2,5}
            build_table("5. PERPETUIDAD Y FCF DESCONTADO (COP Millones)", perp_labels, perp_data, perp_bold)
            elements.append(PageBreak())

            # --- VALORACIÓN ---
            elements.append(Paragraph("6. RESULTADOS DE VALORACIÓN", subtitle_style))
            elements.append(Spacer(1, 0.15*inch))
            val_data = [
                ["Métrica", "Valor"],
                ["VPN (sin Valor Terminal, 10 años)", f"${vpn_sin_vt/1e6:,.0f}M"],
                ["Valor Terminal Año 10 (descontado)", f"${vt_a10/(1+wacc)**10/1e6:,.0f}M"],
                ["VPN (con VT, horizonte 10 años)", f"${vpn_con_vt10/1e6:,.0f}M"],
                ["VPN (Perpetuidad, Año 0-12 + VT)", f"${vpn_perp/1e6:,.0f}M"],
                ["Valor Terminal Año 12 (nominal)", f"${vt_a12/1e6:,.0f}M"],
                ["TIR (sin Valor Terminal)", f"{tir_sin*100:.1f}%" if tir_sin else "N/A"],
                ["TIR (con Valor Terminal)", f"{tir_con*100:.1f}%" if tir_con else "N/A"],
                ["Payback Simple", f"{pb_s} años" if isinstance(pb_s,int) else str(pb_s)],
                ["Payback Descontado", f"{pb_d} años" if isinstance(pb_d,int) else str(pb_d)],
            ]
            val_t = Table(val_data, colWidths=[8*cm, 5*cm])
            val_t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), header_color),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('ALIGN', (1,1), (1,-1), 'RIGHT'),
                ('FONTNAME', (1,1), (1,-1), 'Helvetica-Bold'),
            ]))
            for i in range(1, len(val_data)):
                if i % 2 == 0:
                    val_t.setStyle(TableStyle([('BACKGROUND', (0,i), (-1,i), alt_color)]))
            elements.append(val_t)

            # Indicadores
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("7. INDICADORES DE RENTABILIDAD", subtitle_style))
            ind_labels = ["Margen Directo","Margen Bruto","Margen Operativo",
                "Margen EBITDA","Margen Neto","ROE","ROA"]
            ind_data = [marg_dir, marg_bru, marg_op, marg_ebi, marg_net, roe, roa]
            build_table("", ind_labels, ind_data, fmt_func=lambda v: fp(v) if not isinstance(v,str) else v)

            # Operativos
            elements.append(Paragraph("8. INDICADORES OPERATIVOS", subtitle_style))
            op_labels = ["Total Alumnos","Capacidad Máxima","Ocupación","Headcount","Grupos"]
            op_data = [total_alumnos, capacidad_max, tasa_ocupacion, total_hc, grupos_totales]
            def op_fmt(v):
                if isinstance(v, str): return v
                if isinstance(v, float) and v < 1: return fp(v)
                if v == 0: return "-"
                return f"{v:,.0f}"
            build_table("", op_labels, op_data, fmt_func=op_fmt)

            # Pie de página
            elements.append(Spacer(1, 0.5*inch))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(
                f"Reporte generado el {fecha_reporte.strftime('%d/%m/%Y')} — "
                f"Modelo Financiero {nombre_colegio} — Proyección 12 años con perpetuidad",
                ParagraphStyle('Footer', parent=small_style, textColor=colors.HexColor("#888888"),
                    alignment=TA_CENTER)))

            doc.build(elements)
            pdf_bytes = buf.getvalue()
            buf.close()

            st.success(f"✅ Reporte generado exitosamente ({len(pdf_bytes)/1024:.0f} KB)")
            st.download_button(
                label="⬇️ Descargar Reporte PDF",
                data=pdf_bytes,
                file_name=f"Reporte_{nombre_colegio.replace(' ','_')}_{fecha_reporte.strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

        except ImportError:
            st.error("⚠️ Se requiere la librería `reportlab`. Instálala con:")
            st.code("pip install reportlab", language="bash")
        except Exception as e:
            st.error(f"Error generando PDF: {e}")
            st.exception(e)

st.sidebar.markdown("---")
st.sidebar.caption("Modelo Financiero Colegio Tipo v2.0 — 12 años + Perpetuidad")