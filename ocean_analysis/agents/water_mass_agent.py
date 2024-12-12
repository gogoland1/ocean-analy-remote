from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
import pandas as pd
import xarray as xr
import gsw
import matplotlib.pyplot as plt
import cmocean
from scipy.optimize import nnls
from dataclasses import dataclass
from pathlib import Path
import logging

@dataclass
class WaterMassDefinition:
    """Definición de una masa de agua"""
    name: str
    temperature: float
    salinity: float
    oxygen: Optional[float] = None
    depth_range: Tuple[float, float] = None
    sigma_t: Optional[float] = None
    region: Optional[str] = None
    description: str = ""

class WaterMassAgent:
    """Agente para identificación y análisis de masas de agua"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {
            'min_points': 10,
            'min_fraction': 0.05,
            'max_distance': 0.5,
            'reference_masses': [
                WaterMassDefinition(
                    name="AAIW",
                    temperature=2.2,
                    salinity=33.8,
                    depth_range=(-500, -1000),
                    description="Agua Intermedia Antártica"
                ),
                WaterMassDefinition(
                    name="SACW",
                    temperature=15.0,
                    salinity=35.5,
                    depth_range=(-100, -500),
                    description="Agua Central del Atlántico Sur"
                ),
                WaterMassDefinition(
                    name="TW",
                    temperature=20.0,
                    salinity=36.0,
                    depth_range=(0, -100),
                    description="Agua Tropical"
                )
            ]
        }
        self.output_dir = None
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configura el agente con parámetros específicos
        
        Args:
            config: Diccionario con configuración
        """
        if 'reference_masses' in config:
            self.config['reference_masses'] = [
                WaterMassDefinition(**mass) if isinstance(mass, dict) else mass
                for mass in config['reference_masses']
            ]
        
        # Actualizar otros parámetros
        for key in ['min_points', 'min_fraction', 'max_distance']:
            if key in config:
                self.config[key] = config[key]
    
    def set_output_dir(self, path: Path) -> None:
        """
        Establece el directorio de salida para visualizaciones
        
        Args:
            path: Ruta al directorio de salida
        """
        self.output_dir = path
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identifica y analiza masas de agua
        
        Args:
            data: Diccionario con datos oceanográficos
        """
        try:
            self.logger.info("Iniciando análisis de masas de agua")
            
            if self.output_dir is None:
                self.output_dir = Path("water_masses")
                self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Extraer variables
            temp = data['temperature']
            sal = data['salinity']
            depth = data['depth']
            
            # Calcular densidad potencial
            pressure = gsw.p_from_z(-depth, -34.5)  # Latitud aproximada
            sa = gsw.SA_from_SP(sal, pressure, -50, -34.5)  # Longitud y latitud aproximadas
            ct = gsw.CT_from_t(sa, temp, pressure)
            sigma0 = gsw.sigma0(sa, ct)
            
            # Identificar masas de agua
            water_masses = self._identify_water_masses(temp, sal, depth, sigma0)
            
            # Generar visualizaciones
            figures = self._generate_visualizations(temp, sal, sigma0, water_masses)
            
            # Compilar resultados
            results = {
                'water_masses': water_masses,
                'figures': figures,
                'density': {
                    'sigma0': sigma0.tolist(),
                    'pressure': pressure.tolist(),
                    'absolute_salinity': sa.tolist(),
                    'conservative_temperature': ct.tolist()
                }
            }
            
            self.logger.info("Análisis de masas de agua completado exitosamente")
            return results
            
        except Exception as e:
            self.logger.error(f"Error en análisis de masas de agua: {str(e)}")
            raise
    
    def _identify_water_masses(self, temp: np.ndarray, sal: np.ndarray,
                             depth: np.ndarray, sigma0: np.ndarray) -> Dict[str, Any]:
        """Identifica masas de agua usando análisis OMP"""
        # Preparar matriz de propiedades de referencia
        n_masses = len(self.config['reference_masses'])
        G = np.zeros((3, n_masses))  # Temperatura, salinidad, masa
        for i, mass in enumerate(self.config['reference_masses']):
            G[0, i] = mass.temperature
            G[1, i] = mass.salinity
            G[2, i] = 1  # Conservación de masa
        
        # Preparar datos observados
        n_points = len(temp)
        d = np.zeros((3, n_points))
        d[0, :] = temp
        d[1, :] = sal
        d[2, :] = 1
        
        # Resolver sistema para cada punto
        fractions = np.zeros((n_points, n_masses))
        residuals = np.zeros(n_points)
        
        for i in range(n_points):
            # Resolver sistema usando NNLS (Non-Negative Least Squares)
            x, rnorm = nnls(G, d[:, i])
            fractions[i, :] = x
            residuals[i] = rnorm
        
        # Identificar masa de agua dominante
        dominant_mass = np.argmax(fractions, axis=1)
        
        # Calcular estadísticas
        mass_stats = {}
        for i, mass in enumerate(self.config['reference_masses']):
            mask = dominant_mass == i
            if np.sum(mask) >= self.config['min_points']:
                mass_stats[mass.name] = {
                    'temperature': float(np.mean(temp[mask])),
                    'salinity': float(np.mean(sal[mask])),
                    'sigma0': float(np.mean(sigma0[mask])),
                    'depth_range': [float(np.min(depth[mask])), float(np.max(depth[mask]))],
                    'fraction': float(np.mean(fractions[:, i])),
                    'n_points': int(np.sum(mask))
                }
        
        return {
            'fractions': fractions.tolist(),
            'residuals': residuals.tolist(),
            'dominant_mass': dominant_mass.tolist(),
            'statistics': mass_stats
        }
    
    def _generate_visualizations(self, temp: np.ndarray, sal: np.ndarray,
                               sigma0: np.ndarray, water_masses: Dict[str, Any]) -> Dict[str, str]:
        """Genera visualizaciones de masas de agua"""
        figures = {}
        
        # 1. Diagrama T-S con masas de agua
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plotear datos
        scatter = ax.scatter(sal, temp, c=water_masses['dominant_mass'],
                           cmap='Set3', alpha=0.6)
        
        # Plotear masas de agua de referencia
        for mass in self.config['reference_masses']:
            ax.plot(mass.salinity, mass.temperature, 'r*', 
                   markersize=15, label=mass.name)
        
        # Configurar gráfico
        ax.set_xlabel('Salinidad')
        ax.set_ylabel('Temperatura (°C)')
        ax.grid(True)
        ax.legend()
        
        # Guardar figura
        ts_path = self.output_dir / "ts_diagram_masses.png"
        fig.savefig(ts_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        figures['ts_diagram'] = str(ts_path)
        
        # 2. Distribución vertical de masas de agua
        if 'depth' in water_masses:
            fig, ax = plt.subplots(figsize=(8, 10))
            
            depth = np.array(water_masses['depth'])
            dominant_mass = np.array(water_masses['dominant_mass'])
            
            for i, mass in enumerate(self.config['reference_masses']):
                mask = dominant_mass == i
                if np.any(mask):
                    ax.scatter(np.full_like(depth[mask], i), -depth[mask],
                             alpha=0.6, label=mass.name)
            
            ax.set_ylabel('Profundidad (m)')
            ax.set_xlabel('Masa de Agua')
            ax.grid(True)
            ax.legend()
            
            # Guardar figura
            dist_path = self.output_dir / "vertical_distribution.png"
            fig.savefig(dist_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            figures['vertical_distribution'] = str(dist_path)
        
        return figures