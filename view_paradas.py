"""
Vista Paradas de Proyecto - Dashboard General Optimizado
Diseño ejecutivo con visualizaciones estratégicas y análisis multidimensional
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime


def render_vista_paradas(df: pd.DataFrame, session_state: dict):
    """
    Dashboard ejecutivo de paradas con visualizaciones estratégicas.
    """
    st.title("Dashboard Ejecutivo - Paradas de Proyecto")
    
    df = df.copy()
    
    diagnostico = _diagnosticar_disponibilidad_datos(df)
    
    if diagnostico['faltan_criticas']:
        st.warning(
            f"Columnas críticas no disponibles: {', '.join(diagnostico['faltan_criticas'])}. "
            f"El dashboard funcionará con datos parciales."
        )
    
    with st.expander("Diagnóstico de Disponibilidad de Datos"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Columnas Disponibles**")
            st.caption(f"Total: {len(diagnostico['disponibles'])}")
            for col in sorted(diagnostico['disponibles'])[:20]:
                st.text(f"  {col}")
            if len(diagnostico['disponibles']) > 20:
                st.caption(f"  ... y {len(diagnostico['disponibles']) - 20} más")
        
        with col2:
            st.markdown("**Columnas Faltantes**")
            st.caption(f"Total: {len(diagnostico['faltan_all'])}")
            for col in sorted(diagnostico['faltan_all'])[:20]:
                st.text(f"  {col}")
            if len(diagnostico['faltan_all']) > 20:
                st.caption(f"  ... y {len(diagnostico['faltan_all']) - 20} más")
    
    df = _preparar_datos_robustos(df)
    
    if df.empty:
        st.error("No hay datos disponibles para procesar después de la validación.")
        return
    
    _render_kpis_ejecutivos(df, session_state)
    
    st.divider()
    
    df_filtrado = _aplicar_filtros_avanzados(df)
    
    if df_filtrado.empty:
        st.info("No hay datos que coincidan con los filtros seleccionados.")
        return
    
    st.divider()
    
    _render_analisis_distribucion(df_filtrado)
    
    st.divider()
    
    _render_analisis_temporal(df_filtrado)
    
    st.divider()
    
    _render_matriz_impacto(df_filtrado)
    
    st.divider()
    
    _render_analisis_comparativo(df_filtrado)
    
    st.divider()
    
    _render_tablas_detalle(df_filtrado)


def _diagnosticar_disponibilidad_datos(df: pd.DataFrame) -> dict:
    """Diagnostica disponibilidad de columnas esperadas."""
    
    columnas_esperadas = {
        'criticas': [
            'ProjectID', 'ProjectName', 'CustomerRegion', 
            'ProjectStatus_Flag', 'DiasRetraso'
        ],
        'temporales': ['Año', 'Trimestre', 'Mes', 'FechaActualizacion'],
        'detalle': [
            'CriticalityLevel', 'StatusReason_Category', 'IndicadorRetraso', 
            'ImpactoVenta', 'DuracionProyecto', 'SolutionID', 'IndustryID'
        ]
    }
    
    disponibles = df.columns.tolist()
    faltan_criticas = [c for c in columnas_esperadas['criticas'] if c not in disponibles]
    faltan_all = []
    for grupo in columnas_esperadas.values():
        faltan_all.extend([c for c in grupo if c not in disponibles])
    
    return {
        'disponibles': disponibles,
        'faltan_criticas': faltan_criticas,
        'faltan_all': list(set(faltan_all)),
        'columnas_esperadas': columnas_esperadas
    }


def _preparar_datos_robustos(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara datos con validación inteligente y transformaciones."""
    
    df = df.copy()
    
    if df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated()]
    
    columnas_criticas = {
        'ProjectID': range(1, len(df) + 1),
        'ProjectName': 'Proyecto Sin Nombre',
        'CustomerRegion': 'No Especificado',
        'ProjectStatus_Flag': 'Unknown',
        'DiasRetraso': 0,
        'CriticalityLevel': 'Normal',
        'StatusReason_Category': 'Otro',
        'IndicadorRetraso': 0,
        'ImpactoVenta': 0,
        'DuracionProyecto': 0
    }
    
    for col, default in columnas_criticas.items():
        if col not in df.columns:
            df[col] = default
        else:
            if col in ['DiasRetraso', 'IndicadorRetraso', 'ImpactoVenta', 'DuracionProyecto']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            elif col == 'ProjectID':
                df[col] = df[col].fillna(-1)
            else:
                df[col] = df[col].fillna(default)
    
    if 'FechaActualizacion' not in df.columns:
        df['FechaActualizacion'] = pd.Timestamp.now()
    else:
        df['FechaActualizacion'] = pd.to_datetime(df['FechaActualizacion'], errors='coerce')
    
    if 'Año' not in df.columns:
        df['Año'] = df['FechaActualizacion'].dt.year
    else:
        df['Año'] = pd.to_numeric(df['Año'], errors='coerce').fillna(2024).astype(int)
    
    if 'Mes' not in df.columns:
        df['Mes'] = df['FechaActualizacion'].dt.strftime('%Y-%m')
    
    if 'Trimestre' not in df.columns:
        df['Trimestre'] = 'T' + df['FechaActualizacion'].dt.quarter.astype(str)
    else:
        # Ensure Trimestre is string for concatenation
        df['Trimestre'] = df['Trimestre'].astype(str)
    
    def clasificar_severidad(dias):
        if dias > 31:
            return 'Critico >31d'
        elif dias > 0:
            return 'Moderado 1-31d'
        else:
            return 'Sin retraso'
    
    df['SeveridadRetraso'] = df['DiasRetraso'].apply(clasificar_severidad)
    
    def clasificar_impacto(monto):
        if monto > 500000:
            return '>$500K'
        elif monto > 100000:
            return '$100K-$500K'
        elif monto > 0:
            return '$1-$100K'
        else:
            return 'Sin impacto'
    
    df['RangoImpacto'] = df['ImpactoVenta'].apply(clasificar_impacto)
    
    df['Año_Trimestre'] = df['Año'].astype(str) + '-' + df['Trimestre']
    
    df = df.dropna(subset=['ProjectID'])
    
    return df


