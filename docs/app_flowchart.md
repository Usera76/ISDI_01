# Diagrama de Flujo de la Aplicación

```mermaid
flowchart TD
    subgraph Entrada_Datos[Entrada de Datos]
        A[Interfaz de Usuario] --> B1[Datos Demo]
        A --> B2[Carga CSV]
        A --> B3[Carga PDF]
        A --> B4[Entrada Manual]
        B3 -->|IA| C1[Procesamiento PDF con GPT]
    end

    subgraph Contexto[Configuración Contextual]
        D[Sector]
        E[Región]
    end

    subgraph Análisis_Principal[Análisis Principal]
        F[Datos Procesados] --> G[Generación de Escenarios]
        G -->|IA| H1[Escenario Base]
        G -->|IA| H2[Escenario Optimista]
        G -->|IA| H3[Escenario Pesimista]
        
        F --> I[Análisis de Clustering]
        I -->|IA| J1[Interpretación de Clusters]
        I --> J2[Visualización de Clusters]
    end

    subgraph Visualización[Visualización y Reporting]
        K[Dashboard de Métricas]
        L[Gráficos Comparativos]
        M[Proyecciones Temporales]
    end

    Contexto --> G
    Contexto --> I
    H1 --> K
    H2 --> K
    H3 --> K
    J1 --> L
    J2 --> L

    style G fill:#ff9999
    style C1 fill:#ff9999
    style H1 fill:#ff9999
    style H2 fill:#ff9999
    style H3 fill:#ff9999
    style J1 fill:#ff9999
    
    classDef iaNode fill:#ff9999,stroke:#333,stroke-width:2px;
