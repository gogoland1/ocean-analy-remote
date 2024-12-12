import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Crear directorio de salida si no existe
os.makedirs('test_outputs', exist_ok=True)

# Leer datos de nutrientes
df = pd.read_csv("ocean_analysis/data_tests/datosgerlache_nut.csv", 
                 sep=';', 
                 decimal='.', 
                 encoding='latin-1')

# Profundidades objetivo
target_depths = [0.5, 10, 25, 50, 100, 200, 400]

# Filtrar para la estación GS1
station_data = df[df['Station '] == 'GS1'].copy()

# Función para encontrar el índice más cercano a una profundidad objetivo
def find_nearest_depth(pressure_values, target):
    return (np.abs(np.array(pressure_values) - target)).argmin()

# Filtrar solo las profundidades más cercanas a las objetivo
filtered_indices = []
pressures = station_data['pressure [db]'].values
for target in target_depths:
    idx = find_nearest_depth(pressures, target)
    filtered_indices.append(idx)

station_data = station_data.iloc[filtered_indices].copy()

# Crear la figura con 4 subplots horizontales
fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(16, 6))
fig.suptitle('Perfiles Biogeoquímicos - Estación GS1', fontsize=14)

# Plot Clorofila-a
ax1.plot(station_data['Chl-A [ug/L]'], station_data['pressure [db]'], 'go-', label='Clorofila-a')
ax1.set_ylabel('Presión (dbar)')
ax1.set_xlabel('Clorofila-a (μg/L)')
ax1.invert_yaxis()

# Plot Nitrato
ax2.plot(station_data['nitrate'], station_data['pressure [db]'], 'bo-', label='Nitrato')
ax2.set_xlabel('Nitrato (μM)')
ax2.invert_yaxis()

# Plot Fosfato
ax3.plot(station_data['phosphate'], station_data['pressure [db]'], 'ro-', label='Fosfato')
ax3.set_xlabel('Fosfato (μM)')
ax3.invert_yaxis()

# Plot Silicato
ax4.plot(station_data['silicate'], station_data['pressure [db]'], 'mo-', label='Silicato')
ax4.set_xlabel('Silicato (μM)')
ax4.invert_yaxis()

# Ajustar espaciado
plt.tight_layout()

# Guardar figura
plt.savefig('test_outputs/bgq_profiles_GS1.png', dpi=300, bbox_inches='tight')
plt.close()

# Imprimir información sobre los datos
print("\nInformación de mediciones por variable:")
variables = ['Chl-A [ug/L]', 'nitrate', 'phosphate', 'silicate']
for var in variables:
    print(f"\n{var}:")
    print(f"Número de mediciones: {len(station_data)}")
    print("\nValores por profundidad:")
    for _, row in station_data.sort_values('pressure [db]').iterrows():
        print(f"  {row['pressure [db]']:>6.1f} dbar: {row[var]:>8.3f}") 