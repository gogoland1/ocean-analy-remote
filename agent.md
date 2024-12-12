Desarrollo de Sistema Automatizado para Análisis Oceanográfico
Objetivo
Crear un sistema de agentes IA para automatizar el análisis de datos oceanográficos y generación de informes.
Estructura Actual
1. Agente Supervisor

Actúa como Product Manager
Entrevista otros agentes
Evalúa resultados
Proporciona feedback

2. Agente Parser (en desarrollo)

Maneja formatos: .odv, .nc, .cnv, .csv, .txt
Funcionalidades:

Identificación automática de variables
Extracción de metadata
Manejo de errores
Estandarización de outputs



3. Implementación
Copyocean_analysis/
├── ocean_parser.py     # Parser principal
├── test_parser.py      # Testing
├── data/              # Datos de prueba
└── requirements.txt    # Dependencias
Próximos Pasos

Testing del parser standalone
Migración a Jupyter Notebook
Desarrollo del agente de control de calidad
Integración con sistema de agentes

Tecnologías

Python (base)
LangChain (agentes IA)
netCDF4/xarray (datos oceanográficos)
pandas/numpy (análisis)
Jupyter (desarrollo/testing)

Estado Actual
Fase inicial: Implementación del parser básico para testing.