# Datamart Proyectos SAP - Modelo Dimensional

## Descripción del Proyecto

Este repositorio contiene la implementación de un datamart dimensional para el análisis y seguimiento de proyectos de implementación SAP. El modelo está diseñado para proporcionar una vista analítica integral que permita evaluar el rendimiento, estado y métricas clave de los proyectos de transformación empresarial.

## Arquitectura del Modelo Dimensional

### Fact Table

**Fact_Proyectos**: Tabla central que contiene las métricas y medidas cuantificables relacionadas con los proyectos SAP.

**Métricas:**
- Número de proyectos por estado
- Tiempo de implementación (duración entre Contract Start y Contract End)
- Indicadores de retraso (diferencias entre fechas planificadas y confirmadas)
- Distribución de proyectos por región, industria y área de solución
- Indicadores de cumplimiento contractual

### Dimensiones del Modelo

#### 1. Dim_Proyecto
Contiene la información descriptiva básica de cada proyecto, incluyendo identificadores únicos, nomenclatura oficial, estado actual dentro del ciclo de vida del proyecto y resumen ejecutivo que contextualiza el alcance y objetivos estratégicos.

#### 2. Dim_Tiempo
Dimensión temporal que registra todas las fechas críticas del ciclo de vida del proyecto, desde la firma contractual hasta la puesta en producción, permitiendo análisis temporales y seguimiento de hitos clave en la metodología SAP Activate.

#### 3. Dim_Cliente
Agrupa la información del cliente incluyendo identificación corporativa, segmentación geográfica y clasificación por unidades de mercado, facilitando análisis por perfiles de cliente y distribución geográfica de la cartera de proyectos.

#### 4. Dim_Solución
Categoriza las áreas de solución SAP implementadas, organizadas jerárquicamente desde el nivel más general hasta los productos lógicos específicos, permitiendo análisis de adopción tecnológica y especialización por líneas de producto.

#### 5. Dim_Wave
Gestiona la información de las oleadas de despliegue, que representan agrupaciones lógicas de proyectos con características similares o cronología coordinada, incluyendo su estado operativo y fase de ejecución.

#### 6. Dim_Partner
Registra la información de los socios estratégicos y colaboradores involucrados en la ejecución de proyectos, tanto principales como secundarios, permitiendo análisis de rendimiento y distribución de cartera por canal de partners.

#### 7. Dim_Industria
Clasifica los proyectos según la industria del cliente, arquetipos de implementación y clasificaciones internas de Customer Success, facilitando análisis sectoriales y estrategias de specialización vertical.

#### 8. Dim_Riesgo_Estado
Dimensión que consolida todos los indicadores de riesgo, escalamientos y estados operativos tanto internos como reportados por partners, proporcionando una vista integral de la salud del proyecto y alertas tempranas.

## Diccionario de Datos

### Tabla de Hechos - Fact_Proyectos

| Campo | Descripción | Tipo de Dato SQL Server |
|-------|-------------|------------------------|
| ProjectID | Clave primaria - Identificador único del proyecto | INT |
| WaveID | Clave foránea - Identificador de la ola de despliegue | INT |
| CustomerID | Clave foránea - Identificador único del cliente | INT |
| DateKey | Clave foránea - Referencia a dimensión tiempo | INT |
| DuracionProyecto | Duración en días del proyecto (Contract End - Contract Start) | INT |
| IndicadorRetraso | Indicador binario de retraso en go-live | BIT |
| DiasRetraso | Días de retraso respecto a fecha planificada | INT |

### Dimensión Proyecto - Dim_Proyecto

| Campo | Descripción | Tipo de Dato SQL Server |
|-------|-------------|------------------------|
| ProjectID | Clave primaria - Identificador único del proyecto | INT |
| ProjectName | Nombre oficial del proyecto | NVARCHAR(255) |
| ProjectStatus | Estado actual del proyecto | NVARCHAR(50) |
| CurrentActivatePhase | Fase actual metodología SAP Activate | NVARCHAR(50) |
| ExecutiveSummary | Resumen ejecutivo del proyecto | NVARCHAR(MAX) |
| ProjectContractEnded | Indicador si el proyecto ha finalizado contractualmente | BIT |
| SolutionScope | Alcance funcional de la solución | NVARCHAR(500) |
| Validated | Indicador de validación por SAP | BIT |
| StrategicDeployment | Indicador de despliegue estratégico | BIT |

### Dimensión Tiempo - Dim_Tiempo