def _aplicar_filtros_avanzados(df: pd.DataFrame) -> pd.DataFrame:
    """Filtros avanzados en sidebar con métricas de impacto."""
    
    st.sidebar.header("Filtros Avanzados")
    
    años = sorted(df['Año'].unique())
    años_sel = st.sidebar.multiselect("Año", años, default=años)
    df_temp = df[df['Año'].isin(años_sel)] if años_sel else df
    
    regiones = sorted(df_temp['CustomerRegion'].unique())
    regiones_sel = st.sidebar.multiselect("Región del Cliente", regiones, default=regiones)
    df_temp = df_temp[df_temp['CustomerRegion'].isin(regiones_sel)] if regiones_sel else df_temp
    
    estados = sorted(df_temp['ProjectStatus_Flag'].unique())
    estados_sel = st.sidebar.multiselect("Estado del Proyecto", estados, default=estados)
    df_temp = df_temp[df_temp['ProjectStatus_Flag'].isin(estados_sel)] if estados_sel else df_temp
    
    severidades = sorted(df_temp['SeveridadRetraso'].unique())
    severidades_sel = st.sidebar.multiselect("Severidad de Retraso", severidades, default=severidades)
    df_temp = df_temp[df_temp['SeveridadRetraso'].isin(severidades_sel)] if severidades_sel else df_temp
    
    if 'CriticalityLevel' in df_temp.columns:
        criticidades = sorted(df_temp['CriticalityLevel'].unique())
        criticidades_sel = st.sidebar.multiselect("Nivel de Criticidad", criticidades, default=criticidades)
        df_temp = df_temp[df_temp['CriticalityLevel'].isin(criticidades_sel)] if criticidades_sel else df_temp

    # Filtro avanzado: Criterio de Parada
    if 'StatusReason_Category' in df_temp.columns:
        criterios = sorted(df_temp['StatusReason_Category'].unique())
        criterios_sel = st.sidebar.multiselect("Criterio de Parada", criterios, default=criterios)
        df_temp = df_temp[df_temp['StatusReason_Category'].isin(criterios_sel)] if criterios_sel else df_temp
    
    st.sidebar.divider()
    st.sidebar.caption(f"Registros filtrados: {len(df_temp):,} de {len(df):,}")
    
    if len(df_temp) > 0:
        impacto_filtrado = df_temp['ImpactoVenta'].sum()
        st.sidebar.caption(f"Impacto total: ${impacto_filtrado/1e6:.2f}M")
    
    return df_temp


