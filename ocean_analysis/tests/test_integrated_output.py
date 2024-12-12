import pytest
from pathlib import Path
import shutil
import asyncio
from ocean_analysis.agents import (
    ParserAgent,
    QAAgent,
    AnalystAgent,
    StatsAgent,
    WaterMassAgent,
    PosterAgent,
    ReportAgent,
    SupervisorAgent,
    ResearcherAgent
)

class TestIntegratedOutput:
    """Pruebas de integración para la generación de outputs"""
    
    @pytest.fixture(scope="class")
    def setup_agents(self):
        """Inicializar agentes una sola vez para toda la clase"""
        return {
            'parser': ParserAgent(),
            'qa': QAAgent(),
            'analyst': AnalystAgent(),
            'stats': StatsAgent(),
            'water_mass': WaterMassAgent(),
            'poster': PosterAgent(),
            'report': ReportAgent(),
            'supervisor': SupervisorAgent(),
            'researcher': ResearcherAgent()
        }
    
    @pytest.fixture(scope="function")
    def output_dir(self):
        """Crear y limpiar directorio para outputs"""
        output_dir = Path("ocean_analysis/test_outputs")
        # Limpiar directorio si existe
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    @pytest.fixture(scope="function")
    def sample_data_path(self):
        """Ruta al archivo de datos de muestra"""
        return Path("ocean_analysis/data/raw/sample_ctd.csv")
    
    @pytest.fixture(scope="function")
    def config(self):
        """Configuración de prueba"""
        return {
            'data': {
                'variables': ['temperature', 'salinity', 'depth'],
                'units': {
                    'temperature': '°C',
                    'salinity': 'PSU',
                    'depth': 'm'
                }
            },
            'qa': {
                'outlier_threshold': 3,
                'min_values': {
                    'temperature': -2,
                    'salinity': 0,
                    'depth': 0
                },
                'max_values': {
                    'temperature': 35,
                    'salinity': 40,
                    'depth': 12000
                }
            },
            'analysis': {
                'depth_bins': [-10, -50, -100, -200, -500, -1000],
                'grid_resolution': 0.5,
                'interpolation_method': 'linear'
            },
            'water_masses': {
                'clusters': 3,
                'min_points': 10
            },
            'output': {
                'formats': ['csv', 'netcdf'],
                'plots': ['profiles', 'sections', 'maps'],
                'report_type': 'technical'
            }
        }
    
    @pytest.mark.asyncio
    async def test_integrated_output(self, setup_agents, output_dir, sample_data_path, config):
        """Prueba la generación integrada de outputs"""
        print("\n🚀 Iniciando prueba integrada del sistema multiagente...")
        
        try:
            # 0. Supervisor inicia el proceso
            print("\n👨‍💼 Supervisor iniciando proceso...")
            supervisor = setup_agents['supervisor']
            await supervisor.initialize_workflow(sample_data_path, config)
            
            # 1. Parser procesa datos
            print("\n📊 Parser procesando datos...")
            parser = setup_agents['parser']
            parsed_data = await parser.parse(sample_data_path)
            
            # 2. QA verifica calidad
            print("\n🔍 QA verificando calidad...")
            qa = setup_agents['qa']
            qa_results = await qa.check_quality(parsed_data)
            
            # 3. Analyst genera visualizaciones
            print("\n📈 Analyst generando visualizaciones...")
            analyst = setup_agents['analyst']
            analyst.set_output_dir(output_dir)  # Configurar directorio de salida
            viz_results = await analyst.analyze(qa_results['clean_data'])
            
            # 4. Stats realiza análisis estadístico
            print("\n📊 Stats realizando análisis...")
            stats = setup_agents['stats']
            stats_results = await stats.analyze(qa_results['clean_data'])
            
            # 5. Water Mass identifica masas de agua
            print("\n🌊 Water Mass identificando masas de agua...")
            water_mass = setup_agents['water_mass']
            wm_results = await water_mass.analyze(qa_results['clean_data'])
            
            # 6. Researcher busca referencias
            print("\n📚 Researcher buscando referencias...")
            researcher = setup_agents['researcher']
            research_results = await researcher.search("oceanographic water masses analysis methodology")
            
            # Compilar resultados
            results = {
                'qa': qa_results,
                'visualizations': {
                    'figures': viz_results['visualizations']['figures']
                },
                'statistics': stats_results,
                'water_masses': wm_results,
                'research': research_results
            }
            
            # 7. Poster genera póster
            print("\n🖼️ Poster generando póster...")
            poster = setup_agents['poster']
            poster_path = await poster.generate_poster(
                results,
                output_dir,
                "Análisis Oceanográfico Integrado",
                ["Equipo de Investigación"]
            )
            
            # 8. Report genera reporte técnico
            print("\n📄 Report generando reporte...")
            report = setup_agents['report']
            report_path = await report.generate_report(
                results,
                output_dir,
                "Análisis Oceanográfico Detallado",
                ["Equipo de Investigación"]
            )
            
            # 9. Supervisor finaliza y verifica
            print("\n✅ Supervisor verificando outputs...")
            success = await supervisor.verify_outputs(output_dir)
            
            assert success, "La verificación de outputs falló"
            assert poster_path.exists(), "No se generó el póster"
            assert report_path.exists(), "No se generó el reporte"
            
            print("\n🎉 Prueba integrada completada exitosamente!")
            
        except Exception as e:
            print(f"\n❌ Error en la prueba integrada: {str(e)}")
            raise 