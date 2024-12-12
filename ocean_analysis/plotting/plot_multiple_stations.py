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

# Profundidades objetivo estándar
standard_depths = [0.5, 10, 25, 50, 100, 200]

# Estaciones a procesar
stations = ['GS11', 'GS15', 'GS18', 'GS20', 'GS23', 'GS26', 'GS29', 'GS34']

# Crear una figura para cada estación
for station in stations:
    # Filtrar datos para la estación
    station_data = df[df['Station '] == station].copy()
    
    # Función para encontrar el índice más cercano a una profundidad objetivo
    def find_nearest_depth(pressure_values, target):
        return (np.abs(np.array(pressure_values) - target)).argmin()

    # Filtrar solo las profundidades más cercanas a las objetivo
    filtered_indices = []
    pressures = station_data['pressure [db]'].values
    
    # Usar las profundidades estándar
    for target in standard_depths:
        idx = find_nearest_depth(pressures, target)
        filtered_indices.append(idx)

    station_data = station_data.iloc[filtered_indices].copy()

    # Crear la figura con 4 subplots horizontales
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(16, 6))
    fig.suptitle(f'Perfiles Biogeoquímicos - Estación {station}', fontsize=14)

    # Plot Clorofila-a
    ax1.plot(station_data['Chl-A [ug/L]'], station_data['pressure [db]'], 'go-', label='Clorofila-a')
    ax1.set_ylabel('Presión (dbar)')
    ax1.set_xlabel('Clorofila-a (μg/L)')
    ax1.invert_yaxis()
    ax1.set_ylim(220, 0)  # Establecer límite de profundidad uniforme

    # Plot Nitrato
    ax2.plot(station_data['nitrate'], station_data['pressure [db]'], 'bo-', label='Nitrato')
    ax2.set_xlabel('Nitrato (μM)')
    ax2.invert_yaxis()
    ax2.set_ylim(220, 0)  # Establecer límite de profundidad uniforme

    # Plot Fosfato
    ax3.plot(station_data['phosphate'], station_data['pressure [db]'], 'ro-', label='Fosfato')
    ax3.set_xlabel('Fosfato (μM)')
    ax3.invert_yaxis()
    ax3.set_ylim(220, 0)  # Establecer límite de profundidad uniforme

    # Plot Silicato
    ax4.plot(station_data['silicate'], station_data['pressure [db]'], 'mo-', label='Silicato')
    ax4.set_xlabel('Silicato (μM)')
    ax4.invert_yaxis()
    ax4.set_ylim(220, 0)  # Establecer límite de profundidad uniforme

    # Ajustar espaciado
    plt.tight_layout()

    # Guardar figura
    plt.savefig(f'test_outputs/bgq_profiles_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Imprimir información sobre los datos
    print(f"\nInformación de mediciones para estación {station}:")
    variables = ['Chl-A [ug/L]', 'nitrate', 'phosphate', 'silicate']
    for var in variables:
        print(f"\n{var}:")
        print(f"Número de mediciones: {len(station_data)}")
        print("\nValores por profundidad:")
        for _, row in station_data.sort_values('pressure [db]').iterrows():
            print(f"  {row['pressure [db]']:>6.1f} dbar: {row[var]:>8.3f}")
    print("-" * 50) 