def _render_kpis_ejecutivos(df: pd.DataFrame, session_state: dict):
    """KPIs ejecutivos con comparativas."""
    
    st.subheader("Indicadores Ejecutivos Clave")
    
    total = len(df)
    criticos = len(df[df['CriticalityLevel'] == 'Crítico'])
    con_retraso = len(df[df['DiasRetraso'] > 0])
    dias_prom = df[df['DiasRetraso'] > 0]['DiasRetraso'].mean() if con_retraso > 0 else 0
    duracion_prom = df['DuracionProyecto'].mean() if 'DuracionProyecto' in df.columns else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Paradas", f"{total:,}")

    with col2:
        pct = (criticos / total * 100) if total > 0 else 0
        st.metric("Proyectos Críticos", f"{criticos:,}", f"{pct:.1f}%")

    with col3:
        pct = (con_retraso / total * 100) if total > 0 else 0
        st.metric("Con Retraso", f"{con_retraso:,}", f"{pct:.1f}%")

    with col4:
        st.metric("Retraso Promedio", f"{dias_prom:.0f} días")


def _render_analisis_distribucion(df: pd.DataFrame):
    """Análisis de distribución con múltiples perspectivas."""
    
    st.subheader("Análisis de Distribución")
    
    col1, col2 = st.columns(2)

    with col1:
        severidad_counts = df['SeveridadRetraso'].value_counts()
        fig_severidad = px.pie(
            values=severidad_counts.values,
            names=severidad_counts.index,
            title="Distribución por Severidad de Retraso",
            color_discrete_map={
                'Sin retraso': '#2ecc71',
                'Moderado 1-31d': '#f39c12',
                'Critico >31d': '#e74c3c'
            },
            hole=0.4
        )
        fig_severidad.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_severidad, use_container_width=True)

    with col2:
        estado_counts = df['ProjectStatus_Flag'].value_counts().head(10)
        fig_estado = px.bar(
            x=estado_counts.values,
            y=estado_counts.index,
            orientation='h',
            title="Top 10 Estados de Proyecto",
            labels={'x': 'Cantidad', 'y': 'Estado'},
            color=estado_counts.values,
            color_continuous_scale='Reds'
        )
        fig_estado.update_layout(showlegend=False)
        st.plotly_chart(fig_estado, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        if 'StatusReason_Category' in df.columns:
            motivo_counts = df['StatusReason_Category'].value_counts().head(8)
            fig_motivo = px.bar(
                x=motivo_counts.index,
                y=motivo_counts.values,
                title="Principales Criterios de Parada",
                labels={'x': 'Criterio de Parada', 'y': 'Cantidad'},
                color=motivo_counts.values,
                color_continuous_scale='Blues'
            )
            fig_motivo.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_motivo, use_container_width=True)

    with col4:
        region_counts = df['CustomerRegion'].value_counts().head(10)
        fig_region = px.bar(
            x=region_counts.values,
            y=region_counts.index,
            orientation='h',
            title="Top 10 Regiones Afectadas",
            labels={'x': 'Proyectos', 'y': 'Región'},
            color=region_counts.values,
            color_continuous_scale='Greens'
        )
        fig_region.update_layout(showlegend=False)
        st.plotly_chart(fig_region, use_container_width=True)


