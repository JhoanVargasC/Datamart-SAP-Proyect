"""
Vista de Retrasos - Dashboard Optimizado para Día a Día
Enfoque: Registros activos, gestión móvil y acciones inmediatas
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta


def render_vista_retrasos(df_filtrado: pd.DataFrame, session_state: dict):
    """
    Renderiza dashboard de retrasos optimizado para seguimiento día a día.
    
    Args:
        df_filtrado (pd.DataFrame): DataFrame filtrado de proyectos.
        session_state (dict): Estado global de Streamlit.
    """
    st.title("Gestión de Retrasos - Seguimiento Operacional")
    
    df = df_filtrado.copy()
    df = _preparar_columnas(df)
    df_retrasos = df[df['DiasRetraso'] > 0].copy()
    
    if df_retrasos.empty:
        st.warning("No se encontraron proyectos con retrasos.")
        return
    
    # KPIs ejecutivos en una fila
    _render_kpis_compactos(df, df_retrasos)
    
    st.markdown("---")
    
    # Filtros operacionales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filtro_socio = st.selectbox(
            "Socio Implementador",
            options=['Todos'] + sorted(df_retrasos['MainPartner'].unique()),
            key='filtro_socio'
        )
    
    with col2:
        filtro_region = st.selectbox(
            "Región Cliente",
            options=['Todos'] + sorted(df_retrasos['CustomerRegion'].unique()),
            key='filtro_region'
        )
    
    with col3:
        filtro_gravedad = st.selectbox(
            "Nivel de Gravedad",
            options=['Todos', 'Crítico (>31d)', 'Moderado (8-31d)', 'Leve (1-7d)'],
            key='filtro_gravedad'
        )
    
    with col4:
        busqueda = st.text_input("Buscar proyecto", placeholder="Nombre o ID")
    
    # Aplicar filtros
    df_filtrado_vis = _aplicar_filtros_operacionales(
        df_retrasos, filtro_socio, filtro_region, filtro_gravedad, busqueda
    )
    
    if df_filtrado_vis.empty:
        st.info("No hay registros que coincidan con los filtros aplicados.")
        return
    
    # Tabla principal de proyectos activos
    _render_tabla_retrasos_activos(df_filtrado_vis)
    
    st.markdown("---")
    
    # Resumen comparativo
    _render_comparativa_dimensiones(df_retrasos)
    
    st.markdown("---")
    
    # Listado de acciones recomendadas
    _render_acciones_recomendadas(df_retrasos)


def _preparar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara y valida columnas necesarias."""
    
    cols_defaults = {
        'MainPartner': 'No Especificado',
        'CustomerRegion': 'No Especificado',
        'SolutionArea': 'No Especificado',
        'ISS': 'No Especificado',
        'ProjectStatus': 'Unknown',
        'ProjectName': 'Proyecto',
        'ProjectID': '0'
    }
    
    for col, default in cols_defaults.items():
        if col not in df.columns:
            df[col] = default
        df[col] = df[col].fillna(default)
    
    # Recalcular DiasRetraso usando la fecha seleccionada
    from datetime import datetime
    fecha_hoy = st.session_state.get('fecha_hoy', None)
    if fecha_hoy is not None:
        # Si existe columna de fecha de referencia, usarla
        if 'PlannedGoLive' in df.columns:
            df['PlannedGoLive'] = pd.to_datetime(df['PlannedGoLive'], errors='coerce')
            fecha_hoy_dt = pd.to_datetime(fecha_hoy)
            df['DiasRetraso'] = (fecha_hoy_dt - df['PlannedGoLive']).dt.days
            df['DiasRetraso'] = df['DiasRetraso'].fillna(0).astype(int)
        else:
            if 'DiasRetraso' not in df.columns:
                df['DiasRetraso'] = 0
            df['DiasRetraso'] = pd.to_numeric(df['DiasRetraso'], errors='coerce').fillna(0)
    else:
        if 'DiasRetraso' not in df.columns:
            df['DiasRetraso'] = 0
        df['DiasRetraso'] = pd.to_numeric(df['DiasRetraso'], errors='coerce').fillna(0)
    return df


