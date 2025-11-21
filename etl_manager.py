"""
ETL Manager for SAP Projects Exception Dashboard
- Connects to SQLite database (configurable path)
- Provides data loading functions for Fact_Proyectos and related dimensions
- Includes exception filtering and summary metrics
- Error handling and Streamlit cache support
"""
import sqlite3
import pandas as pd
import streamlit as st


def get_connection(db_path: str):
    """
    Establish a connection to the SQLite database.
    Args:
        db_path (str): Path to the SQLite database file.
    Returns:
        sqlite3.Connection: SQLite connection object.
    Raises:
        sqlite3.Error: If connection fails.
    """
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(f"Error connecting to database: {e}")


@st.cache_data(show_spinner=False)
def load_fact_proyectos(db_path: str) -> pd.DataFrame:
    """
    Load Fact_Proyectos joined with Dim_Proyecto and Dim_Tiempo.
    Args:
        db_path (str): Path to the SQLite database file.
    Returns:
        pd.DataFrame: DataFrame with joined project facts and dimensions.
    """
    query = '''
        SELECT f.*, dp.ProjectName, dp.ProjectStatus, dt.ContractSigned, dt.PlannedGoLive,
               dt.Año, dt.Mes, dt.Trimestre,
               f.CriticalityLevel, f.StatusReason_Category, f.ProjectStatus_Flag,
               f.ImpactoVenta
        FROM Fact_Proyectos_LIMPIA f
        LEFT JOIN Dim_Proyecto dp ON f.ProjectID = dp.ProjectID
        LEFT JOIN Dim_Tiempo dt ON f.DateKey = dt.DateKey
    '''
    try:
        with get_connection(db_path) as conn:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        raise RuntimeError(f"Error loading Fact_Proyectos: {e}")


@st.cache_data(show_spinner=False)
def load_exceptions_data(db_path: str) -> pd.DataFrame:
    """
    Load only projects with IndicadorRetraso=1 OR Estado='Pausado'.
    Args:
        db_path (str): Path to the SQLite database file.
    Returns:
        pd.DataFrame: DataFrame with exception projects.
    """
    query = '''
        SELECT f.*,
               dp.ProjectName, dp.ProjectStatus,
               dt.ContractSigned, dt.PlannedGoLive,
               dt.Año, dt.Mes, dt.Trimestre,
               dc.CustomerRegion,
               ds.SolutionArea,
               di.ISS,
               dpa.MainPartner,
               f.CriticalityLevel, f.StatusReason_Category, f.ProjectStatus_Flag
        FROM Fact_Proyectos_LIMPIA f
        LEFT JOIN Dim_Proyecto dp ON f.ProjectID = dp.ProjectID
        LEFT JOIN Dim_Tiempo dt ON f.DateKey = dt.DateKey
        LEFT JOIN Dim_Cliente dc ON f.CustomerID = dc.CustomerID
        LEFT JOIN Dim_Solucion ds ON f.SolutionID = ds.SolutionID
        LEFT JOIN Dim_Industria di ON f.IndustryID = di.IndustryID
        LEFT JOIN Dim_Partner dpa ON f.PartnerID = dpa.PartnerID
        WHERE f.IndicadorRetraso = 1 OR dp.ProjectStatus = 'Pausado'
    '''
    try:
        with get_connection(db_path) as conn:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        raise RuntimeError(f"Error loading exceptions data: {e}")


@st.cache_data(show_spinner=False)
def load_summary_metrics(db_path: str) -> dict:
    """
    Compute global KPIs: average delay days, % affected, sales at risk.
    Args:
        db_path (str): Path to the SQLite database file.
    Returns:
        dict: Dictionary with KPI metrics.
    """
    query = '''
        SELECT 
            AVG(f.DiasRetraso) AS avg_delay_days,
            SUM(CASE WHEN f.IndicadorRetraso = 1 OR dp.ProjectStatus = 'Pausado' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS pct_affected
        FROM Fact_Proyectos f
        LEFT JOIN Dim_Proyecto dp ON f.ProjectID = dp.ProjectID
    '''
    try:
        with get_connection(db_path) as conn:
            row = pd.read_sql_query(query, conn).iloc[0]
        return {
            'avg_delay_days': row['avg_delay_days'],
            'pct_affected': row['pct_affected']
        }
    except Exception as e:
        raise RuntimeError(f"Error loading summary metrics: {e}")
