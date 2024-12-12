from ocean_analysis.agents import ParserAgent, QAAgent, WaterMassAgent, StatsAgent, AnalystAgent
import logging
import os
from pathlib import Path
import numpy as np
import pandas as pd
import asyncio
import matplotlib.pyplot as plt

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def plot_ctd_profile(data, output_dir):
    """Genera perfil CTD para una estación"""
    try:
        # Crear figura con dos subplots
        fig = plt.figure(figsize=(12, 8))
        
        # Ajustar los márgenes para bajar la figura
        plt.subplots_adjust(top=0.85)  # Reducir el margen superior
        
        # Crear los subplots con posición específica
        ax1 = fig.add_subplot(121)  # 1x2 grid, primera posición
        ax2 = fig.add_subplot(122)  # 1x2 grid, segunda posición
        
        # Configuración común para ambos ejes
        for ax in [ax1, ax2]:
            ax.grid(True, linestyle=':', alpha=0.7, color='gray')
            ax.spines['top'].set_visible(True)
            ax.spines['right'].set_visible(False)
            ax.xaxis.set_ticks_position('top')
            ax.xaxis.set_label_position('top')
        
        # Perfil de Temperatura
        ax1.plot(data['temperature'], data['depth'], 'b-', linewidth=2, label='Temperatura')
        ax1.set_xlabel('Temperatura (°C)')
        ax1.set_ylabel('Profundidad (m)')
        ax1.set_xlim(-2, 4)  # Rango de temperatura ajustado
        ax1.set_ylim(-250, 0)  # Rango de profundidad
        
        # Perfil de Salinidad
        ax2.plot(data['salinity'], data['depth'], 'm-', linewidth=2, label='Salinidad')
        ax2.set_xlabel('Salinidad (PSU)')
        ax2.set_xlim(33, 35)  # Rango de salinidad
        ax2.set_ylim(-250, 0)  # Rango de profundidad
        
        # Agregar leyendas
        ax1.legend(loc='lower right')
        ax2.legend(loc='lower right')
        
        # Agregar título
        plt.suptitle(f"Perfiles CTD - Estación {data['metadata']['station']}", y=0.95)
        
        # Agregar información de la estación
        info_text = f"Fecha: {data['metadata']['date']}\n"
        info_text += f"Lat: {data['metadata']['latitude']:.3f}°N\n"
        info_text += f"Lon: {data['metadata']['longitude']:.3f}°E\n"
        info_text += f"Prof. fondo: {data['metadata']['bottom_depth']}m"
        
        plt.figtext(0.02, 0.02, info_text, fontsize=8, va='bottom')
        
        # Ajustar espaciado
        plt.tight_layout()
        
        # Guardar figura
        output_path = output_dir / 'ctd_profile_GS18.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Error generando perfil CTD: {str(e)}")
        raise

async def process_data():
    # Configurar rutas
    data_file = Path("ocean_analysis/data/raw/datos_gerlache.csv")
    output_dir = Path("output_gerlache")
    
    # Crear directorios de salida
    output_dirs = {
        'main': output_dir,
        'figures': output_dir / 'figures'
    }
    
    # Crear todos los directorios necesarios
    for dir_path in output_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio creado: {dir_path}")
    
    try:
        logger.info("Iniciando procesamiento de datos del Gerlache...")
        
        # 1. Parseo de datos
        logger.info("Procesando archivo de datos...")
        
        # Leer el archivo con la configuración correcta
        df = pd.read_csv(data_file, 
                        encoding='latin-1',
                        sep=';',
                        decimal='.')
        
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Filtrar solo la estación GS18
        df = df[df['Station'] == 'GS18']
        
        if len(df) == 0:
            raise ValueError("No se encontraron datos para la estación GS18")
            
        logger.info(f"Procesando {len(df)} registros de la estación GS18")
        
        # Crear el diccionario de datos en el formato esperado
        data = {
            'temperature': df['temperature [ºC]'].values,
            'salinity': df['salinity [PSU]'].values,
            'depth': df['depth [m]'].values,
            'metadata': {
                'station': df['Station'].iloc[0],
                'date': df['dd/mm/yyyy'].iloc[0],
                'latitude': df['Latitude [degrees North]'].iloc[0],
                'longitude': df['Longitude [degrees East]'].iloc[0],
                'bottom_depth': df['Bot. Depth [m]'].iloc[0]
            }
        }
        
        # Generar perfil CTD
        logger.info("Generando perfil CTD...")
        profile_path = plot_ctd_profile(data, output_dirs['figures'])
        logger.info(f"Perfil CTD guardado en: {profile_path}")
        
        # Mostrar resumen de datos
        logger.info("\nResumen de datos procesados:")
        for var in ['temperature', 'salinity', 'depth']:
            if var in data:
                data_array = data[var]
                logger.info(f"{var.capitalize()}:")
                logger.info(f"  Media: {np.mean(data_array):.2f}")
                logger.info(f"  Min: {np.min(data_array):.2f}")
                logger.info(f"  Max: {np.max(data_array):.2f}")
        
        # Mostrar metadata
        logger.info("\nMetadata de la estación GS18:")
        for key, value in data['metadata'].items():
            logger.info(f"  {key}: {value}")
        
    except Exception as e:
        logger.error(f"Error durante el procesamiento: {str(e)}")
        raise

def main():
    asyncio.run(process_data())

if __name__ == "__main__":
    main() 