def _render_analisis_temporal(df: pd.DataFrame):
    """Análisis de evolución temporal con múltiples métricas."""
    
    st.subheader("Evolución Temporal")
    
    df_temporal = df[df['Mes'].notna()].copy()
    
    if df_temporal.empty:
        st.info("No hay datos temporales disponibles para análisis.")
        return
    
    evolucion_mes = df_temporal.groupby('Mes').agg({
        'ProjectID': 'count',
        'DiasRetraso': 'mean'
    }).reset_index()
    evolucion_mes.columns = ['Mes', 'Cantidad', 'Retraso_Prom']
    evolucion_mes = evolucion_mes.sort_values('Mes')

    fig_temporal = make_subplots(
        rows=1, cols=1,
        subplot_titles=('Cantidad de Paradas y Retraso Promedio',),
        specs=[[{"secondary_y": True}]],
        vertical_spacing=0.15
    )

    fig_temporal.add_trace(
        go.Bar(
            x=evolucion_mes['Mes'],
            y=evolucion_mes['Cantidad'],
            name='Cantidad Paradas',
            marker_color='lightblue'
        ),
        row=1, col=1, secondary_y=False
    )

    fig_temporal.add_trace(
        go.Scatter(
            x=evolucion_mes['Mes'],
            y=evolucion_mes['Retraso_Prom'],
            name='Retraso Promedio',
            mode='lines+markers',
            marker=dict(size=8, color='red'),
            line=dict(width=3)
        ),
        row=1, col=1, secondary_y=True
    )

    fig_temporal.update_xaxes(title_text="Mes", row=1, col=1)
    fig_temporal.update_yaxes(title_text="Cantidad Paradas", row=1, col=1, secondary_y=False)
    fig_temporal.update_yaxes(title_text="Retraso Promedio (días)", row=1, col=1, secondary_y=True)

    fig_temporal.update_layout(height=500, hovermode='x unified', showlegend=True)

    st.plotly_chart(fig_temporal, use_container_width=True)
    
    if 'Año_Trimestre' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            trimestre_data = df.groupby('Año_Trimestre').size().reset_index(name='Cantidad')
            trimestre_data = trimestre_data.sort_values('Año_Trimestre')
            
            fig_trim = px.line(
                trimestre_data,
                x='Año_Trimestre',
                y='Cantidad',
                title='Tendencia Trimestral',
                markers=True
            )
            fig_trim.update_traces(line=dict(width=3), marker=dict(size=10))
            st.plotly_chart(fig_trim, use_container_width=True)
        
        with col2:
            año_data = df.groupby('Año').size().reset_index(name='Cantidad')
            
            fig_año = px.bar(
                año_data,
                x='Año',
                y='Cantidad',
                title='Paradas por Año',
                color='Cantidad',
                color_continuous_scale='Oranges'
            )
            st.plotly_chart(fig_año, use_container_width=True)


def _render_matriz_impacto(df: pd.DataFrame):
    """Matriz de impacto y análisis de correlación."""
    
    # Eliminado análisis de impacto financiero
    st.subheader("Análisis por Región")
    region_agg = df.groupby('CustomerRegion').agg({
        'ProjectID': 'count',
        'DiasRetraso': 'mean'
    }).sort_values('DiasRetraso', ascending=False).head(10).reset_index()
    fig_region = px.bar(
        region_agg,
        x='CustomerRegion',
        y='DiasRetraso',
        title='Retraso Promedio por Región (Top 10)',
        labels={'DiasRetraso': 'Retraso Promedio (días)', 'CustomerRegion': 'Región'},
        color='DiasRetraso',
        color_continuous_scale='Reds'
    )
    fig_region.update_layout(showlegend=False)
    st.plotly_chart(fig_region, use_container_width=True)


def _render_analisis_comparativo(df: pd.DataFrame):
    """Análisis comparativo por dimensiones clave."""
    
    st.subheader("Análisis Comparativo Multidimensional")
    
    tab1, tab2, tab3 = st.tabs(["Por Región", "Por Industria", "Por Solución"])
    
    with tab1:
        region_agg = df.groupby('CustomerRegion').agg({
            'ProjectID': 'count',
            'ImpactoVenta': 'sum',
            'DiasRetraso': 'mean'
        }).sort_values('ImpactoVenta', ascending=False).head(15).reset_index()
        region_agg.columns = ['Region', 'Proyectos', 'Impacto_Total', 'Retraso_Prom']
        
        fig_region = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Proyectos por Región', 'Impacto Financiero por Región'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        fig_region.add_trace(
            go.Bar(x=region_agg['Region'], y=region_agg['Proyectos'], name='Proyectos'),
            row=1, col=1
        )
        
        fig_region.add_trace(
            go.Bar(
                x=region_agg['Region'],
                y=region_agg['Impacto_Total']/1e6,
                name='Impacto ($M)',
                marker_color='coral'
            ),
            row=1, col=2
        )
        
        fig_region.update_xaxes(tickangle=-45)
        fig_region.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_region, use_container_width=True)
    
    with tab2:
        if 'IndustryID' in df.columns:
            industry_agg = df.groupby('IndustryID').agg({
                'ProjectID': 'count',
                'DiasRetraso': 'mean'
            }).sort_values('ProjectID', ascending=False).head(12).reset_index()
            
            fig_industry = px.bar(
                industry_agg,
                x='IndustryID',
                y='ProjectID',
                title='Paradas por Industria',
                labels={'ProjectID': 'Cantidad', 'IndustryID': 'Industria'},
                color='DiasRetraso',
                color_continuous_scale='YlOrRd'
            )
            fig_industry.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_industry, use_container_width=True)
        else:
            st.info("Datos de industria no disponibles")
    
    with tab3:
        if 'SolutionID' in df.columns:
            solution_agg = df.groupby('SolutionID').agg({
                'ProjectID': 'count',
                'DiasRetraso': 'mean'
            }).sort_values('ProjectID', ascending=False).head(12).reset_index()
            
            fig_solution = px.bar(
                solution_agg,
                x='SolutionID',
                y='ProjectID',
                title='Paradas por Solución',
                labels={'ProjectID': 'Cantidad', 'SolutionID': 'Solución'},
                color='DiasRetraso',
                color_continuous_scale='Blues'
            )
            fig_solution.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_solution, use_container_width=True)
        else:
            st.info("Datos de solución no disponibles")


