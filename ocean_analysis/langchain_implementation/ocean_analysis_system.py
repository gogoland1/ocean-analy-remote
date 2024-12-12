from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from pathlib import Path
from ocean_analysis.core.output_manager import OutputManager

# Configuración del entorno
load_dotenv()

# Configurar variables de entorno para LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "pr-indelible-cloakroom-64"

# Inicializar el modelo
llm = ChatOpenAI()

# Resto de las importaciones para nuestras herramientas
from langchain.agents import Tool, AgentExecutor, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from typing import Dict, Any, List

# Definición de herramientas (mantener el código existente de las herramientas)
class ParserTool(BaseTool):
    name = "DataParserTool"
    description = """
    Herramienta para procesar y parsear datos oceanográficos.
    Útil para leer y estructurar datos de CTD, botellas, y otros formatos oceanográficos.
    Input: ruta al archivo de datos
    Output: datos estructurados y validados
    """
    
    def _run(self, file_path: str) -> Dict:
        # Implementar lógica del ParserAgent aquí
        return {"status": "parsed", "data": "structured_data"}

class QATool(BaseTool):
    name = "QualityControlTool"
    description = """
    Herramienta para control de calidad de datos oceanográficos.
    Realiza validaciones, detección de outliers y control de calidad.
    Input: datos estructurados
    Output: datos validados con flags de calidad
    """
    
    def _run(self, data: Dict) -> Dict:
        # Implementar lógica del QAAgent aquí
        return {"status": "validated", "qa_results": "quality_flags"}

class AnalysisTool(BaseTool):
    name = "OceanAnalysisTool"
    description = """
    Herramienta para análisis oceanográfico.
    Realiza análisis de perfiles, secciones y propiedades del agua.
    Input: datos validados
    Output: resultados de análisis oceanográfico
    """
    
    def _run(self, data: Dict) -> Dict:
        # Implementar lógica del AnalystAgent aquí
        return {"status": "analyzed", "analysis": "ocean_properties"}

class WaterMassTool(BaseTool):
    name = "WaterMassAnalysisTool"
    description = """
    Herramienta para análisis de masas de agua.
    Identifica y caracteriza masas de agua usando diagramas T-S y OMP.
    Input: datos analizados
    Output: caracterización de masas de agua
    """
    
    def _run(self, data: Dict) -> Dict:
        # Implementar lógica del WaterMassAgent aquí
        return {"status": "identified", "water_masses": "mass_characteristics"}

class StatsTool(BaseTool):
    name = "StatisticalAnalysisTool"
    description = """
    Herramienta para análisis estadístico.
    Realiza análisis multivariado, clusters y tests estadísticos.
    Input: datos analizados
    Output: resultados estadísticos
    """
    
    def _run(self, data: Dict) -> Dict:
        # Implementar lógica del StatsAgent aquí
        return {"status": "analyzed", "stats": "statistical_results"}

# Modificar la función de configuración del sistema
def setup_ocean_analysis_system():
    """Configurar el sistema de análisis oceanográfico"""
    
    # Crear instancias de herramientas
    tools = [
        ParserTool(),
        QATool(),
        AnalysisTool(),
        WaterMassTool(),
        StatsTool()
    ]
    
    # Configurar memoria
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Crear agente ejecutor
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        tools=tools,
        llm=llm,  # Usar el llm ya configurado
        memory=memory,
        verbose=True,
        max_iterations=5
    )
    
    return agent_executor

# 3. Función principal para ejecutar análisis
async def run_ocean_analysis(
    agent_executor: AgentExecutor,
    data_path: str,
    analysis_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Ejecuta el análisis oceanográfico completo
    """
    try:
        # Iniciar análisis
        response = await agent_executor.arun(
            f"Analizar datos oceanográficos en {data_path} "
            f"con la siguiente configuración: {analysis_config}"
        )
        
        return {
            "status": "success",
            "response": response,
            "chat_history": agent_executor.memory.chat_memory.messages
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "chat_history": agent_executor.memory.chat_memory.messages
        }

class OceanAnalysisSystem:
    def __init__(self):
        self.output_manager = OutputManager()
        self.setup_agents()
    
    def setup_agents(self):
        # Configuración existente...
        self.output_manager.log_event("Sistema inicializado correctamente")
    
    async def run_analysis(self, data_path: str, config: Dict[str, Any]):
        try:
            self.output_manager.log_event(f"Iniciando análisis de {data_path}")
            
            # Ejecutar análisis...
            results = await self.run_ocean_analysis(...)
            
            # Guardar resultados
            self.output_manager.save_data(
                results,
                "analysis_results",
                "analysis_results"
            )
            
            # Guardar figuras
            for fig in results.get('figures', []):
                self.output_manager.save_figure(
                    fig,
                    fig['name'],
                    fig['category']
                )
            
            # Generar y guardar reporte
            report_path = self.output_manager.save_report(
                results['report'],
                "final_report",
                "final"
            )
            
            # Archivar sesión
            archive_path = self.output_manager.archive_session()
            
            return {
                'status': 'success',
                'report_path': report_path,
                'archive_path': archive_path
            }
            
        except Exception as e:
            self.output_manager.log_event(
                f"Error en análisis: {str(e)}",
                level='error'
            )
            raise

# Ejemplo de uso
if __name__ == "__main__":
    # Configurar sistema
    agent_system = setup_ocean_analysis_system()
    
    # Prueba simple para verificar la conexión
    try:
        response = llm.invoke("Hello, world!")
        print("Respuesta del modelo:", response)
        
        # Continuar con el análisis oceanográfico
        data_path = Path("data/raw/sample_ctd.csv")
        analysis_config = {
            "region": "Pacific",
            "analysis_type": "full",
            "required_analyses": [
                "water_masses",
                "statistical",
                "vertical_sections"
            ]
        }
        
        results = asyncio.run(run_ocean_analysis(
            agent_system,
            data_path,
            analysis_config
        ))
        
        print("\n=== Resultados del Análisis ===")
        print(f"Estado: {results['status']}")
        print("\nRespuesta del sistema:")
        print(results['response'])
        
    except Exception as e:
        print(f"\n❌ Error: {e}")