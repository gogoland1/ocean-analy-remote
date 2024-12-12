import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, List
import logging

class StatsAgent:
    """Agente para análisis estadístico de datos oceanográficos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {
            'scaling': 'standard',
            'min_samples': 10,
            'significance_level': 0.05
        }
        self.scaler = StandardScaler()
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configura el agente con parámetros específicos
        
        Args:
            config: Diccionario con configuración
        """
        self.config.update(config)
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza análisis estadístico de los datos
        
        Args:
            data: Diccionario con datos oceanográficos
        """
        try:
            # Preparar datos
            temp = data['temperature']
            sal = data['salinity']
            depth = data['depth']
            
            # Análisis básico
            basic_stats = self._calculate_basic_stats({
                'temperature': temp,
                'salinity': sal,
                'depth': depth
            })
            
            # Análisis de correlación
            correlation = self._analyze_correlation(temp, sal)
            
            # Análisis de estratificación
            stratification = self._analyze_stratification(temp, sal, depth)
            
            # Compilar resultados
            results = {
                'basic_stats': basic_stats,
                'correlation': correlation,
                'stratification': stratification,
                'summary': self._generate_summary(basic_stats, correlation, stratification)
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error en análisis estadístico: {str(e)}")
            raise
    
    def _calculate_basic_stats(self, variables: Dict[str, np.ndarray]) -> Dict[str, Dict]:
        """Calcula estadísticas básicas para cada variable"""
        stats_dict = {}
        
        for var_name, values in variables.items():
            stats_dict[var_name] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'median': float(np.median(values)),
                'q25': float(np.percentile(values, 25)),
                'q75': float(np.percentile(values, 75))
            }
            
        return stats_dict
    
    def _analyze_correlation(self, temp: np.ndarray, sal: np.ndarray) -> Dict[str, float]:
        """Analiza la correlación entre temperatura y salinidad"""
        # Eliminar NaN si existen
        mask = ~(np.isnan(temp) | np.isnan(sal))
        temp_clean = temp[mask]
        sal_clean = sal[mask]
        
        # Calcular correlación
        corr_coef, p_value = stats.pearsonr(temp_clean, sal_clean)
        
        return {
            'correlation_coefficient': float(corr_coef),
            'p_value': float(p_value)
        }
    
    def _analyze_stratification(self, temp: np.ndarray, sal: np.ndarray, depth: np.ndarray) -> Dict[str, float]:
        """Analiza la estratificación de la columna de agua"""
        # Calcular gradientes
        temp_gradient = np.gradient(temp, depth)
        sal_gradient = np.gradient(sal, depth)
        
        # Identificar termoclina y haloclina
        thermocline_idx = np.argmax(np.abs(temp_gradient))
        halocline_idx = np.argmax(np.abs(sal_gradient))
        
        return {
            'thermocline_depth': float(depth[thermocline_idx]),
            'thermocline_gradient': float(temp_gradient[thermocline_idx]),
            'halocline_depth': float(depth[halocline_idx]),
            'halocline_gradient': float(sal_gradient[halocline_idx]),
            'mean_temp_gradient': float(np.mean(np.abs(temp_gradient))),
            'mean_sal_gradient': float(np.mean(np.abs(sal_gradient)))
        }
    
    def _generate_summary(self, basic_stats: Dict, correlation: Dict, stratification: Dict) -> str:
        """Genera un resumen de los resultados estadísticos"""
        summary = []
        
        # Resumen de rangos
        temp_stats = basic_stats['temperature']
        sal_stats = basic_stats['salinity']
        summary.append(f"Rango de temperatura: {temp_stats['min']:.1f}°C - {temp_stats['max']:.1f}°C")
        summary.append(f"Rango de salinidad: {sal_stats['min']:.1f} - {sal_stats['max']:.1f}")
        
        # Correlación T-S
        corr = correlation['correlation_coefficient']
        summary.append(f"Correlación T-S: {corr:.2f}")
        
        # Estratificación
        summary.append(f"Termoclina principal a {stratification['thermocline_depth']:.1f}m")
        summary.append(f"Haloclina principal a {stratification['halocline_depth']:.1f}m")
        
        return "\n".join(summary)