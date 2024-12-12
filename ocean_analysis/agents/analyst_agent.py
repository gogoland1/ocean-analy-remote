from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
import gsw  # Para cálculos oceanográficos
import cmocean  # Paletas de colores oceanográficas
from scipy import signal
from pathlib import Path
from dataclasses import dataclass
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.interpolate import griddata
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
import zipfile
import shutil
from datetime import datetime
import json
import logging

@dataclass
class AnalysisConfig:
    """Configuración para análisis oceanográficos"""
    mld_method: str = 'density'  # 'density' o 'temperature'
    mld_threshold: float = 0.03  # kg/m³ para densidad, °C para temperatura
    spice_method: str = 'gsw'    # Método para cálculo de spiciness
    plot_style: str = 'paper'    # 'paper' o 'presentation'
    colormap: str = 'deep'       # Paleta de colores por defecto

class AnalystAgent:
    """Agente para análisis y visualización de datos oceanográficos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {
            'depth_bins': [-10, -50, -100, -200, -500, -1000],
            'grid_resolution': 0.5,  # grados
            'interpolation_method': 'linear',
            'colormap': 'RdYlBu_r',
            'figure_dpi': 300,
            'figure_format': 'png'
        }
        self.output_dir = None
        
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configura el agente con parámetros específicos
        
        Args:
            config: Diccionario con configuración
        """
        self.config.update(config)
        
    def set_output_dir(self, output_dir: Path) -> None:
        """Configura el directorio de salida"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear subdirectorios necesarios
        (self.output_dir / 'figures').mkdir(exist_ok=True)
        
    def plot_ctd_profiles(self, data: Dict[str, np.ndarray], output_dir: Path) -> Dict[str, str]:
        """
        Genera perfiles verticales de CTD con énfasis en las clinas
        
        Args:
            data: Diccionario con datos oceanográficos
            output_dir: Directorio para guardar las figuras
        
        Returns:
            Dict con rutas a las figuras generadas
        """
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
            ax1.set_xlim(10, 20)  # Rango de temperatura ajustado
            ax1.set_ylim(-500, 0)  # Rango de profundidad
            
            # Perfil de Salinidad
            ax2.plot(data['salinity'], data['depth'], 'm-', linewidth=2, label='Salinidad')
            ax2.set_xlabel('Salinidad (PSU)')
            ax2.set_xlim(34.5, 35.5)  # Rango de salinidad
            ax2.set_ylim(-500, 0)  # Rango de profundidad
            
            # Agregar leyendas
            ax1.legend(loc='lower right')
            ax2.legend(loc='lower right')
            
            # Ajustar espaciado
            plt.tight_layout()
            
            # Guardar figura
            output_path = output_dir / 'ctd_profiles.png'
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return {'ctd_profiles': str(output_path)}
            
        except Exception as e:
            self.logger.error(f"Error generando perfiles CTD: {str(e)}")
            raise
            
    async def analyze(self, data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Realiza análisis oceanográfico completo
        
        Args:
            data: Diccionario con datos limpios
            
        Returns:
            Dict con resultados del análisis
        """
        try:
            if self.output_dir is None:
                raise ValueError("No se ha configurado el directorio de salida")
                
            # Crear directorio para figuras
            figures_dir = self.output_dir / 'figures'
            figures_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar visualizaciones
            figures = {}
            
            # 1. Perfiles CTD
            ctd_profiles = self.plot_ctd_profiles(data, figures_dir)
            figures['ctd_profiles'] = ctd_profiles['ctd_profiles']
            
            # 2. Diagrama T-S
            ts_diagram = self._plot_ts_diagram(data, figures_dir)
            figures['ts_diagram'] = ts_diagram
            
            # 3. Secciones verticales
            vertical_sections = self._plot_vertical_sections(data, figures_dir)
            figures['vertical_sections'] = vertical_sections
            
            # 4. Distribución espacial
            spatial_distribution = self._plot_spatial_distribution(data, figures_dir)
            figures['spatial_distribution'] = spatial_distribution
            
            # Calcular estadísticas básicas
            stats = {
                'temperature': {
                    'mean': float(np.mean(data['temperature'])),
                    'std': float(np.std(data['temperature'])),
                    'min': float(np.min(data['temperature'])),
                    'max': float(np.max(data['temperature']))
                },
                'salinity': {
                    'mean': float(np.mean(data['salinity'])),
                    'std': float(np.std(data['salinity'])),
                    'min': float(np.min(data['salinity'])),
                    'max': float(np.max(data['salinity']))
                }
            }
            
            # Calcular correlaciones
            correlations = {
                'temp_sal': float(np.corrcoef(data['temperature'], data['salinity'])[0,1]),
                'temp_depth': float(np.corrcoef(data['temperature'], data['depth'])[0,1]),
                'sal_depth': float(np.corrcoef(data['salinity'], data['depth'])[0,1])
            }
            
            return {
                'statistics': stats,
                'correlations': correlations,
                'visualizations': {
                    'figures': figures
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error en análisis: {str(e)}")
            raise
    
    def _plot_vertical_section(self, temp: np.ndarray, depth: np.ndarray) -> plt.Figure:
        """Genera sección vertical de temperatura"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Crear grilla para la sección
        n_stations = len(temp)
        distance = np.linspace(0, 100, n_stations)  # km
        depth_grid = np.array(self.config['depth_bins'])
        
        # Interpolar temperatura en la grilla
        temp_grid = np.zeros((len(depth_grid), n_stations))
        for i in range(n_stations):
            temp_grid[:, i] = np.interp(depth_grid, depth, temp)
        
        # Plotear sección
        dist_grid, z_grid = np.meshgrid(distance, depth_grid)
        c = ax.pcolormesh(dist_grid, z_grid, temp_grid, 
                         cmap=self.config['colormap'], shading='auto')
        plt.colorbar(c, label='Temperatura (°C)')
        
        ax.set_xlabel('Distancia (km)')
        ax.set_ylabel('Profundidad (m)')
        
        plt.tight_layout()
        return fig
    
    def _plot_ts_diagram(self, data: Dict[str, np.ndarray], output_dir: Path) -> str:
        """Genera diagrama T-S"""
        plt.figure(figsize=(8, 6))
        plt.scatter(data['salinity'], data['temperature'], c=data['depth'], 
                   cmap='viridis', alpha=0.6)
        plt.colorbar(label='Profundidad (m)')
        plt.xlabel('Salinidad (PSU)')
        plt.ylabel('Temperatura (°C)')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        output_path = output_dir / 'ts_diagram.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(output_path)
    
    def _plot_vertical_sections(self, data: Dict[str, np.ndarray], output_dir: Path) -> str:
        """Genera sección vertical de temperatura"""
        try:
            # Crear figura
            plt.figure(figsize=(12, 8))
            
            # Calcular distancia entre estaciones (en km)
            lat = data['latitude']
            lon = data['longitude']
            R = 6371  # Radio de la Tierra en km
            distances = []
            for i in range(len(lat)):
                if i == 0:
                    distances.append(0)
                else:
                    dlat = np.radians(lat[i] - lat[i-1])
                    dlon = np.radians(lon[i] - lon[i-1])
                    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat[i-1])) * np.cos(np.radians(lat[i])) * np.sin(dlon/2)**2
                    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
                    distances.append(distances[-1] + R * c)
            
            # Crear grids para interpolación
            dist_grid = np.linspace(min(distances), max(distances), 100)
            depth_grid = np.linspace(min(data['depth']), max(data['depth']), 100)
            DIST, DEPTH = np.meshgrid(dist_grid, depth_grid)
            
            # Interpolar temperatura en el grid
            points = np.array([(d, z) for d, z in zip(distances, data['depth'])])
            temp_grid = griddata(points, data['temperature'], (DIST, DEPTH), method='cubic')
            
            # Crear el contour plot
            plt.contourf(DIST, DEPTH, temp_grid, levels=20, cmap='RdYlBu_r')
            plt.colorbar(label='Temperatura (°C)')
            
            # Configurar ejes
            plt.gca().invert_yaxis()
            plt.xlabel('Distancia (km)')
            plt.ylabel('Profundidad (m)')
            
            # Agregar grid
            plt.grid(True, linestyle=':', alpha=0.3, color='white')
            
            # Guardar figura
            output_path = output_dir / 'vertical_sections.png'
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error generando sección vertical: {str(e)}")
            raise
    
    def _plot_spatial_distribution(self, data: Dict[str, np.ndarray], output_dir: Path) -> str:
        """Genera mapa de distribución espacial de los datos"""
        try:
            # Crear figura
            plt.figure(figsize=(10, 8))
            
            # Crear mapa base
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.coastlines()
            ax.gridlines(draw_labels=True)
            
            # Agregar datos
            scatter = plt.scatter(data['longitude'], data['latitude'], 
                                c=data['temperature'], cmap='RdYlBu_r',
                                transform=ccrs.PlateCarree(),
                                s=100, alpha=0.7)
            
            # Ajustar límites del mapa
            margin = 2  # grados
            ax.set_extent([
                min(data['longitude']) - margin,
                max(data['longitude']) + margin,
                min(data['latitude']) - margin,
                max(data['latitude']) + margin
            ])
            
            # Agregar colorbar
            plt.colorbar(scatter, label='Temperatura (°C)')
            
            # Agregar título y etiquetas
            plt.title('Distribución Espacial de Estaciones')
            
            # Guardar figura
            output_path = output_dir / 'spatial_distribution.png'
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error generando mapa de distribución: {str(e)}")
            raise
    
    def _calculate_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula estadísticas básicas"""
        stats = {}
        for var in ['temperature', 'salinity', 'depth']:
            if var in data:
                stats[var] = {
                    'mean': float(np.mean(data[var])),
                    'std': float(np.std(data[var])),
                    'min': float(np.min(data[var])),
                    'max': float(np.max(data[var])),
                    'n_samples': len(data[var])
                }
        return stats
    
    def _calculate_mean_profiles(self, temp: np.ndarray, sal: np.ndarray,
                               depth: np.ndarray) -> Dict[str, Any]:
        """Calcula perfiles promedio"""
        # Definir bins de profundidad
        depth_bins = np.array(self.config['depth_bins'])
        
        # Inicializar arrays para promedios
        temp_mean = np.zeros_like(depth_bins)
        sal_mean = np.zeros_like(depth_bins)
        
        # Calcular promedios por bin
        for i, d in enumerate(depth_bins):
            if i == 0:
                mask = depth <= d
            else:
                mask = (depth > depth_bins[i-1]) & (depth <= d)
            
            if np.any(mask):
                temp_mean[i] = np.mean(temp[mask])
                sal_mean[i] = np.mean(sal[mask])
        
        return {
            'depth_bins': depth_bins.tolist(),
            'temperature': temp_mean.tolist(),
            'salinity': sal_mean.tolist()
        }