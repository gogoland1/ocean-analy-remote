import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from tensorflow.keras.models import load_model
from scipy.interpolate import griddata, interp1d
import joblib
import os

def create_section_plot(data, model, scaler):
    """
    Crear sección vertical con masas de agua clasificadas por la red neuronal
    usando solo temperatura, salinidad y oxígeno
    """
    # Definir estaciones y distancias
    stations = [f'GS{i}' for i in range(1, 39)]  # GS1 a GS38
    # Calcular distancias proporcionales entre estaciones
    distances = np.linspace(0, 120, len(stations))  # 120 km de longitud total aproximada
    
    # Crear grid para interpolación
    dist_grid, depth_grid = np.meshgrid(
        np.linspace(0, max(distances), 400),  # Mayor resolución horizontal
        np.linspace(0, 1000, 200)
    )
    
    # Preparar datos para interpolación
    section_data = data[data['Station '].isin(stations)].copy()
    
    # Recolectar datos de batimetría
    bottom_depths = []
    station_positions = []
    
    # Arrays para interpolación
    x = []
    y = []
    features = []
    
    # Almacenar estaciones encontradas
    found_stations = []
    found_distances = []
    
    for station, dist in zip(stations, distances):
        station_data = section_data[section_data['Station '] == station]
        if len(station_data) > 0:
            # Obtener profundidad del fondo
            bottom_depth = station_data['Bot. Depth [m]'].iloc[0]
            bottom_depths.append(bottom_depth)
            station_positions.append(dist)
            found_stations.append(station)
            found_distances.append(dist)
            
            for _, row in station_data.iterrows():
                x.append(dist)
                y.append(row['pressure [db]'])
                # Extraer solo T, S y O2
                feature_vector = [
                    row['Pot. Temp. [ºC]'],
                    row['salinity [PSU]'],
                    row['O2[umol/kg]']
                ]
                features.append(feature_vector)
    
    # Convertir a arrays
    features = np.array(features)
    
    # Normalizar features
    features_scaled = scaler.transform(features)
    
    # Predecir masas de agua
    predictions = model.predict(features_scaled)
    water_masses = np.argmax(predictions, axis=1)
    
    # Interpolar predicciones
    grid_predictions = griddata(
        (x, y),
        water_masses,
        (dist_grid, depth_grid),
        method='nearest'
    )
    
    # Interpolar batimetría
    f_bathy = interp1d(station_positions, bottom_depths, kind='cubic')
    x_bathy = np.linspace(min(distances), max(distances), 200)
    y_bathy = f_bathy(x_bathy)
    
    # Crear máscara para batimetría
    bathy_mask = np.zeros_like(grid_predictions, dtype=bool)
    for i, dist in enumerate(dist_grid[0]):
        depth_at_dist = np.interp(dist, x_bathy, y_bathy)
        bathy_mask[:, i] = depth_grid[:, i] > depth_at_dist
    
    # Aplicar máscara
    grid_predictions = np.ma.masked_array(grid_predictions, bathy_mask)
    
    # Crear figura
    plt.figure(figsize=(20, 10))  # Figura más ancha para acomodar todas las estaciones
    
    # Colores para masas de agua
    colors = ['#80b1d3',  # AASW - Azul claro
             '#b3de69',   # Glacial Meltwater - Verde claro
             '#fb8072',   # mCDW - Rojo
             '#8dd3c7']   # HSSW - Turquesa
    
    # Crear colormap personalizado
    cmap = ListedColormap(colors)
    
    # Plotear masas de agua
    plt.pcolormesh(dist_grid, depth_grid, grid_predictions,
                  cmap=cmap, shading='auto')
    
    # Plotear batimetría
    plt.fill_between(x_bathy, y_bathy, 1000, color='lightgray', alpha=1.0)
    plt.plot(x_bathy, y_bathy, 'k-', linewidth=1.5)
    
    # Configurar ejes
    plt.gca().invert_yaxis()
    plt.xlabel('Distancia (km)')
    plt.ylabel('Profundidad (m)')
    plt.ylim(1000, 0)
    
    # Añadir estaciones encontradas
    for station, dist in zip(found_stations, found_distances):
        plt.axvline(x=dist, color='gray', linestyle=':', alpha=0.3)
        plt.text(dist, -20, station, ha='center', va='bottom', rotation=90)
    
    # Añadir leyenda
    legend_elements = [plt.Rectangle((0,0), 1, 1, facecolor=color, label=name)
                      for color, name in zip(colors, ['AASW', 'Glacial Meltwater', 'mCDW', 'HSSW'])]
    plt.legend(handles=legend_elements, loc='center left', 
              bbox_to_anchor=(1.02, 0.5))
    
    plt.title('Clasificación de Masas de Agua\nEstrecho de Gerlache', pad=20)
    plt.tight_layout()
    
    # Guardar figura
    os.makedirs('test_outputs', exist_ok=True)
    plt.savefig('test_outputs/nn_water_masses_section.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def main():
    try:
        # Cargar modelo entrenado y scaler
        model = load_model('water_mass_classifier.h5')
        scaler = joblib.load('feature_scaler.pkl')
        
        # Leer datos
        data = pd.read_csv("ocean_analysis/data_tests/datosgerlache_nut.csv", 
                          sep=';', 
                          decimal='.', 
                          encoding='latin-1')
        
        # Crear sección
        create_section_plot(data, model, scaler)
        print("\nSección vertical guardada en: test_outputs/nn_water_masses_section.png")
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("Asegúrate de que el modelo entrenado (water_mass_classifier.h5) y")
        print("el scaler (feature_scaler.pkl) existan en el directorio actual.")
    except Exception as e:
        print(f"\nError inesperado: {e}")

if __name__ == '__main__':
    main() 