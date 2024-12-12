import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.interpolate import griddata, interp1d
import os

def create_vertical_section(df, stations, variable='temperature', 
                          cmap='RdYlBu_r', title=None, highlight_value=None):
    """
    Crear una sección vertical para una variable dada
    
    Args:
        df: DataFrame con los datos
        stations: Lista de estaciones a incluir en la sección
        variable: Variable a graficar
        cmap: Mapa de colores
        title: Título de la figura
        highlight_value: Valor específico a destacar
    """
    # Crear directorio de salida si no existe
    os.makedirs('test_outputs', exist_ok=True)
    
    # Filtrar datos para las estaciones seleccionadas
    section_data = df[df['Station '].isin(stations)].copy()
    
    # Calcular la distancia acumulada entre estaciones
    distances = []
    current_distance = 0
    prev_lat = None
    prev_lon = None
    
    # Recolectar profundidades del fondo
    bottom_depths = []
    
    for station in stations:
        station_data = section_data[section_data['Station '] == station].iloc[0]
        lat = station_data['Latitude [degrees North]']
        lon = station_data['Longitude [degrees East]']
        bottom_depths.append(station_data['Bot. Depth [m]'])
        
        if prev_lat is not None and prev_lon is not None:
            # Calcular distancia en km usando la fórmula del haversine
            R = 6371  # Radio de la Tierra en km
            dlat = np.radians(lat - prev_lat)
            dlon = np.radians(lon - prev_lon)
            a = (np.sin(dlat/2)**2 + 
                 np.cos(np.radians(prev_lat)) * np.cos(np.radians(lat)) * 
                 np.sin(dlon/2)**2)
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            distance = R * c
            current_distance += distance
            
        distances.append(current_distance)
        prev_lat = lat
        prev_lon = lon
    
    # Crear grilla para interpolación
    xi = np.linspace(0, max(distances), 100)
    yi = np.linspace(0, 500, 100)  # Profundidad máxima
    xi, yi = np.meshgrid(xi, yi)
    
    # Preparar datos para interpolación
    x = []
    y = []
    z = []
    
    for station, dist in zip(stations, distances):
        station_data = section_data[section_data['Station '] == station]
        for _, row in station_data.iterrows():
            x.append(dist)
            y.append(row['pressure [db]'])
            z.append(row[variable])
    
    # Interpolar datos
    zi = griddata((x, y), z, (xi, yi), method='cubic')
    
    # Crear figura con dos subplots
    fig = plt.figure(figsize=(20, 16))
    
    # Subplot superior: Sección vertical
    ax1 = plt.subplot(2, 1, 1)
    
    # Interpolar batimetría primero
    f_bathy = interp1d(distances, bottom_depths, kind='cubic', 
                      bounds_error=False, fill_value='extrapolate')
    x_bathy = np.linspace(0, max(distances), 200)
    y_bathy = f_bathy(x_bathy)
    
    # Crear máscara para los datos debajo de la batimetría
    bathy_interp = f_bathy(xi[0])
    mask = yi > np.tile(bathy_interp, (yi.shape[0], 1))
    zi_masked = np.ma.masked_where(mask, zi)
    
    # Plotear sección vertical con relleno de colores
    levels_fill = np.linspace(np.nanmin(zi), np.nanmax(zi), 20)
    cf = ax1.contourf(xi, yi, zi_masked, levels=levels_fill, cmap=cmap, extend='both')
    
    # Añadir isolíneas (excepto el valor destacado)
    levels_contour = np.arange(np.floor(np.nanmin(zi)*10)/10, 
                              np.ceil(np.nanmax(zi)*10)/10 + 0.1, 
                              0.1)
    if highlight_value is not None:
        levels_contour = levels_contour[levels_contour != highlight_value]
    cs = ax1.contour(xi, yi, zi_masked, levels=levels_contour, colors='k', 
                     linewidths=0.5, alpha=0.7)
    ax1.clabel(cs, fmt='%.1f', fontsize=8, colors='k', inline=True, inline_spacing=10)
    
    # Destacar isolínea específica si se proporciona
    if highlight_value is not None:
        cs_highlight = ax1.contour(xi, yi, zi_masked, levels=[highlight_value], 
                                 colors='k', linewidths=2)
        ax1.clabel(cs_highlight, fmt=f'{highlight_value}', fontsize=10, 
                  colors='k', inline=True, inline_spacing=10)
    
    # Plotear batimetría como área sombreada
    ax1.fill_between(x_bathy, y_bathy, 500, color='lightgray', alpha=1.0)
    # Añadir línea negra para el contorno del fondo
    ax1.plot(x_bathy, y_bathy, 'k-', linewidth=1.5)
    
    # Configurar ejes
    ax1.invert_yaxis()
    ax1.set_xlabel('Distancia [km]')
    ax1.set_ylabel('Profundidad [m]')
    ax1.set_ylim(500, 0)  # Fijar límite de profundidad
    
    # Añadir barra de color
    cbar = plt.colorbar(cf, ax=ax1, orientation='vertical', pad=0.02)
    cbar.set_label(variable)
    
    # Marcar posiciones de las estaciones
    for station, dist in zip(stations, distances):
        ax1.axvline(x=dist, color='gray', linestyle='--', alpha=0.5)
        ax1.text(dist, -10, station, rotation=45, ha='right')
    
    # Subplot inferior: Mapa con la sección
    ax2 = plt.subplot(2, 1, 2, projection=ccrs.PlateCarree())
    
    # Añadir características del mapa
    ax2.add_feature(cfeature.LAND, facecolor='lightgray')
    ax2.add_feature(cfeature.COASTLINE)
    
    # Establecer límites del mapa
    lon_min = section_data['Longitude [degrees East]'].min() - 0.5
    lon_max = section_data['Longitude [degrees East]'].max() + 0.5
    lat_min = section_data['Latitude [degrees North]'].min() - 0.2
    lat_max = section_data['Latitude [degrees North]'].max() + 0.2
    ax2.set_extent([lon_min, lon_max, lat_min, lat_max])
    
    # Plotear estaciones y línea de sección
    lons = section_data.groupby('Station ')['Longitude [degrees East]'].first()
    lats = section_data.groupby('Station ')['Latitude [degrees North]'].first()
    
    # Línea de sección
    ax2.plot(lons, lats, 'r-', transform=ccrs.PlateCarree(), linewidth=2)
    
    # Estaciones
    ax2.plot(lons, lats, 'bo', transform=ccrs.PlateCarree(), markersize=8)
    
    # Etiquetas de estaciones
    for station in stations:
        station_data = section_data[section_data['Station '] == station].iloc[0]
        ax2.text(station_data['Longitude [degrees East]'] + 0.02,
                station_data['Latitude [degrees North]'] + 0.02,
                station,
                transform=ccrs.PlateCarree())
    
    # Añadir grid
    gl = ax2.gridlines(draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
    
    # Título general
    if title:
        plt.suptitle(title, size=16, y=0.95)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    output_path = 'test_outputs/vertical_section.png'
    plt.savefig(output_path, 
                dpi=300, 
                bbox_inches='tight',
                facecolor='white')
    plt.close()
    
    print(f"\nFigura guardada en: {os.path.abspath(output_path)}")

# Leer datos
df = pd.read_csv("ocean_analysis/data_tests/datosgerlache_nut.csv", 
                 sep=';', 
                 decimal='.', 
                 encoding='latin-1')

# Definir estaciones para la sección (siguiendo la línea roja del mapa)
stations = ['GS29', 'GS28', 'GS27', 'GS26', 'GS25', 'GS24', 
           'GS23', 'GS22', 'GS21', 'GS20', 'GS19', 'GS18']

# Crear sección vertical
create_vertical_section(
    df, 
    stations,
    variable='salinity [PSU]',
    cmap='viridis',  # Paleta de colores adecuada para salinidad
    title='Sección Vertical de Salinidad\nEstrecho de Gerlache - Verano Austral 2020',
    highlight_value=34.6
) 