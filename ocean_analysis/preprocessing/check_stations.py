import pandas as pd
import numpy as np

# Leer datos de nutrientes
df = pd.read_csv("ocean_analysis/data_tests/datosgerlache_nut.csv", 
                 sep=';', 
                 decimal='.', 
                 encoding='latin-1')

# Variables a revisar
variables = ['Chl-A [ug/L]', 'nitrate', 'phosphate', 'silicate']

# Obtener lista única de estaciones
stations = df['Station '].unique()

print("Análisis de datos por estación:")
print("-" * 50)

for station in sorted(stations):
    # Filtrar datos para la estación
    station_data = df[df['Station '] == station].copy()
    
    # Verificar si hay datos de nutrientes y clorofila
    has_data = {}
    measurements = {}
    for var in variables:
        valid_data = station_data[~station_data[var].isna()]
        has_data[var] = len(valid_data) > 0
        measurements[var] = len(valid_data)
    
    # Si hay datos de al menos una variable, mostrar información
    if any(has_data.values()):
        print(f"\nEstación: {station}")
        print("Variables disponibles:")
        for var in variables:
            if has_data[var]:
                print(f"  - {var}: {measurements[var]} mediciones")
                # Mostrar profundidades si hay datos
                depths = sorted(station_data[~station_data[var].isna()]['pressure [db]'].unique())
                print(f"    Profundidades (dbar): {depths}")
        print("-" * 30) 