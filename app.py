import streamlit as st
from etl_manager import load_exceptions_data
from view_retrasos import render_vista_retrasos
from view_paradas import render_vista_paradas
from view_retrasos import render_tabla_detalle


st.set_page_config(layout="wide")

# Global date picker for 'hoy'
if 'fecha_hoy' not in st.session_state:
    st.session_state['fecha_hoy'] = None
st.session_state['fecha_hoy'] = st.date_input(
    "Selecciona la fecha de 'hoy' para el cálculo de retrasos",
    value=st.session_state['fecha_hoy'] or None,
    key='fecha_hoy_input'
)

# Inicializar session_state
if 'selected_partner' not in st.session_state:
    st.session_state.selected_partner = None
if 'selected_region' not in st.session_state:
    st.session_state.selected_region = None
if 'selected_reason' not in st.session_state:
    st.session_state.selected_reason = None

# Cargar datos
df_exceptions = load_exceptions_data("datamart.sqlite")


# Tabs
tab1, tab2, tab3 = st.tabs(["Retrasos", "Paradas", "Detalle"])

# Pass fecha_hoy in session_state to all views
with tab1:
    render_vista_retrasos(df_exceptions, st.session_state)

with tab2:
    render_vista_paradas(df_exceptions, st.session_state)

with tab3:
    render_tabla_detalle(df_exceptions, st.session_state)
