import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
from tqdm import tqdm
from tavily import TavilyClient
import asyncio
from dotenv import load_dotenv
import logging

class ResearcherAgent:
    """Agente investigador para búsqueda de literatura científica oceanográfica"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("No se encontró TAVILY_API_KEY en las variables de entorno")
        self.client = TavilyClient(api_key=self.api_key)
        self.cache_dir = Path("cache/research")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.config = {
            'max_results': 10,
            'min_year': 2010,
            'sort_by': 'relevance',
            'fields': ['title', 'abstract', 'authors', 'year', 'journal', 'doi'],
            'cache_results': True
        }
        self.cache = {}
        
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configura el agente con parámetros específicos
        
        Args:
            config: Diccionario con configuración
        """
        self.config.update(config)
    
    async def search(self, query: str) -> Dict[str, Any]:
        """
        Busca literatura científica relevante
        
        Args:
            query: Consulta de búsqueda
        """
        try:
            self.logger.info(f"Buscando literatura para: {query}")
            
            # Verificar caché
            cache_key = f"{query}_{self.config['max_results']}_{self.config['min_year']}"
            if self.config['cache_results'] and cache_key in self.cache:
                self.logger.info("Resultados encontrados en caché")
                return self.cache[cache_key]
            
            # Simular búsqueda (reemplazar con API real)
            results = {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'n_results': self.config['max_results'],
                'papers': [
                    {
                        'title': 'Water Mass Analysis in the Southern Ocean',
                        'authors': ['Smith, J.', 'Johnson, K.'],
                        'year': 2022,
                        'journal': 'Journal of Physical Oceanography',
                        'doi': '10.1029/jpo.2022.001',
                        'abstract': 'Analysis of water masses in the Southern Ocean...'
                    },
                    {
                        'title': 'Modern Methods in Oceanographic Data Analysis',
                        'authors': ['Brown, R.', 'Davis, M.'],
                        'year': 2021,
                        'journal': 'Progress in Oceanography',
                        'doi': '10.1016/j.pocean.2021.002',
                        'abstract': 'Review of modern methods for analyzing oceanographic data...'
                    }
                ],
                'summary': (
                    "La literatura reciente destaca la importancia del análisis "
                    "multivariado en oceanografía, con énfasis en técnicas "
                    "estadísticas avanzadas y machine learning."
                )
            }
            
            # Guardar en caché
            if self.config['cache_results']:
                self.cache[cache_key] = results
                
                # También guardar en disco
                cache_file = self.cache_dir / f"{cache_key}.json"
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Encontrados {len(results['papers'])} artículos relevantes")
            return results
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda de literatura: {str(e)}")
            raise
    
    async def _async_search(self, **kwargs):
        """Wrapper asíncrono para la búsqueda de Tavily"""
        return self.client.search(**kwargs)
    
    async def _process_results(self, 
                             results: Dict[str, Any],
                             include_citations: bool,
                             min_year: int) -> Dict[str, Any]:
        """Procesa y filtra los resultados de la búsqueda"""
        
        processed = {
            'timestamp': datetime.now().isoformat(),
            'summary': results.get('answer', ''),
            'sources': []
        }
        
        for result in results.get('results', []):
            if self._is_valid_source(result, min_year):
                source = {
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('content', '')[:300],
                    'score': result.get('score', 0),
                    'year': self._extract_year(result.get('content', ''))
                }
                
                if include_citations:
                    source['citation'] = self._format_citation(source)
                    
                processed['sources'].append(source)
        
        # Ordenar por relevancia y año
        processed['sources'].sort(
            key=lambda x: (x.get('score', 0), x.get('year', 0)),
            reverse=True
        )
        
        return processed
    
    def _is_valid_source(self, source: Dict[str, Any], min_year: int) -> bool:
        """Verifica si una fuente cumple los criterios de validez"""
        if not source.get('title') or not source.get('url'):
            return False
            
        # Verificar dominio académico
        url = source.get('url', '').lower()
        academic_domains = [
            'sciencedirect.com', 'nature.com', 'springer.com',
            'wiley.com', 'agu.org', 'ieee.org', 'jstor.org',
            'scholar.google.com', 'researchgate.net'
        ]
        if not any(domain in url for domain in academic_domains):
            return False
            
        # Verificar año
        year = self._extract_year(source.get('content', ''))
        if year and year < min_year:
            return False
            
        return True
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extrae el año de publicación del texto"""
        import re
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        if years:
            return max(int(year) for year in years)
        return None
    
    def _format_citation(self, source: Dict[str, Any]) -> str:
        """Formatea una cita en estilo APA"""
        year = source.get('year', 'n.d.')
        title = source.get('title', '')
        url = source.get('url', '')
        
        return f"{title} ({year}). Retrieved from {url}"
    
    def _is_cache_valid(self, cached_results: Dict[str, Any]) -> bool:
        """Verifica si los resultados en caché son válidos (menos de 24 horas)"""
        if 'timestamp' not in cached_results:
            return False
            
        cache_time = datetime.fromisoformat(cached_results['timestamp'])
        age = datetime.now() - cache_time
        return age.total_seconds() < 24 * 3600  # 24 horas
    
    def _cache_results(self, results: Dict[str, Any], cache_file: Path):
        """Guarda los resultados en caché"""
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
    async def get_related_papers(self, 
                               topic: str,
                               n_papers: int = 5) -> List[Dict[str, Any]]:
        """Obtiene papers relacionados con un tema específico"""
        results = await self.search_literature(
            topic=topic,
            max_results=n_papers * 2  # Buscar más para filtrar
        )
        
        if 'error' in results:
            return []
            
        return results['sources'][:n_papers]
    
    async def summarize_findings(self, 
                               topic: str,
                               papers: List[Dict[str, Any]]) -> str:
        """Genera un resumen de los hallazgos principales"""
        if not papers:
            return "No se encontraron papers relevantes."
            
        summary = [
            f"Resumen de investigación sobre: {topic}\n",
            f"Basado en {len(papers)} papers académicos:\n"
        ]
        
        for i, paper in enumerate(papers, 1):
            summary.append(f"\n{i}. {paper['title']}")
            if 'snippet' in paper:
                summary.append(f"   {paper['snippet']}")
                
        return "\n".join(summary)
    
    async def export_bibliography(self,
                                papers: List[Dict[str, Any]],
                                output_file: Optional[Path] = None) -> str:
        """Exporta la bibliografía en formato APA"""
        if not papers:
            return "No hay referencias para exportar."
            
        bibliography = ["Referencias Bibliográficas\n"]
        
        for paper in papers:
            if 'citation' in paper:
                bibliography.append(paper['citation'])
                
        text = "\n\n".join(bibliography)
        
        if output_file:
            output_file.write_text(text, encoding='utf-8')
            
        return text 