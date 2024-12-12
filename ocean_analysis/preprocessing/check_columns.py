import pandas as pd

# Leer datos
print("Leyendo datos...")
df = pd.read_csv("ocean_analysis/data/raw/datos_gerlache.csv", 
                 sep=';', 
                 decimal='.', 
                 encoding='latin-1')

# Mostrar todas las columnas
print("\nColumnas disponibles:")
for col in df.columns:
    print(f"  - {col}") 