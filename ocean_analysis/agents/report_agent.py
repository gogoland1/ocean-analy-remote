import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import markdown
import json
from datetime import datetime

class ReportAgent:
    """Agente para generación de reportes en markdown"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {
            'title': 'Reporte de Análisis Oceanográfico',
            'output_format': 'md',
            'include_plots': True,
            'include_stats': True,
            'include_metadata': True,
            'template': 'default'
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
        Establece el directorio de salida para reportes
        
        Args:
            path: Ruta al directorio de salida
        """
        self.output_dir = path
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_report(self, results: Dict[str, Any], output_dir: Path,
                             title: str = None, authors: List[str] = None) -> Path:
        """
        Genera un reporte en markdown
        
        Args:
            results: Resultados del análisis
            output_dir: Directorio de salida
            title: Título del reporte (opcional)
            authors: Lista de autores (opcional)
        """
        try:
            self.logger.info("Iniciando generación de reporte")
            
            # Actualizar configuración temporal
            temp_config = self.config.copy()
            if title:
                temp_config['title'] = title
            if authors:
                temp_config['authors'] = authors
            
            # Establecer directorio de salida
            self.set_output_dir(output_dir)
            
            # Generar contenido del reporte
            content = self._generate_markdown_content(results, temp_config)
            
            # Guardar reporte
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = self.output_dir / f"report_{timestamp}.md"
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Generar HTML si se requiere
            if temp_config['output_format'] == 'html':
                html_content = markdown.markdown(content)
                html_path = self.output_dir / f"report_{timestamp}.html"
                
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
            
            self.logger.info("Reporte generado exitosamente")
            return report_path
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {str(e)}")
            raise
    
    def _format_value(self, value: Any) -> str:
        """Formatea un valor para su presentación en markdown"""
        if isinstance(value, (int, bool)):
            return str(value)
        elif isinstance(value, float):
            return f"{value:.2f}"
        elif isinstance(value, (list, tuple)):
            return ", ".join(str(x) for x in value)
        elif isinstance(value, dict):
            return "; ".join(f"{k}: {v}" for k, v in value.items())
        else:
            return str(value)
    
    def _generate_markdown_content(self, results: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Genera el contenido del reporte en markdown"""
        sections = []
        
        # Título y encabezado
        sections.append(f"# {config['title']}\n")
        sections.append(f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        if config['authors']:
            sections.append(f"**Autores:** {', '.join(config['authors'])}*\n")
        
        # Metadata
        if config['include_metadata'] and 'metadata' in results:
            sections.append("\n## Metadata\n")
            sections.append("| Campo | Valor |")
            sections.append("|-------|-------|")
            for key, value in results['metadata'].items():
                sections.append(f"| {key} | {self._format_value(value)} |")
        
        # Control de Calidad
        if 'qa' in results and 'statistics' in results['qa']:
            sections.append("\n## Control de Calidad\n")
            for var, stats in results['qa']['statistics'].items():
                if isinstance(stats, dict):
                    sections.append(f"\n### {var.title()}\n")
                    sections.append("| Métrica | Valor |")
                    sections.append("|---------|-------|")
                    for metric, value in stats.items():
                        sections.append(f"| {metric} | {self._format_value(value)} |")
        
        # Estadísticas
        if config['include_stats'] and 'statistics' in results:
            sections.append("\n## Estadísticas\n")
            stats = results['statistics']
            if isinstance(stats, dict):
                for var, var_stats in stats.items():
                    if isinstance(var_stats, dict):
                        sections.append(f"\n### {var.title()}\n")
                        sections.append("| Métrica | Valor |")
                        sections.append("|---------|-------|")
                        for metric, value in var_stats.items():
                            sections.append(f"| {metric} | {self._format_value(value)} |")
        
        # Masas de Agua
        if 'water_masses' in results:
            sections.append("\n## Masas de Agua\n")
            wm_results = results['water_masses']
            if isinstance(wm_results, dict):
                if 'statistics' in wm_results:
                    sections.append("\n### Estadísticas por Masa de Agua\n")
                    for mass, stats in wm_results['statistics'].items():
                        if isinstance(stats, dict):
                            sections.append(f"\n#### {mass}\n")
                            sections.append("| Métrica | Valor |")
                            sections.append("|---------|-------|")
                            for metric, value in stats.items():
                                sections.append(f"| {metric} | {self._format_value(value)} |")
        
        # Visualizaciones
        if config['include_plots'] and 'visualizations' in results:
            sections.append("\n## Visualizaciones\n")
            viz_results = results['visualizations']
            if isinstance(viz_results, dict) and 'figures' in viz_results:
                for name, path in viz_results['figures'].items():
                    sections.append(f"\n### {name.replace('_', ' ').title()}\n")
                    sections.append(f"![{name}]({path})\n")
        
        # Referencias
        if 'research' in results:
            sections.append("\n## Referencias\n")
            research = results['research']
            if isinstance(research, dict):
                if 'papers' in research:
                    for paper in research['papers']:
                        if isinstance(paper, dict):
                            sections.append(f"\n### {paper.get('title', 'Sin título')}\n")
                            sections.append(f"**Autores:** {', '.join(paper.get('authors', []))}\n")
                            sections.append(f"**Año:** {paper.get('year', 'N/A')}\n")
                            sections.append(f"**Revista:** {paper.get('journal', 'N/A')}\n")
                            sections.append(f"**DOI:** {paper.get('doi', 'N/A')}\n")
                            if 'abstract' in paper:
                                sections.append(f"\n{paper['abstract']}\n")
                
                if 'summary' in research:
                    sections.append("\n### Resumen de la Literatura\n")
                    sections.append(research['summary'])
        
        return "\n".join(sections)