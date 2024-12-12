import numpy as np
from typing import Dict, Any, List, Optional
import logging
from scipy import stats

class QAAgent:
    """Agente para control de calidad de datos oceanográficos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {
            'min_samples': 5,  # Reducido de 10 a 5
            'min_values': {
                'temperature': -2,  # °C
                'salinity': 0,      # PSU
                'depth': -11000     # m (negativo porque profundidad es negativa)
            },
            'max_values': {
                'temperature': 35,  # °C
                'salinity': 40,     # PSU
                'depth': 0          # m
            },
            'outlier_threshold': 3,  # Desviaciones estándar
            'max_gap': 100,         # m
            'min_density': 1020,    # kg/m³
            'max_density': 1040     # kg/m³
        }
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configura el agente con parámetros específicos
        
        Args:
            config: Diccionario con configuración
        """
        self.config.update(config)
    
    async def check_quality(self, data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Realiza control de calidad de los datos
        
        Args:
            data: Diccionario con datos oceanográficos
            
        Returns:
            Dict con resultados del QA y datos limpios
        """
        try:
            # Extraer variables principales
            temp = data['temperature']
            sal = data['salinity']
            depth = data['depth']
            lat = data['latitude']
            lon = data['longitude']
            
            # Verificar NaN
            valid_idx = ~(np.isnan(temp) | np.isnan(sal) | np.isnan(depth))
            
            # Verificar límites físicos
            valid_idx &= (temp >= self.config['min_values']['temperature']) & (temp <= self.config['max_values']['temperature'])
            valid_idx &= (sal >= self.config['min_values']['salinity']) & (sal <= self.config['max_values']['salinity'])
            valid_idx &= (depth >= self.config['min_values']['depth'])
            
            # Verificar outliers
            z_temp = np.abs(stats.zscore(temp))
            z_sal = np.abs(stats.zscore(sal))
            valid_idx &= (z_temp < self.config['outlier_threshold']) & (z_sal < self.config['outlier_threshold'])
            
            # Filtrar datos
            clean_data = {
                'temperature': temp[valid_idx],
                'salinity': sal[valid_idx],
                'depth': depth[valid_idx],
                'latitude': lat[valid_idx],
                'longitude': lon[valid_idx]
            }
            
            # Calcular estadísticas
            stats_data = {
                'n_total': len(temp),
                'n_valid': np.sum(valid_idx),
                'temp_range': [float(np.min(clean_data['temperature'])), float(np.max(clean_data['temperature']))],
                'sal_range': [float(np.min(clean_data['salinity'])), float(np.max(clean_data['salinity']))],
                'depth_range': [float(np.min(clean_data['depth'])), float(np.max(clean_data['depth']))]
            }
            
            return {
                'clean_data': clean_data,
                'stats': stats_data,
                'flags': {
                    'nan': np.isnan(temp) | np.isnan(sal) | np.isnan(depth),
                    'range': ~((temp >= self.config['min_values']['temperature']) & 
                              (temp <= self.config['max_values']['temperature']) &
                              (sal >= self.config['min_values']['salinity']) & 
                              (sal <= self.config['max_values']['salinity']) &
                              (depth >= self.config['min_values']['depth'])),
                    'outlier': (z_temp >= self.config['outlier_threshold']) | 
                              (z_sal >= self.config['outlier_threshold'])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error en control de calidad: {str(e)}")
            raise
    
    def _check_density_consistency(self, temp: np.ndarray, sal: np.ndarray) -> bool:
        """
        Verifica consistencia de la densidad calculada
        
        Args:
            temp: Array de temperatura
            sal: Array de salinidad
            
        Returns:
            bool: True si la densidad está en rangos esperados
        """
        # Aproximación simple de densidad
        density = 1000 + 0.8 * sal - 0.2 * temp
        
        return np.all(
            (density >= self.config['min_density']) & 
            (density <= self.config['max_density'])
        )