def _render_tablas_detalle(df: pd.DataFrame):
    """Tablas pivote y detalle exportable."""
    
    st.subheader(f"Análisis Detallado ({len(df):,} registros)")
    
    tab1, tab2, tab3 = st.tabs(["Tablas Pivote", "Detalle Completo", "Resumen Ejecutivo"])
    
    with tab1:
        st.markdown("#### Tabla Pivote: Región vs Estado")
        pivot_region_estado = df.pivot_table(
            index='CustomerRegion',
            columns='ProjectStatus_Flag',
            values='ProjectID',
            aggfunc='count',
            fill_value=0,
            margins=True,
            margins_name='Total'
        )
        st.dataframe(pivot_region_estado, use_container_width=True)
        
        if 'CriticalityLevel' in df.columns:
            st.markdown("#### Tabla Pivote: Criticidad vs Severidad")
            pivot_crit_sev = df.pivot_table(
                index='CriticalityLevel',
                columns='SeveridadRetraso',
                values='ProjectID',
                aggfunc='count',
                fill_value=0,
                margins=True,
                margins_name='Total'
            )
            st.dataframe(pivot_crit_sev, use_container_width=True)
    
    with tab2:
        cols_exportar = [
            'ProjectID', 'ProjectName', 'CustomerRegion', 'ProjectStatus_Flag',
            'CriticalityLevel', 'StatusReason_Category', 'DiasRetraso',
            'ImpactoVenta', 'DuracionProyecto', 'SeveridadRetraso',
            'Año', 'Trimestre', 'Mes'
        ]
        cols_disponibles = [c for c in cols_exportar if c in df.columns]
        df_detalle = df[cols_disponibles].copy()
        
        if 'DiasRetraso' in df_detalle.columns:
            df_detalle['DiasRetraso'] = df_detalle['DiasRetraso'].round(0).astype(int)
        
        if 'ImpactoVenta' in df_detalle.columns:
            df_detalle['ImpactoVenta_Formatted'] = df_detalle['ImpactoVenta'].apply(
                lambda x: f"${x:,.0f}"
            )
        
        st.dataframe(df_detalle, use_container_width=True, height=400)
        
        csv = df_detalle.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Detalle Completo (CSV)",
            data=csv,
            file_name=f"detalle_paradas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.markdown("#### Resumen por Región")
        resumen_region = df.groupby('CustomerRegion').agg({
            'ProjectID': 'count',
            'DiasRetraso': ['mean', 'max'],
            'ImpactoVenta': 'sum'
        }).round(2)
        resumen_region.columns = ['Proyectos', 'Retraso_Prom', 'Retraso_Max', 'Impacto_Total']
        resumen_region = resumen_region.sort_values('Impacto_Total', ascending=False)
        st.dataframe(resumen_region, use_container_width=True)
        
        st.markdown("#### Top 10 Proyectos por Impacto")
        top_proyectos = df.nlargest(10, 'ImpactoVenta')[
            ['ProjectName', 'CustomerRegion', 'DiasRetraso', 'ImpactoVenta']
        ].copy()
        top_proyectos['ImpactoVenta'] = top_proyectos['ImpactoVenta'].apply(
            lambda x: f"${x:,.0f}"
        )
        st.dataframe(top_proyectos, use_container_width=True, hide_index=True)