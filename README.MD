# Datamart Proyectos SAP - Modelo Dimensional

## Problema de Negocio

El equipo que gestionan un portafolio de proyectos de implementación SAP enfrentan una falta de visibilidad centralizada sobre el estado real de sus iniciativas. La información se encuentra distribuida en múltiples fuentes, lo que dificulta:

- Detectar de manera temprana los retrasos entre las fechas planificadas y las fechas confirmadas.
- Identificar patrones de riesgo según región, industria, partner o fase del proyecto.

Consecuencia principal: La falta de una vista integrada limita la capacidad de toma de decisiones, incrementa el riesgo de retrasos y reduce la eficiencia en la gestión del portafolio SAP.

## Objetivo

Proporcionar una plataforma analítica que permita:
- Monitorear estados y fases de proyectos SAP 
- Identificar cuellos de botella y paradas en el ciclo de implementación
- Analizar desvíos temporales y cumplimiento de hitos contractuales
- Evaluar rendimiento por dimensiones clave (región, industria, partner, solución)
- Generar alertas tempranas basadas en indicadores de riesgo

## Solución Implementada

### **view_paradas.py** - Análisis de Paradas en Ciclo de Vida
Dashboard que identifica estancamientos en fases del proyecto (Kickoff, Prepare, Explore, Realize, Deploy). Visualiza:
- Proyectos sin avance de fase por período prolongado
- Distribución de proyectos por CurrentActivatePhase
- Tiempo promedio en cada fase vs. benchmark
- Cuellos de botella por industria/región/partner

**Valor:** Detecta ineficiencias operativas y permite reasignación proactiva de recursos.

### **view_retrasos.py** - Monitoreo de Desvíos Temporales
Sistema de análisis de brechas entre PlannedGoLive y ConfirmedGoLive. Muestra:
- Indicadores de retraso (IndicadorRetraso) y días acumulados (DiasRetraso)
- Distribución de retrasos por WaveStatus, Industry y MainPartner
- Correlación entre EscalationLevel y magnitud de desvío
- Tendencias temporales de cumplimiento

**Valor:** Identifica causas recurrentes de retrasos y facilita acciones correctivas preventivas.

## Arquitectura del Modelo Dimensional

### **Fact_Proyectos** - Tabla de Hechos
| Campo | Descripción | Tipo |
|-------|-------------|------|
| ProjectID | PK - Identificador único | INT |
| WaveID | FK - Ola de despliegue | INT |
| CustomerID | FK - Cliente | INT |
| DateKey | FK - Dimensión tiempo | INT |
| DuracionProyecto | Días (ContractEnd - ContractStart) | INT |
| IndicadorRetraso | Retraso en go-live (0/1) | BIT |
| DiasRetraso | Días vs. PlannedGoLive | INT |

### **Dim_Proyecto**
| Campo | Descripción | Tipo |
|-------|-------------|------|
| ProjectID | PK | INT |
| ProjectName | Nombre oficial | NVARCHAR(255) |
| ProjectStatus | Estado actual | NVARCHAR(50) |
| CurrentActivatePhase | Fase SAP Activate | NVARCHAR(50) |
| ExecutiveSummary | Resumen ejecutivo | NVARCHAR(MAX) |
| SolutionScope | Alcance funcional | NVARCHAR(500) |
| Validated | Validación SAP | BIT |
| StrategicDeployment | Despliegue estratégico | BIT |

### **Dim_Tiempo**
| Campo | Descripción | Tipo |
|-------|-------------|------|
| DateKey | PK | INT |
| ContractSigned | Firma contrato | DATE |
| ContractStart | Inicio contrato | DATE |
| ContractEnd | Fin planificado | DATE |
| KickoffDate | Reunión inicio | DATE |
| PlannedGoLive | Go-live planificado | DATE |
| ConfirmedGoLive | Go-live confirmado | DATE |
| Año / Trimestre / Mes | Jerarquía temporal | INT |

### **Dim_Cliente**
| Campo | Descripción | Tipo |
|-------|-------------|------|
| CustomerID | PK | INT |
| Customer | Razón social | NVARCHAR(255) |
| CustomerRegion | Región comercial | NVARCHAR(50) |
| Country / CountryCode | País ISO | NVARCHAR(100) |
| MarketUnit | Unidad de mercado | NVARCHAR(100) |
| GrowWithSAPScaleups | Programa Grow with SAP | BIT |

### **Dim_Solución**
| Campo | Descripción | Tipo |
|-------|-------------|------|
| SolutionID | PK | INT |
| SolutionArea | Área nivel 1 | NVARCHAR(100) |
| SubSolutionArea | Subárea | NVARCHAR(100) |
| SolutionAreaL3/L4 | Niveles 3 y 4 | NVARCHAR(100) |
| LogicalProduct | Producto lógico | NVARCHAR(100) |
| SAPCloudALM / IntelligentEnterpriseBTP | Indicadores adicionales | BIT |

### **Dim_Wave**
| Campo | Descripción | Tipo |
|-------|-------------|------|
| WaveID | PK | INT |
| WaveName | Nombre descriptivo | NVARCHAR(255) |
| WaveStage | Etapa operativa | NVARCHAR(100) |
| WaveStatus | Semáforo estado | NVARCHAR(20) |
| RISEEntitlement / RISECore / SOLEX / CAPP | Indicadores programas | BIT |
| RolloutCountries | Países despliegue | NVARCHAR(MAX) |

### **Dim_Partner**
| Campo | Descripción | Tipo |
|-------|-------------|------|
| PartnerID | PK | INT |
| MainPartner / MainPartnerID | Socio principal | NVARCHAR(255) |
| WavePartners / WavePartnerIDs | Partners adicionales | NVARCHAR(MAX) |
| LastChangedByPartner | Último cambio por partner | BIT |

### **Dim_Industria**
| Campo | Descripción | Tipo |
|-------|-------------|------|
| IndustryID | PK | INT |
| Industry | Categorización SAP | NVARCHAR(100) |
| ISS | Código segmentación | NVARCHAR(50) |
| Archetype / SubArchetype | Arquetipo despliegue | NVARCHAR(100) |
| CSClassification | Clasificación Customer Success | NVARCHAR(100) |

### **Dim_Riesgo_Estado**
| Campo | Descripción | Tipo |
|-------|-------------|------|
| RiskStatusID | PK | INT |
| EscalationLevel | Nivel escalamiento | INT |
| StatusReason | Motivo estado | NVARCHAR(500) |
| WavePartnerStatus | Semáforo partner | NVARCHAR(20) |
| StatusMatch | Coincidencia status | BIT |
| ManuallySetLive | Estado Live manual | BIT |

## Estructura del Repositorio

```
├── README.md                  # Este documento
├── datamart_diagram.md        # Diagrama del modelo dimensional
├── app.py                     # Aplicación principal
├── etl_manager.py            # Gestión de procesos ETL
├── view_paradas.py           # Dashboard análisis de paradas
├── view_retrasos.py          # Dashboard análisis de retrasos
└── requirements.txt          # Dependencias del proyecto
```

---

**Integrantes:**  
Francesco Ernesto Carlevarino Diaz | Jhoan Leandro Vargas Collas