def _render_kpis_compactos(df: pd.DataFrame, df_retrasos: pd.DataFrame):
    """Renderiza KPIs en formato compacto."""
    
    st.subheader("Indicadores Operacionales")
    
    total_proyectos = len(df)
    retrasados = len(df_retrasos)
    tasa = (retrasados / total_proyectos * 100) if total_proyectos > 0 else 0
    dias_prom = df_retrasos['DiasRetraso'].mean()
    criticos = len(df_retrasos[df_retrasos['DiasRetraso'] > 31])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Proyectos Retrasados", f"{retrasados}/{total_proyectos}", f"{tasa:.1f}%")
    
    with col2:
        st.metric("Promedio de Retraso", f"{dias_prom:.0f} días")
    
    with col3:
        st.metric("Críticos (>31d)", f"{criticos}")
    
    with col4:
        top_region = df_retrasos.groupby('CustomerRegion')['DiasRetraso'].sum().idxmax()
        st.metric("Mayor Impacto", top_region[:15])


def _aplicar_filtros_operacionales(
    df: pd.DataFrame, socio: str, region: str, gravedad: str, busqueda: str
) -> pd.DataFrame:
    """Aplica filtros operacionales al dataframe."""
    
    if socio != 'Todos':
        df = df[df['MainPartner'] == socio]
    
    if region != 'Todos':
        df = df[df['CustomerRegion'] == region]
    
    if gravedad != 'Todos':
        if gravedad == 'Crítico (>31d)':
            df = df[df['DiasRetraso'] > 31]
        elif gravedad == 'Moderado (8-31d)':
            df = df[(df['DiasRetraso'] > 7) & (df['DiasRetraso'] <= 31)]
        elif gravedad == 'Leve (1-7d)':
            df = df[df['DiasRetraso'] <= 7]
    
    if busqueda:
        df = df[df['ProjectName'].str.contains(busqueda, case=False, na=False)]
    
    return df.sort_values('DiasRetraso', ascending=False)


def _render_tabla_retrasos_activos(df: pd.DataFrame):
    """Renderiza tabla principal de retrasos."""
    
    st.subheader(f"Proyectos Activos con Retraso ({len(df)} registros)")
    
    # Preparar datos
    df_vista = df[[
        'ProjectName', 'MainPartner', 'CustomerRegion', 
        'DiasRetraso', 'ProjectStatus', 'SolutionArea'
    ]].copy()
    
    df_vista['DiasRetraso'] = df_vista['DiasRetraso'].astype(int)
    df_vista = df_vista.reset_index(drop=True)
    # Ensure columns are unique to avoid Styler.apply KeyError
    df_vista = df_vista.loc[:, ~df_vista.columns.duplicated()]
    
    # Función de coloreado
    def colorear_fila(row):
        dias = row['DiasRetraso']
        if dias > 31:
            return ['background-color: #ffe6e6'] * len(row)
        elif dias > 7:
            return ['background-color: #fff4e6'] * len(row)
        return [''] * len(row)
    
    # Mostrar tabla
    st.dataframe(
        df_vista.style.apply(colorear_fila, axis=1),
        hide_index=True,
        use_container_width=True,
        height=400
    )
    
    # Botón de descarga
    csv = df_vista.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar Reporte CSV",
        data=csv,
        file_name=f"retrasos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def _render_comparativa_dimensiones(df: pd.DataFrame):
    """Renderiza comparativa simple de impacto por dimensión."""
    
    st.subheader("Concentración de Impacto por Dimensión")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Por Socio Implementador**")
        socio_impact = df.groupby('MainPartner').agg({
            'ProjectID': 'count',
            'DiasRetraso': 'sum'
        }).sort_values('DiasRetraso', ascending=False).head(8)
        socio_impact.columns = ['Cantidad', 'Días Acum.']
        st.dataframe(socio_impact, use_container_width=True)
    
    with col2:
        st.markdown("**Por Región del Cliente**")
        region_impact = df.groupby('CustomerRegion').agg({
            'ProjectID': 'count',
            'DiasRetraso': 'sum'
        }).sort_values('DiasRetraso', ascending=False).head(8)
        region_impact.columns = ['Cantidad', 'Días Acum.']
        st.dataframe(region_impact, use_container_width=True)