| Campo | Descripción | Tipo de Dato SQL Server |
|-------|-------------|------------------------|
| DateKey | Clave primaria - Identificador único de fecha | INT |
| ContractSigned | Fecha de firma del contrato | DATE |
| ContractStart | Fecha de inicio del contrato | DATE |
| ContractEnd | Fecha de fin planificada del contrato | DATE |
| ContractEnded | Indicador si el contrato está finalizado | BIT |
| KickoffDate | Fecha de reunión de inicio del proyecto | DATE |
| PlannedGoLive | Fecha planificada de go-live | DATE |
| ConfirmedGoLive | Fecha confirmada de go-live | DATE |
| Año | Año de la fecha | INT |
| Mes | Mes de la fecha | INT |
| Trimestre | Trimestre de la fecha | INT |

### Dimensión Cliente - Dim_Cliente

| Campo | Descripción | Tipo de Dato SQL Server |
|-------|-------------|------------------------|
| CustomerID | Clave primaria - Identificador único del cliente | INT |
| Customer | Razón social del cliente | NVARCHAR(255) |
| CustomerRegion | Región comercial del cliente | NVARCHAR(50) |
| Country | País principal de operación | NVARCHAR(100) |
| CountryCode | Código ISO del país | NVARCHAR(10) |
| MarketUnit | Unidad de mercado específica | NVARCHAR(100) |
| GrowWithSAPScaleups | Indicador programa Grow with SAP | BIT |

### Dimensión Solución - Dim_Solución

| Campo | Descripción | Tipo de Dato SQL Server |
|-------|-------------|------------------------|
| SolutionID | Clave primaria - Identificador único de solución | INT |
| SolutionArea | Área de solución SAP nivel 1 | NVARCHAR(100) |
| SubSolutionArea | Subárea de solución SAP | NVARCHAR(100) |
| SolutionAreaL3 | Nivel 3 de categorización | NVARCHAR(100) |
| SolutionAreaL4 | Nivel 4 de categorización | NVARCHAR(100) |
| LogicalProduct | Producto lógico asociado | NVARCHAR(100) |
| SAPCloudALM | Indicador uso SAP Cloud ALM | BIT |
| IntelligentEnterpriseBTP | Indicador servicios BTP complementarios | BIT |

### Dimensión Wave - Dim_Wave

| Campo | Descripción | Tipo de Dato SQL Server |
|-------|-------------|------------------------|
| WaveID | Clave primaria - Identificador único de ola | INT |
| WaveName | Nombre descriptivo de la ola | NVARCHAR(255) |
| WaveStage | Etapa operativa de la ola | NVARCHAR(100) |
| WaveStatus | Semáforo de estado de la ola | NVARCHAR(20) |
| RISEEntitlement | Indicador derechos RISE | BIT |
| RISECore | Indicador RISE Core | BIT |
| SOLEX | Indicador programas SOLEX | BIT |
| CAPP | Indicador participación CAPP | BIT |
| RolloutCountries | Países contemplados para despliegue | NVARCHAR(MAX) |

### Dimensión Partner - Dim_Partner

| Campo | Descripción | Tipo de Dato SQL Server |
|-------|-------------|------------------------|
| PartnerID | Clave primaria - Identificador único de partner | INT |
| MainPartner | Socio principal del proyecto | NVARCHAR(255) |
| MainPartnerID | Identificador del partner principal | NVARCHAR(50) |
| WavePartners | Lista de partners de la ola | NVARCHAR(MAX) |
| WavePartnerIDs | Identificadores de partners de ola | NVARCHAR(MAX) |
| LastChangedByPartner | Indicador último cambio por partner | BIT |

### Dimensión Industria - Dim_Industria

| Campo | Descripción | Tipo de Dato SQL Server |
|-------|-------------|------------------------|
| IndustryID | Clave primaria - Identificador único de industria | INT |
| Industry | Industria según categorización SAP | NVARCHAR(100) |
| ISS | Código segmentación industria/solución | NVARCHAR(50) |
| Archetype | Arquetipo del cliente o despliegue | NVARCHAR(100) |
| SubArchetype | Subarquetipo del despliegue | NVARCHAR(100) |
| CSClassification | Clasificación Customer Success | NVARCHAR(100) |

### Dimensión Riesgo Estado - Dim_Riesgo_Estado

| Campo | Descripción | Tipo de Dato SQL Server |
|-------|-------------|------------------------|
| RiskStatusID | Clave primaria - Identificador único | INT |
| EscalationLevel | Nivel de escalamiento activo | INT |
| StatusReason | Motivo del estado actual | NVARCHAR(500) |
| WavePartnerStatus | Semáforo reportado por partner | NVARCHAR(20) |
| StatusMatch | Coincidencia status partner/interno | BIT |
| ManuallySetLive | Estado Live establecido manualmente | BIT |

## Integrantes:
- Francesco Ernesto Carlevarino Diaz
- Jhoan Leandro Vargas Collas
