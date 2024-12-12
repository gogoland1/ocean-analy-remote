import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.gridspec import GridSpec

def create_distribution_map(data, parameter, title, units, cmap='YlGn', output_name=None):
    """
    Crear mapa de distribución superficial para un parámetro dado
    """
    # Configurar el estilo del mapa
    plt.style.use('seaborn-v0_8-white')

    # Establecer límites del mapa
    lon_min, lon_max = -64.6, -61.5
    lat_min, lat_max = -65.2, -64.0

    # Crear figura
    fig_width = 20
    fig_height = 8
    fig = plt.figure(figsize=(fig_width, fig_height))

    # Crear proyección
    projection = ccrs.PlateCarree(central_longitude=-63.5)
    ax = plt.axes(projection=projection)

    # Establecer límites
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

    # Añadir características del mapa
    land = cfeature.NaturalEarthFeature('physical', 'land', '10m',
                                       edgecolor='black',
                                       facecolor='lightgray',
                                       alpha=1)
    ax.add_feature(land)

    # Añadir solo las etiquetas de los ejes sin ninguna grilla
    gl = ax.gridlines(draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 14}
    gl.ylabel_style = {'size': 14}
    gl.ylocator = plt.MultipleLocator(0.2)
    gl.xlocator = plt.MultipleLocator(0.5)
    gl.xlines = False
    gl.ylines = False

    # Crear scatter plot
    scatter = ax.scatter(data['Longitude [degrees East]'],
                        data['Latitude [degrees North]'],
                        c=data[parameter],
                        cmap=cmap,
                        s=150,
                        edgecolor='black',
                        linewidth=0.5,
                        transform=ccrs.PlateCarree(),
                        zorder=5)

    # Añadir etiquetas de estaciones con nombres
    for _, row in data.iterrows():
        # Punto de la estación
        ax.plot(row['Longitude [degrees East]'],
                row['Latitude [degrees North]'],
                'o',
                color='blue',
                markersize=7,
                transform=ccrs.PlateCarree(),
                zorder=4)
        
        # Etiqueta de la estación
        ax.text(row['Longitude [degrees East]'] + 0.02,
                row['Latitude [degrees North]'] + 0.02,
                row['Station '].strip(),
                fontsize=8,
                transform=ccrs.PlateCarree(),
                zorder=6)

    # Configurar etiquetas
    ax.set_xlabel('Longitud (°W)', size=16)
    ax.set_ylabel('Latitud (°S)', size=16)

    # Ajustar el tamaño y posición de la barra de color
    pos = ax.get_position()
    cax = fig.add_axes([pos.x1 + 0.02,
                        pos.y0,
                        0.015,
                        pos.height])
    cbar = plt.colorbar(scatter, cax=cax)
    cbar.set_label(f'{title} ({units})', size=16)
    cbar.ax.tick_params(labelsize=14)

    # Ajustar la posición del mapa para dejar espacio a los títulos
    ax.set_position([pos.x0, pos.y0, pos.width, pos.height])

    # Añadir títulos con posición ajustada
    fig.text(0.5, 0.95, f'Distribución superficial de {title.lower()}', 
             ha='center', va='bottom', size=18)
    fig.text(0.5, 0.90, 'Estrecho de Gerlache Verano Austral 2020', 
             ha='center', va='bottom', size=16)

    # Guardar figura
    output_filename = f'test_outputs/surface_distribution_{output_name}_map.png'
    plt.savefig(output_filename,
                dpi=600,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none',
                pad_inches=0.1)
    plt.close()

# Crear directorio de salida si no existe
os.makedirs('test_outputs', exist_ok=True)

# Leer datos
df = pd.read_csv("ocean_analysis/data_tests/datosgerlache_nut.csv", 
                 sep=';', 
                 decimal='.', 
                 encoding='latin-1')

# Filtrar datos superficiales (0.5 dbar)
surface_data = df[np.isclose(df['pressure [db]'], 0.5)].copy()

# Definir parámetros a graficar
parameters = [
    ('Chl-A [ug/L]', 'clorofila-a', 'μg/L', 'YlGn', 'chlorophyll'),
    ('nitrate', 'nitrato', 'μM', 'YlOrRd', 'nitrate'),
    ('phosphate', 'fosfato', 'μM', 'RdPu', 'phosphate'),
    ('silicate', 'silicato', 'μM', 'BuPu', 'silicate'),
    ('dFe [nM]', 'dFe', 'nM', 'OrRd', 'dfe'),
    ('dMn[nM]', 'dMn', 'nM', 'PuRd', 'dmn')
]

# Crear mapas para cada parámetro
for param, title, units, cmap, output_name in parameters:
    create_distribution_map(surface_data, param, title, units, cmap, output_name)
    print(f"\nInformación de datos superficiales de {title}:")
    print("\nEstación  Latitud   Longitud   Valor")
    print("-" * 40)
    for _, row in surface_data.sort_values('Station ').iterrows():
        print(f"{row['Station ']:8} {row['Latitude [degrees North]']:8.3f} "
              f"{row['Longitude [degrees East]']:9.3f} {row[param]:8.2f}") 