def _render_acciones_recomendadas(df: pd.DataFrame):
    """Renderiza lista de acciones prioritarias."""
    
    st.subheader("Acciones Prioritarias del Día")
    
    # Top críticos
    criticos = df[df['DiasRetraso'] > 31].nlargest(5, 'DiasRetraso')
    
    if not criticos.empty:
        st.markdown("**Intervención Inmediata (>31 días de retraso)**")
        for idx, row in criticos.iterrows():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.text(f"{row['ProjectName']}")
            with col2:
                st.text(f"{row['MainPartner']} - {row['CustomerRegion']}")
            with col3:
                st.metric("", f"{int(row['DiasRetraso'])}d")
    
    # Casos moderados próximos a crítico
    moderados = df[
        (df['DiasRetraso'] > 15) & (df['DiasRetraso'] <= 31)
    ].nlargest(5, 'DiasRetraso')
    
    if not moderados.empty:
        st.markdown("**Monitoreo de Proximidad (15-31 días)**")
        for idx, row in moderados.iterrows():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.text(f"{row['ProjectName']}")
            with col2:
                st.text(f"{row['MainPartner']} - {row['CustomerRegion']}")
            with col3:
                st.metric("", f"{int(row['DiasRetraso'])}d")


def render_tabla_detalle(df_filtrado: pd.DataFrame, session_state: dict):
    """
    Renderiza tabla detallada con búsqueda y exportación.
    Compatible con otras vistas de Streamlit.
    
    Args:
        df_filtrado (pd.DataFrame): DataFrame filtrado.
        session_state (dict): Estado global.
    """
    st.subheader("Detalle Completo de Retrasos")
    
    df = df_filtrado.copy()
    df = _preparar_columnas(df)
    df = df[df['DiasRetraso'] > 0].copy()
    
    if df.empty:
        st.info("No hay proyectos con retraso para mostrar.")
        return
    
    # Búsqueda y filtros
    col1, col2 = st.columns(2)
    
    with col1:
        busqueda = st.text_input("Buscar por nombre:", placeholder="Ingresa texto")
        if busqueda:
            df = df[df['ProjectName'].str.contains(busqueda, case=False, na=False)]
    
    with col2:
        min_dias = st.number_input("Retraso mínimo (días):", min_value=0, value=0)
        df = df[df['DiasRetraso'] >= min_dias]
    
    df = df.sort_values('DiasRetraso', ascending=False)
    
    # Tabla
    cols_mostrar = ['ProjectName', 'MainPartner', 'CustomerRegion', 
                    'SolutionArea', 'DiasRetraso', 'ProjectStatus']
    
    for col in cols_mostrar:
        if col not in df.columns:
            df[col] = 'N/A'
    
    df_display = df[cols_mostrar].reset_index(drop=True)
    df_display['DiasRetraso'] = df_display['DiasRetraso'].astype(int)
    # Ensure columns are unique to avoid Styler.apply KeyError
    df_display = df_display.loc[:, ~df_display.columns.duplicated()]
    
    # Paginación
    total_rows = len(df_display)
    rows_per_page = 100
    total_pages = max(1, (total_rows - 1) // rows_per_page + 1)
    
    page = st.number_input(
        f"Página (Total: {total_rows} registros)",
        min_value=1,
        max_value=total_pages,
        value=1
    )
    
    start_idx = (page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    df_page = df_display.iloc[start_idx:end_idx]
    
    # Coloreo
    def highlight_severity(row):
        dias = row['DiasRetraso']
        if dias > 31:
            return ['background-color: #ffe6e6'] * len(row)
        elif dias > 7:
            return ['background-color: #fff4e6'] * len(row)
        return [''] * len(row)
    
    st.dataframe(
        df_page.style.apply(highlight_severity, axis=1),
        hide_index=True,
        use_container_width=True,
        height=600
    )
    
    # Exportar
    csv_data = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar Reporte Completo",
        data=csv_data,
        file_name=f"retrasos_detalle_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )