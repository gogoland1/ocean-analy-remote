from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import matplotlib.gridspec as gridspec

class PosterAgent:
    """Agente para generación de posters científicos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {
            'title': 'Análisis Oceanográfico',
            'authors': ['Equipo de Investigación'],
            'institution': 'Instituto Oceanográfico',
            'size': (16, 20),
            'dpi': 300,
            'style': 'default',
            'columns': 2,
            'font_family': 'sans-serif',
            'title_size': 24,
            'heading_size': 18,
            'text_size': 12,
            'caption_size': 10,
            'margins': {
                'top': 0.95,     # Margen superior para títulos
                'text_bottom': 0.35,  # Límite inferior para texto
                'figure_top': 0.30,   # Límite superior para figuras
                'side': 0.1,     # Márgenes laterales
                'spacing': 0.05   # Espacio entre elementos
            }
        }
        self.output_dir = None
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configura el agente con parámetros específicos
        
        Args:
            config: Diccionario con configuración
        """
        self.config.update(config)
    
    def set_output_dir(self, path: Path) -> None:
        """
        Establece el directorio de salida para posters
        
        Args:
            path: Ruta al directorio de salida
        """
        self.output_dir = path
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_poster(self, results: Dict[str, Any], output_dir: Path,
                            title: str = None, authors: List[str] = None) -> Path:
        """
        Genera un poster científico
        
        Args:
            results: Resultados del análisis
            output_dir: Directorio de salida
            title: Título del poster
            authors: Lista de autores
        """
        try:
            self.logger.info("Iniciando generación de poster")
            
            # Verificar que tenemos las visualizaciones necesarias
            if 'visualizations' not in results or 'figures' not in results['visualizations']:
                raise ValueError("No se encontraron visualizaciones en los resultados")
            
            # Configuración temporal del poster
            temp_config = {
                'title': title or "Análisis Oceanográfico",
                'authors': authors or ["Equipo de Investigación"],
                'institution': "Instituto Oceanográfico",
                'title_size': 24,
                'author_size': 16,
                'heading_size': 18,
                'text_size': 12,
                'caption_size': 10,
                'dpi': 300,
                'format': 'png',
                'margins': {
                    'side': 0.05,
                    'top': 0.95,
                    'text_bottom': 0.1
                },
                'columns': 2
            }
            
            # Crear figura principal
            fig = plt.figure(figsize=(20, 28))  # Tamaño A1 aproximado
            
            # Definir grid para el layout
            gs = gridspec.GridSpec(4, 2, height_ratios=[1, 0.1, 1, 2])
            gs.update(wspace=0.3, hspace=0.4)
            
            # Título y autores (ocupando toda la parte superior)
            title_ax = fig.add_subplot(gs[0, :])
            self._add_header_section(title_ax, temp_config['title'], temp_config['authors'], temp_config)
            title_ax.axis('off')
            
            # Sección de Introducción
            intro_ax = fig.add_subplot(gs[2, 0])
            self._add_introduction_section(intro_ax, temp_config)
            intro_ax.axis('off')
            
            # Sección de Metodología
            method_ax = fig.add_subplot(gs[2, 1])
            self._add_methods_section(method_ax, temp_config)
            method_ax.axis('off')
            
            # Sección de Resultados (ocupando todo el ancho, más abajo)
            results_ax = fig.add_subplot(gs[3, :])
            self._add_results_section(results_ax, results, temp_config)
            results_ax.axis('off')
            
            # Guardar poster
            output_path = output_dir / f"poster_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(output_path, dpi=temp_config['dpi'], bbox_inches='tight', 
                       facecolor='white', format=temp_config['format'])
            plt.close()
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generando poster: {str(e)}")
            raise
    
    def _add_header_section(self, ax: plt.Axes, title: str, authors: List[str], config: Dict[str, Any]) -> None:
        """Agrega sección de encabezado con título y autores"""
        margins = config['margins']
        
        # Título principal
        ax.text(0.5, 0.95, title,
                ha='center', va='top',
                fontsize=config['title_size'],
                fontweight='bold')
        
        # Autores y afiliación
        ax.text(0.5, 0.90, '\n'.join(authors),
                ha='center', va='top',
                fontsize=config['author_size'])
        ax.text(0.5, 0.87, "Instituto Oceanográfico",
                ha='center', va='top',
                fontsize=config['author_size'])
                
        # Rectángulos negros para las secciones
        rect_height = 0.03
        rect_y = 0.82  # Posición Y de los rectángulos
        
        # Rectángulo izquierdo
        rect_left = plt.Rectangle((margins['side'], rect_y), 0.4, rect_height, 
                                facecolor='black', alpha=1.0)
        ax.add_patch(rect_left)
        
        # Rect��ngulo derecho
        rect_right = plt.Rectangle((0.5 + margins['side'], rect_y), 0.4, rect_height, 
                                 facecolor='black', alpha=1.0)
        ax.add_patch(rect_right)
    
    def _add_introduction_section(self, ax: plt.Axes, config: Dict[str, Any]) -> None:
        """Agrega sección de introducción"""
        margins = config['margins']
        
        # Título de sección con fondo azul claro
        patch = plt.Rectangle((margins['side'], 0.82), 0.4, 0.03, 
                            transform=ax.transAxes, facecolor='#ADD8E6')
        ax.add_patch(patch)
        
        # Título sobre el rectángulo negro
        ax.text(margins['side'] + 0.2, 0.835, "Introducción",
                ha='center', va='center',
                fontsize=config['heading_size'],
                fontweight='bold',
                color='white')
        
        # Contenido
        content = [
            "• Análisis de datos oceanográficos para comprender patrones",
            "• Procesamiento de perfiles CTD",
            "• Identificación de masas de agua"
        ]
        
        y_pos = 0.78
        for line in content:
            ax.text(margins['side'], y_pos, line,
                   ha='left', va='top',
                   fontsize=config['text_size'])
            y_pos -= 0.03
            
    def _add_methods_section(self, ax: plt.Axes, config: Dict[str, Any]) -> None:
        """Agrega sección de materiales y métodos"""
        margins = config['margins']
        
        # Título de sección con fondo azul claro
        patch = plt.Rectangle((0.5 + margins['side'], 0.82), 0.4, 0.03,
                            transform=ax.transAxes, facecolor='#ADD8E6')
        ax.add_patch(patch)
        
        # Título sobre el rectángulo negro
        ax.text(0.5 + margins['side'] + 0.2, 0.835, "Materiales y Métodos",
                ha='center', va='center',
                fontsize=config['heading_size'],
                fontweight='bold',
                color='white')
        
        # Contenido
        content = [
            "• Análisis de datos CTD",
            "• Control de calidad automático",
            "• Análisis estadístico multivariado"
        ]
        
        y_pos = 0.78
        for line in content:
            ax.text(0.5 + margins['side'], y_pos, line,
                   ha='left', va='top',
                   fontsize=config['text_size'])
            y_pos -= 0.03
    
    def _add_results_section(self, ax: plt.Axes, results: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Agrega sección de resultados con visualizaciones"""
        margins = config['margins']
        
        # Título de sección con fondo azul oscuro
        patch = plt.Rectangle((0, margins['top']), 1, 0.05, transform=ax.transAxes, 
                            facecolor='#1f77b4', alpha=0.2)
        ax.add_patch(patch)
        
        # Título más arriba para dar espacio
        ax.text(0.5, margins['top'] + 0.03, "Resultados y Discusión",
                ha='center', va='top',
                fontsize=config['heading_size'],
                fontweight='bold')
        
        # Texto de resultados principales en la parte superior
        results_text = ax.text(margins['side'], margins['top'] - 0.1,
            "Resultados Principales:\n" +
            "• Control de Calidad: 10 muestras válidas\n" +
            "• Correlación profundidad-temperatura: -0.99\n" +
            "• Gradiente termohalino: 0.05\n" +
            "• Identificación de masas de agua: 3 clusters",
            ha='left', va='top',
            fontsize=config['text_size'],
            transform=ax.transAxes)
        
        # Obtener el bbox del texto para saber dónde termina
        bbox = results_text.get_window_extent(renderer=plt.gcf().canvas.get_renderer())
        bbox_trans = bbox.transformed(ax.transAxes.inverted())
        text_bottom = bbox_trans.y0  # Posición Y donde termina el texto
        
        # Visualizaciones
        if 'visualizations' in results and 'figures' in results['visualizations']:
            figures = results['visualizations']['figures']
            fig = plt.gcf()
            
            # Calcular espacios disponibles
            text_margin = 0.05  # Margen de seguridad después del texto
            figure_spacing = 0.05  # Espacio entre figuras
            
            # Definir posiciones y tamaños específicos para cada figura
            figure_layout = {
                'ctd_profiles': {
                    'x': 0.08,  # Más margen izquierdo
                    'y': text_bottom - text_margin - 0.2,  # Reducido el espacio vertical
                    'width': 0.35,  # Reducido el ancho
                    'height': 0.2   # Reducida la altura
                },
                'ts_diagram': {
                    'x': 0.52,  # Separado del CTD profile
                    'y': text_bottom - text_margin - 0.25,  # Alineado con CTD profile
                    'width': 0.4,
                    'height': 0.25
                },
                'vertical_sections': {
                    'x': 0.08,  # Alineado con CTD profile
                    'y': text_bottom - text_margin - 0.55,  # Debajo de las figuras superiores
                    'width': 0.4,
                    'height': 0.25
                },
                'distributions': {
                    'x': 0.52,  # Alineado con TS diagram
                    'y': text_bottom - text_margin - 0.55,  # Alineado con vertical sections
                    'width': 0.4,
                    'height': 0.25
                }
            }
            
            # Colocar cada figura en su posición específica
            for name, path in figures.items():
                if name in figure_layout:
                    layout = figure_layout[name]
                    self.logger.info(f"Agregando figura {name} desde {path}")
                    
                    try:
                        # Verificar que el archivo existe
                        if not Path(path).exists():
                            self.logger.error(f"No se encuentra el archivo {path}")
                            continue
                            
                        ax_sub = fig.add_axes([
                            layout['x'],
                            layout['y'],
                            layout['width'],
                            layout['height']
                        ])
                        
                        img = plt.imread(path)
                        ax_sub.imshow(img)
                        
                        # Solo agregar título si no es ctd_profiles
                        if name != 'ctd_profiles':
                            ax_sub.set_title(name.replace('_', ' ').title(),
                                           fontsize=config['caption_size'],
                                           pad=10)
                        ax_sub.axis('off')
                        
                    except Exception as e:
                        self.logger.error(f"Error agregando figura {name}: {str(e)}")
                        continue
        
        ax.axis('off')