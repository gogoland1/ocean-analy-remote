import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Generator
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class ParserAgent:
    """Agente para parsear y validar datos oceanográficos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {
            'variables': ['temperature', 'salinity', 'pressure', 'latitude', 'longitude'],
            'units': {
                'temperature': '°C',
                'salinity': 'PSU',
                'pressure': 'dbar',
                'latitude': '°N',
                'longitude': '°E'
            },
            'encoding': 'utf-8',
            'delimiter': ',',
            'decimal': '.',
            'na_values': ['NA', 'NaN', '', ' '],
            'batch_size': 1000,  # Tamaño predeterminado del lote
            'max_workers': 4     # Número máximo de workers para procesamiento paralelo
        }
        self.data_path = None
        
    def process_in_batches(self, file_list: List[Path], batch_size: Optional[int] = None) -> Generator[Dict[str, Any], None, None]:
        """
        Procesa una lista de archivos en lotes
        
        Args:
            file_list: Lista de rutas a los archivos CTD
            batch_size: Tamaño opcional del lote (usa el valor de config si no se especifica)
            
        Yields:
            Diccionario con datos procesados para cada lote
        """
        batch_size = batch_size or self.config['batch_size']
        total_files = len(file_list)
        
        self.logger.info(f"Iniciando procesamiento por lotes de {total_files} archivos")
        self.logger.info(f"Tamaño de lote: {batch_size}")
        
        # Crear barra de progreso
        with tqdm(total=total_files, desc="Procesando archivos") as pbar:
            for i in range(0, total_files, batch_size):
                batch = file_list[i:i + batch_size]
                try:
                    # Procesar lote actual
                    batch_results = self._process_batch(batch)
                    
                    # Actualizar progreso
                    pbar.update(len(batch))
                    
                    yield batch_results
                    
                except Exception as e:
                    self.logger.error(f"Error procesando lote {i//batch_size}: {str(e)}")
                    continue
    
    def _process_batch(self, batch: List[Path]) -> Dict[str, Any]:
        """
        Procesa un lote de archivos en paralelo
        
        Args:
            batch: Lista de archivos a procesar
            
        Returns:
            Diccionario con datos combinados del lote
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            # Crear futures para cada archivo
            future_to_file = {
                executor.submit(self._process_single_file, file): file 
                for file in batch
            }
            
            # Recolectar resultados a medida que se completan
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    data = future.result()
                    results.append(data)
                except Exception as e:
                    self.logger.error(f"Error procesando archivo {file}: {str(e)}")
                    continue
        
        # Combinar resultados del lote
        return self._combine_batch_results(results)
    
    def _process_single_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Procesa un único archivo CTD
        
        Args:
            file_path: Ruta al archivo CTD
            
        Returns:
            Diccionario con datos procesados
        """
        try:
            # Leer y procesar archivo
            df = pd.read_csv(
                file_path,
                encoding=self.config['encoding'],
                delimiter=self.config['delimiter'],
                decimal=self.config['decimal'],
                na_values=self.config['na_values']
            )
            
            # Extraer variables
            data = {}
            for var in self.config['variables']:
                if var in df.columns:
                    data[var] = df[var].values
                else:
                    self.logger.warning(f"Variable {var} no encontrada en {file_path}")
                    data[var] = np.array([])
            
            # Convertir presión a profundidad
            if 'pressure' in data:
                data['depth'] = -1 * data['pressure']
            
            # Agregar metadata
            data['metadata'] = {
                'source_file': str(file_path),
                'n_samples': len(df),
                'timestamp': time.time()
            }
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error procesando archivo {file_path}: {str(e)}")
            raise
    
    def _combine_batch_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combina los resultados de múltiples archivos en un único conjunto de datos
        
        Args:
            results: Lista de diccionarios con datos procesados
            
        Returns:
            Diccionario con datos combinados
        """
        if not results:
            return {}
        
        combined = {
            'metadata': {
                'n_files': len(results),
                'total_samples': sum(r['metadata']['n_samples'] for r in results),
                'timestamp': time.time()
            }
        }
        
        # Combinar variables
        for var in self.config['variables']:
            combined[var] = np.concatenate([r[var] for r in results if var in r])
        
        # Combinar profundidad si existe
        if 'depth' in results[0]:
            combined['depth'] = np.concatenate([r['depth'] for r in results if 'depth' in r])
        
        return combined