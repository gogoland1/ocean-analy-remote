# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import ListedColormap
import tensorflow as tf
import joblib
from scipy.interpolate import griddata

def load_data():
    """Cargar y preparar datos"""
    data = pd.read_csv("ocean_analysis/data_tests/datosgerlache_nut.csv", 
                      sep=';', decimal='.', encoding='latin-1')
    
    # Mapear estaciones a distancias
    station_map = {
        'GS1': 0, 'GS16': 15, 'GS20': 30,
        'GS26': 45, 'GS30': 60
    }
    data['Distance'] = data['Station '].map(station_map)
    data['Depth'] = data['pressure [db]']
    
    return data

def create_grid(data):
    """Crear grid para interpolación"""
    depths = np.arange(0, 1000, 10)
    distances = np.arange(0, 65, 1)
    dist_grid, depth_grid = np.meshgrid(distances, depths)
    
    # Interpolar variables
    points = np.column_stack((data['Distance'], data['Depth']))
    temp_grid = griddata(points, data['Pot. Temp. [ºC]'], 
                        (dist_grid, depth_grid), method='linear')
    sal_grid = griddata(points, data['salinity [PSU]'], 
                       (dist_grid, depth_grid), method='linear')
    o2_grid = griddata(points, data['O2[umol/kg]'], 
                      (dist_grid, depth_grid), method='linear')
    
    return dist_grid, depth_grid, temp_grid, sal_grid, o2_grid

def predict_masses(temp_grid, sal_grid, o2_grid):
    """Predecir masas de agua"""
    model = tf.keras.models.load_model('water_mass_classifier.h5')
    scaler = joblib.load('feature_scaler.pkl')
    
    # Preparar datos
    features = np.vstack([
        temp_grid.flatten(),
        sal_grid.flatten(),
        o2_grid.flatten()
    ]).T
    
    # Manejar NaNs
    valid = ~np.isnan(features).any(axis=1)
    features_valid = features[valid]
    
    # Predecir
    features_scaled = scaler.transform(features_valid)
    predictions = model.predict(features_scaled)
    masses = np.argmax(predictions, axis=1)
    
    # Reconstruir grid
    result = np.full(temp_grid.size, np.nan)
    result[valid] = masses
    return result.reshape(temp_grid.shape)

def plot_section(dist_grid, depth_grid, masses):
    """Crear visualización"""
    plt.figure(figsize=(15, 10))
    
    # Colores para masas de agua
    colors = ['#80b1d3',  # AASW - Azul claro
             '#b3de69',   # GMW - Verde claro
             '#fb8072',   # mCDW - Rojo
             '#8dd3c7']   # HSSW - Turquesa
    
    # Plotear masas de agua
    plt.pcolormesh(dist_grid, depth_grid, masses,
                  cmap=ListedColormap(colors), shading='auto')
    
    # Estaciones
    stations = ['GS1', 'GS16', 'GS20', 'GS26', 'GS30']
    distances = [0, 15, 30, 45, 60]
    
    for dist, name in zip(distances, stations):
        plt.axvline(x=dist, color='gray', linestyle='--', alpha=0.5)
        plt.text(dist, -50, name, ha='center', va='bottom', rotation=90)
    
    # Configuración
    plt.gca().invert_yaxis()
    plt.xlabel('Distancia (km)')
    plt.ylabel('Profundidad (m)')
    plt.ylim(1000, 0)
    plt.xlim(0, 60)
    
    # Leyenda
    legend = [plt.Rectangle((0,0),1,1, fc=c) for c in colors]
    plt.legend(legend, ['AASW', 'GMW', 'mCDW', 'HSSW'],
              loc='lower right', bbox_to_anchor=(1.15, 0))
    
    plt.title('Distribución de Masas de Agua\nEstrecho de Gerlache', pad=20)
    plt.tight_layout()
    
    # Guardar
    plt.savefig('water_masses_section.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Cargar datos
    data = load_data()
    
    # Crear grid e interpolar
    dist_grid, depth_grid, temp_grid, sal_grid, o2_grid = create_grid(data)
    
    # Predecir masas de agua
    masses = predict_masses(temp_grid, sal_grid, o2_grid)
    
    # Crear visualización
    plot_section(dist_grid, depth_grid, masses)

if __name__ == '__main__':
    main()
