import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def create_subplot_map(fig, rows, cols, index, data, parameter, title, units, cmap='YlGn'):
    """
    Crear mapa de distribución superficial para un parámetro dado como subplot
    """
    # Establecer límites del mapa
    lon_min, lon_max = -64.6, -61.5
    lat_min, lat_max = -65.2, -64.0

    # Crear proyección
    projection = ccrs.PlateCarree(central_longitude=-63.5)
    
    # Crear subplot
    ax = fig.add_subplot(rows, cols, index, projection=projection)
    
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
    gl.xlabel_style = {'size': 10}
    gl.ylabel_style = {'size': 10}
    gl.ylocator = plt.MultipleLocator(0.2)
    gl.xlocator = plt.MultipleLocator(0.5)
    gl.xlines = False
    gl.ylines = False

    # Crear scatter plot
    scatter = ax.scatter(data['Longitude [degrees East]'],
                        data['Latitude [degrees North]'],
                        c=data[parameter],
                        cmap=cmap,
                        s=100,
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
                markersize=5,
                transform=ccrs.PlateCarree(),
                zorder=4)
        
        # Etiqueta de la estación
        ax.text(row['Longitude [degrees East]'] + 0.02,
                row['Latitude [degrees North]'] + 0.02,
                row['Station '].strip(),
                fontsize=6,
                transform=ccrs.PlateCarree(),
                zorder=6)

    # Configurar etiquetas
    ax.set_xlabel('Longitud (°W)', size=12)
    ax.set_ylabel('Latitud (°S)', size=12)

    # Añadir título del subplot
    ax.set_title(f'{title} ({units})', size=12, pad=10)

    return ax, scatter

# Crear directorio de salida si no existe
os.makedirs('test_outputs', exist_ok=True)

# Leer datos
df = pd.read_csv("ocean_analysis/data_tests/datosgerlache_nut.csv", 
                 sep=';', 
                 decimal='.', 
                 encoding='latin-1')

# Filtrar datos superficiales (0.5 dbar)
surface_data = df[np.isclose(df['pressure [db]'], 0.5)].copy()

# Configurar el estilo del mapa
plt.style.use('seaborn-v0_8-white')

# Crear figura con subplots
fig = plt.figure(figsize=(20, 18))  # Aumentado el alto para acomodar las colorbars
plt.subplots_adjust(hspace=0.3, wspace=0.1)

# Definir parámetros a graficar con sus descripciones
parameters = [
    ('Chl-A [ug/L]', 'Clorofila-a', 'μg/L', 'YlGn', 'Pigmento fotosintético'),
    ('nitrate', 'Nitrato', 'μM', 'YlOrRd', 'Nutriente limitante del crecimiento fitoplanctónico'),
    ('dFe [nM]', 'dFe', 'nM', 'OrRd', 'Hierro disuelto - micronutriente esencial'),
    ('dMn[nM]', 'dMn', 'nM', 'PuRd', 'Manganeso disuelto - trazador de fuentes hidrotermales')
]

# Crear subplots y guardar los objetos scatter
scatters = []
axes = []

# Crear subplots
for i, (param, title, units, cmap, desc) in enumerate(parameters, 1):
    ax, scatter = create_subplot_map(fig, 2, 2, i, data=surface_data, 
                                   parameter=param, title=title, 
                                   units=units, cmap=cmap)
    scatters.append((scatter, title, units, desc))
    axes.append(ax)

# Ajustar título general
plt.suptitle('Distribución superficial de variables\nEstrecho de Gerlache Verano Austral 2020', 
             size=16, y=0.95)

# Obtener la posición del último subplot para referencia
last_ax = axes[-1]
pos = last_ax.get_position()

# Calcular posiciones para las colorbars horizontales
colorbar_width = pos.width * 0.6  # Reducido para dejar espacio a la leyenda
spacing = 0.02  # Espacio entre colorbars
bottom_margin = 0.08  # Margen inferior

for i, (scatter, title, units, desc) in enumerate(scatters):
    # Calcular posición para cada colorbar
    y_pos = bottom_margin + i * spacing
    x_pos = (1.0 - colorbar_width) / 2  # Centrar horizontalmente
    
    # Crear axes para la colorbar
    cax = fig.add_axes([x_pos, y_pos, colorbar_width, 0.015])
    
    # Añadir colorbar horizontal
    cbar = plt.colorbar(scatter, cax=cax, orientation='horizontal')
    cbar.ax.tick_params(labelsize=10)
    
    # Añadir título de la variable y descripción
    fig.text(x_pos + colorbar_width + 0.02, y_pos + 0.007, 
             f'{title}: {desc}', 
             va='center', ha='left', size=10)

# Guardar figura
plt.savefig('test_outputs/combined_surface_distributions.png',
            dpi=600,
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none')
plt.close() 