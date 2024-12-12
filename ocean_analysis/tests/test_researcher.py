import os
import pytest
from dotenv import load_dotenv
from tavily import TavilyClient
from tqdm import tqdm
import time
import json
import re
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

def print_separator():
    print("\n" + "="*80 + "\n")

class ResearchAgent:
    """Agente investigador para búsqueda de información científica"""
    
    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.sources = []
        
        # Dominios académicos y de acceso abierto
        self.academic_domains = {
            'primary': [
                'scholar.google.com',
                'scielo.org',
                'doaj.org',          # Directory of Open Access Journals
                'arxiv.org',
                'biorxiv.org',
                'zenodo.org',
                'researchgate.net'
            ],
            'journals': [
                'sciencedirect.com',
                'springer.com',
                'wiley.com',
                'tandfonline.com',
                'mdpi.com',          # Open Access
                'frontiersin.org',   # Open Access
                'plos.org',          # Open Access
                'hindawi.com'        # Open Access
            ],
            'oceanographic': [
                'agu.org',           # American Geophysical Union
                'aslo.org',          # Association for the Sciences of Limnology and Oceanography
                'jor.br',            # Brazilian Journal of Oceanography
                'int-res.com',       # Inter-Research Science Publisher
                'ocean-sci.net'      # Ocean Science (Open Access)
            ]
        }
    
    def search_scientific_sources(self, query, max_results=5):
        """Busca fuentes científicas sobre un tema específico"""
        try:
            # Agregar términos de búsqueda académica
            academic_terms = [
                "research", "paper", "journal", "doi", "abstract",
                "methodology", "analysis", "scientific", "study"
            ]
            
            # Construir consulta académica
            academic_query = f"{query} {' OR '.join(academic_terms)}"
            
            # Realizar búsqueda con Tavily
            search_result = self.client.search(
                query=academic_query,
                search_depth="advanced",
                max_results=max_results * 2,  # Buscar más resultados para filtrar
                include_answer=True,
                include_raw_content=True,
                include_images=False,
                search_type="research"  # Enfocado en investigación
            )
            
            # Guardar el resumen generado por Tavily
            if search_result.get('answer'):
                print(f"\n🤖 Resumen de Tavily: {search_result['answer']}")
            
            # Filtrar y clasificar resultados
            scientific_sources = []
            for result in search_result.get('results', []):
                source_info = self._analyze_source(result)
                if source_info:
                    scientific_sources.append(source_info)
            
            # Ordenar por relevancia y tipo de fuente
            scientific_sources.sort(
                key=lambda x: (
                    x['source_type_score'],  # Primero por tipo de fuente
                    x['score'],              # Luego por relevancia
                    x.get('year', 0)         # Finalmente por año (más reciente primero)
                ),
                reverse=True
            )
            
            # Tomar los mejores resultados
            return scientific_sources[:max_results]
            
        except Exception as e:
            print(f"Error en la búsqueda: {str(e)}")
            return []
    
    def _analyze_source(self, result):
        """Analiza y clasifica una fuente"""
        url = result.get('url', '').lower()
        title = result.get('title', '').lower()
        content = result.get('content', '').lower()
        
        # Verificar si es una fuente académica
        source_type = self._get_source_type(url)
        if not source_type:
            return None
            
        # Extraer información adicional
        doi = self._extract_doi(content) or self._extract_doi(url)
        year = self._extract_year(content) or self._extract_year(title)
        abstract = self._extract_abstract(content)
        
        # Calcular puntuación de relevancia
        relevance_score = self._calculate_relevance(result, source_type)
        
        return {
            'title': result.get('title', ''),
            'url': result.get('url', ''),
            'source_type': source_type,
            'source_type_score': self._get_source_type_score(source_type),
            'year': year,
            'doi': doi,
            'abstract': abstract,
            'score': relevance_score,
            'content': content[:500] if content else ''
        }
    
    def _get_source_type(self, url):
        """Determina el tipo de fuente basado en el dominio"""
        for domain_type, domains in self.academic_domains.items():
            if any(domain in url for domain in domains):
                return domain_type
        return None
    
    def _get_source_type_score(self, source_type):
        """Asigna una puntuación según el tipo de fuente"""
        scores = {
            'oceanographic': 1.0,
            'primary': 0.9,
            'journals': 0.8
        }
        return scores.get(source_type, 0.5)
    
    def _extract_doi(self, text):
        """Extrae DOI del texto"""
        doi_pattern = r'(10\.\d{4,}/[-._;()/:\w]+)'
        match = re.search(doi_pattern, text)
        return match.group(1) if match else None
    
    def _extract_year(self, text):
        """Extrae el año de publicación del texto"""
        current_year = datetime.now().year
        year_pattern = r'\b(19|20)\d{2}\b'
        years = [int(y) for y in re.findall(year_pattern, text)]
        valid_years = [y for y in years if 1900 <= y <= current_year]
        return max(valid_years) if valid_years else None
    
    def _extract_abstract(self, text):
        """Extrae el abstract del texto"""
        abstract_patterns = [
            r'abstract[:\s]+(.*?)(?=introduction|\n\n|$)',
            r'resumen[:\s]+(.*?)(?=introducción|\n\n|$)',
            r'summary[:\s]+(.*?)(?=introduction|\n\n|$)'
        ]
        
        for pattern in abstract_patterns:
            match = re.search(pattern, text.lower(), re.IGNORECASE | re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                return abstract[:500] + '...' if len(abstract) > 500 else abstract
        return None
    
    def _calculate_relevance(self, result, source_type):
        """Calcula la relevancia de una fuente"""
        base_score = result.get('score', 0)
        
        # Factores de ajuste
        adjustments = {
            'has_doi': 0.2,
            'has_abstract': 0.2,
            'recent_year': 0.1,
            'open_access': 0.2
        }
        
        # Verificar factores
        if self._extract_doi(result.get('content', '')):
            base_score += adjustments['has_doi']
        
        if self._extract_abstract(result.get('content', '')):
            base_score += adjustments['has_abstract']
        
        year = self._extract_year(result.get('content', ''))
        if year and year >= 2020:
            base_score += adjustments['recent_year']
        
        if any(domain in result.get('url', '').lower() for domain in ['scielo', 'doaj', 'arxiv', 'mdpi', 'frontiersin', 'plos']):
            base_score += adjustments['open_access']
        
        return min(base_score, 1.0)  # Normalizar a máximo 1.0

def test_researcher():
    """Prueba básica del agente investigador"""
    print("\n🔍 Probando búsqueda de información oceanográfica...")
    
    try:
        researcher = ResearchAgent()
        
        # Temas específicos de oceanografía con consultas simplificadas
        topics = {
            "CTD": {
                "query": "CTD conductivity temperature depth analysis methods oceanography sciencedirect springer",
                "description": "Métodos de análisis de datos CTD"
            },
            "Water Masses": {
                "query": "water mass identification temperature salinity diagram open access doaj scielo",
                "description": "Identificación de masas de agua"
            },
            "Stability": {
                "query": "ocean density stratification water column stability calculation methods",
                "description": "Cálculo de estabilidad oceánica"
            }
        }
        
        all_results = {}
        
        for topic_key, topic_info in topics.items():
            print(f"\n📖 Investigando: {topic_info['description']}")
            print(f"🔎 Consulta: {topic_info['query']}")
            
            results = researcher.search_scientific_sources(
                topic_info['query'],
                max_results=5
            )
            all_results[topic_key] = results
            
            if results:
                print(f"\n✅ Encontrados {len(results)} resultados relevantes")
                
                # Mostrar resumen de hallazgos
                print("\n📑 Resumen de hallazgos:")
                for i, result in enumerate(results, 1):
                    source_type = result['source_type']
                    source_icon = {
                        'oceanographic': '🌊',
                        'primary': '📚',
                        'journals': '📰'
                    }.get(source_type, '📄')
                    
                    relevance = result['score']
                    stars = "⭐" * int(relevance * 5)  # 0-5 estrellas basado en relevancia
                    
                    print(f"\n{source_icon} Fuente {i} {stars}")
                    print(f"   📚 Título: {result['title']}")
                    print(f"   🔗 URL: {result['url']}")
                    print(f"   📊 Relevancia: {relevance:.2f}")
                    print(f"   📂 Tipo: {source_type.title()}")
                    
                    if result.get('doi'):
                        print(f"   🔍 DOI: {result['doi']}")
                    if result.get('year'):
                        print(f"   📅 Año: {result['year']}")
                    if result.get('abstract'):
                        print(f"   📝 Abstract: {result['abstract'][:200]}...")
                        
                    # Indicadores adicionales
                    if "pdf" in result['url'].lower():
                        print("   📄 PDF disponible")
                    if any(domain in result['url'].lower() for domain in ['scielo', 'doaj', 'arxiv', 'mdpi', 'frontiersin', 'plos']):
                        print("   🔓 Acceso Abierto")
            else:
                print(f"\n⚠️ No se encontraron resultados para este tema")
            
            print_separator()
        
        # Resumen final
        print("\n📊 Resumen de la investigación:")
        total_sources = sum(len(results) for results in all_results.values())
        print(f"\n📚 Total de fuentes encontradas: {total_sources}")
        
        for topic_key, results in all_results.items():
            print(f"\n{topic_key}:")
            print(f"- Fuentes encontradas: {len(results)}")
            if results:
                avg_relevance = sum(r['score'] for r in results) / len(results)
                print(f"- Relevancia promedio: {avg_relevance:.2f}")
                
                # Análisis de tipos de fuentes
                source_types = [r['source_type'] for r in results]
                print("- Distribución de fuentes:")
                for source_type in set(source_types):
                    count = source_types.count(source_type)
                    print(f"  • {source_type.title()}: {count}")
                
                # Análisis de años
                years = [r.get('year') for r in results if r.get('year')]
                if years:
                    print(f"- Rango de años: {min(years)} - {max(years)}")
                
                # Análisis de acceso
                open_access = sum(1 for r in results if any(domain in r['url'].lower() 
                    for domain in ['scielo', 'doaj', 'arxiv', 'mdpi', 'frontiersin', 'plos']))
                print(f"- Artículos de acceso abierto: {open_access}/{len(results)}")
                
                # Análisis de formatos
                pdfs = sum(1 for r in results if "pdf" in r['url'].lower())
                print(f"- Documentos PDF: {pdfs}/{len(results)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en la prueba: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🚀 Iniciando prueba del agente investigador...")
    print_separator()
    
    success = test_researcher()
    
    if success:
        print("\n✨ Prueba completada exitosamente!")
    else:
        print("\n⚠️ La prueba falló. Revise los mensajes de error anteriores.")
    
    print_separator() 