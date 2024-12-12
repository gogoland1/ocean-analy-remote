import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def plot_station_ctd(data_file, station_name, output_dir='output_ctd'):
    """
    Genera perfiles CTD para una estación específica
    
    Args:
        data_file: Ruta al archivo de datos
        station_name: Nombre de la estación a procesar
        output_dir: Directorio de salida para las figuras
    """
    # Crear directorio de salida si no existe
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Leer datos
    print(f"Leyendo datos de {data_file}...")
    df = pd.read_csv(data_file, sep=';', decimal='.', encoding='latin-1')
    
    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()
    
    # Filtrar estación
    station_data = df[df['Station'] == station_name].copy()
    
    if len(station_data) == 0:
        print(f"No se encontraron datos para la estación {station_name}")
        # Mostrar estaciones disponibles
        print("\nEstaciones disponibles:")
        print(df['Station'].unique())
        return
    
    print(f"\nProcesando estación {station_name}")
    print(f"Número de registros: {len(station_data)}")
    
    # Obtener metadata
    metadata = {
        'station': station_name,
        'date': station_data['dd/mm/yyyy'].iloc[0],
        'latitude': station_data['Latitude [degrees North]'].iloc[0],
        'longitude': station_data['Longitude [degrees East]'].iloc[0],
        'bottom_depth': station_data['Bot. Depth [m]'].iloc[0]
    }
    
    # Crear figura
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))
    
    # Configuración común para ambos ejes
    for ax in [ax1, ax2]:
        ax.grid(True, linestyle=':', alpha=0.7)
        ax.invert_yaxis()  # Invertir eje y para mostrar profundidad correctamente
    
    # Graficar temperatura
    ax1.plot(station_data['temperature [ºC]'], station_data['depth [m]'], 
            'b-', linewidth=2, label='Temperatura')
    ax1.set_xlabel('Temperatura (°C)')
    ax1.set_ylabel('Profundidad (m)')
    ax1.legend(loc='lower right')
    
    # Graficar salinidad
    ax2.plot(station_data['salinity [PSU]'], station_data['depth [m]'], 
            'm-', linewidth=2, label='Salinidad')
    ax2.set_xlabel('Salinidad (PSU)')
    ax2.legend(loc='lower right')
    
    # Ajustar límites de los ejes
    temp_range = station_data['temperature [ºC]'].agg(['min', 'max'])
    sal_range = station_data['salinity [PSU]'].agg(['min', 'max'])
    depth_range = station_data['depth [m]'].agg(['min', 'max'])
    
    # Agregar un pequeño margen a los rangos
    temp_margin = (temp_range['max'] - temp_range['min']) * 0.1
    sal_margin = (sal_range['max'] - sal_range['min']) * 0.1
    
    ax1.set_xlim(temp_range['min'] - temp_margin, temp_range['max'] + temp_margin)
    ax2.set_xlim(sal_range['min'] - sal_margin, sal_range['max'] + sal_margin)
    
    # Establecer límites de profundidad
    max_depth = min(depth_range['max'] * 1.1, metadata['bottom_depth'])
    ax1.set_ylim(max_depth, 0)
    ax2.set_ylim(max_depth, 0)
    
    # Agregar título
    plt.suptitle(f'Perfiles CTD - Estación {station_name}', y=0.95)
    
    # Agregar información de la estación
    info_text = (f"Fecha: {metadata['date']}\n"
                f"Lat: {metadata['latitude']:.3f}°N\n"
                f"Lon: {metadata['longitude']:.3f}°E\n"
                f"Prof. fondo: {metadata['bottom_depth']}m")
    
    plt.figtext(0.02, 0.02, info_text, fontsize=8, va='bottom')
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    output_file = output_path / f'ctd_profile_{station_name}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPerfil guardado en: {output_file}")
    
    # Mostrar estadísticas
    print("\nEstadísticas:")
    print(f"Temperatura: {temp_range['min']:.2f}°C a {temp_range['max']:.2f}°C")
    print(f"Salinidad: {sal_range['min']:.2f} a {sal_range['max']:.2f} PSU")
    print(f"Profundidad: {depth_range['min']:.1f}m a {depth_range['max']:.1f}m")
    
    plt.close()

if __name__ == "__main__":
    # Configurar rutas
    data_file = "ocean_analysis/data/raw/datos_gerlache.csv"
    
    # Procesar estación GS18
    plot_station_ctd(data_file, "GS18") 