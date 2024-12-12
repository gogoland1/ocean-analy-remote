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

# Filtrar para la estación GS1
station_data = df[df['Station'] == 'GS1'].copy()

# Variables a revisar
variables = ['Chl-A [ug/L]', 'nitrate', 'phosphate', 'silicate']

print("\nAnálisis de profundidades por variable para GS1:")
for var in variables:
    if var in station_data.columns:
        # Filtrar datos no nulos
        valid_data = station_data[~station_data[var].isna()]
        depths = sorted(valid_data['depth [m]'].unique())
        
        print(f"\n{var}:")
        print(f"Número de mediciones: {len(valid_data)}")
        print(f"Profundidades (m): {depths}")
        print("\nValores por profundidad:")
        for depth in depths:
            value = valid_data[valid_data['depth [m]'] == depth][var].iloc[0]
            print(f"  {depth:>6.1f} m: {value:>8.3f}") 