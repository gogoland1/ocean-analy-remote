import pandas as pd
import numpy as np

# Configurar pandas para mostrar todas las columnas
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Leer datos de nutrientes
print("Leyendo datos de nutrientes...")
df = pd.read_csv("ocean_analysis/data_tests/datosgerlache_nut.csv", 
                 sep=';', 
                 decimal='.', 
                 encoding='latin-1')

# Mostrar todas las columnas
print("\nColumnas disponibles:")
for i, col in enumerate(df.columns, 1):
    print(f"{i:2d}. {col}")

# Buscar columnas relacionadas con nutrientes
print("\nColumnas que podrían contener datos de nutrientes:")
nutrient_terms = ['no3', 'no2', 'nh4', 'po4', 'sio4', 'nitr', 'phos', 'sil']
for col in df.columns:
    if any(term in col.lower() for term in nutrient_terms):
        print(f"  - {col}")

# Filtrar para la estación GS1
station_data = df[df['Station'] == 'GS1']

# Mostrar información básica del dataset
print(f"\nNúmero total de registros: {len(df)}")
print(f"Número de registros para GS1: {len(station_data)}")

# Mostrar las primeras filas de la estación GS1
print("\nPrimeras filas de la estación GS1:")
print(station_data.head()) 