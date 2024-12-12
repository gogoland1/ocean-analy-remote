import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analyze_variable_ranges(data):
    """
    Analizar rangos de variables oceanográficas
    """
    variables = {
        'Temperatura': 'Pot. Temp. [ºC]',
        'Salinidad': 'salinity [PSU]',
        'Oxígeno': 'O2[umol/kg]',
        'Silicato': 'silicate',
        'Nitrato': 'nitrate',
        'Fosfato': 'phosphate'
    }
    
    print("\nRangos de variables:")
    print("-" * 50)
    
    for name, var in variables.items():
        values = data[var].dropna()
        print(f"\n{name}:")
        print(f"  Mínimo: {values.min():.2f}")
        print(f"  Máximo: {values.max():.2f}")
        print(f"  Media: {values.mean():.2f}")
        print(f"  Mediana: {values.median():.2f}")
        
        # Calcular percentiles
        percentiles = [5, 25, 75, 95]
        percs = np.percentile(values, percentiles)
        for p, v in zip(percentiles, percs):
            print(f"  Percentil {p}: {v:.2f}")

def plot_ts_diagram(data):
    """
    Crear diagrama T-S coloreado por oxígeno
    """
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(data['salinity [PSU]'], 
                         data['Pot. Temp. [ºC]'],
                         c=data['O2[umol/kg]'], 
                         cmap='viridis', 
                         alpha=0.6)
    plt.colorbar(scatter, label='Oxígeno [μmol/kg]')
    plt.xlabel('Salinidad [PSU]')
    plt.ylabel('Temperatura Potencial [°C]')
    plt.title('Diagrama T-S coloreado por Oxígeno')
    plt.grid(True, alpha=0.3)
    plt.savefig('ts_diagram_analysis.png')
    plt.close()

def analyze_correlations(data):
    """
    Analizar correlaciones entre variables
    """
    variables = ['Pot. Temp. [ºC]', 'salinity [PSU]', 'O2[umol/kg]',
                'silicate', 'nitrate', 'phosphate']
    
    corr = data[variables].corr()
    
    print("\nCorrelaciones importantes:")
    print("-" * 50)
    
    for i in range(len(variables)):
        for j in range(i+1, len(variables)):
            corr_val = corr.iloc[i, j]
            if abs(corr_val) > 0.5:  # Solo mostrar correlaciones significativas
                print(f"\n{variables[i]} vs {variables[j]}:")
                print(f"  Correlación: {corr_val:.3f}")

def main():
    # Leer datos
    data = pd.read_csv("ocean_analysis/data_tests/datosgerlache_nut.csv", 
                      sep=';', 
                      decimal='.', 
                      encoding='latin-1')
    
    # Analizar rangos
    analyze_variable_ranges(data)
    
    # Crear diagrama T-S
    plot_ts_diagram(data)
    
    # Analizar correlaciones
    analyze_correlations(data)
    
    # Analizar distribución por profundidad
    print("\nDistribución por profundidad:")
    print("-" * 50)
    depth_ranges = [(0, 50), (50, 100), (100, 200), (200, 500)]
    
    for min_d, max_d in depth_ranges:
        mask = (data['pressure [db]'] >= min_d) & (data['pressure [db]'] < max_d)
        n_samples = mask.sum()
        print(f"\nProfundidad {min_d}-{max_d} m ({n_samples} muestras):")
        if n_samples > 0:
            depth_data = data[mask]
            print(f"  Temperatura: {depth_data['Pot. Temp. [ºC]'].mean():.2f}°C")
            print(f"  Salinidad: {depth_data['salinity [PSU]'].mean():.2f} PSU")
            print(f"  Oxígeno: {depth_data['O2[umol/kg]'].mean():.2f} μmol/kg")

if __name__ == '__main__':
    main() 