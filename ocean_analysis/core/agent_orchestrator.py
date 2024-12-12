from typing import Dict, Any, List
import asyncio
from pathlib import Path

class AgentOrchestrator:
    """
    Orquestador central para la coordinación de agentes
    """
    
    def __init__(self):
        self.supervisor = None
        self.agent_hierarchy = {
            'level_1': ['supervisor'],
            'level_2': ['parser', 'qa'],
            'level_3': ['analyst', 'water_mass', 'stats'],
            'level_4': ['report']
        }
        
        self.dependencies = {
            'parser': [],
            'qa': ['parser'],
            'analyst': ['parser', 'qa'],
            'water_mass': ['parser', 'qa', 'analyst'],
            'stats': ['parser', 'qa', 'analyst'],
            'report': ['parser', 'qa', 'analyst', 'water_mass', 'stats']
        }
        
        self.communication_channels = {}
        
    async def setup_workflow(self):
        """Configura el flujo de trabajo y las comunicaciones entre agentes"""
        # Crear canales de comunicación
        self.communication_channels = {
            'data_queue': asyncio.Queue(),  # Para datos procesados
            'results_queue': asyncio.Queue(),  # Para resultados de análisis
            'feedback_queue': asyncio.Queue(),  # Para feedback del supervisor
            'status_queue': asyncio.Queue()  # Para actualizaciones de estado
        }
        
        # Establecer jerarquía de trabajo
        self.workflow = {
            'stages': [
                {
                    'name': 'data_processing',
                    'agents': ['parser', 'qa'],
                    'parallel': False
                },
                {
                    'name': 'analysis',
                    'agents': ['analyst', 'water_mass', 'stats'],
                    'parallel': True
                },
                {
                    'name': 'reporting',
                    'agents': ['report'],
                    'parallel': False
                }
            ]
        }

class AgentCommunicationProtocol:
    """
    Protocolo de comunicación entre agentes
    """
    
    @staticmethod
    async def send_message(sender: str, receiver: str, 
                         message_type: str, content: Any,
                         channel: asyncio.Queue):
        """Envía mensaje entre agentes"""
        message = {
            'sender': sender,
            'receiver': receiver,
            'type': message_type,
            'content': content,
            'timestamp': datetime.now()
        }
        await channel.put(message)
    
    @staticmethod
    async def request_feedback(agent: str, results: Dict,
                             supervisor_queue: asyncio.Queue):
        """Solicita feedback del supervisor"""
        await AgentCommunicationProtocol.send_message(
            sender=agent,
            receiver='supervisor',
            message_type='feedback_request',
            content=results,
            channel=supervisor_queue
        )

class WorkflowManager:
    """
    Gestor del flujo de trabajo entre agentes
    """
    
    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self.current_stage = None
        self.stage_results = {}
        
    async def execute_workflow(self, input_data: Dict[str, Any]):
        """Ejecuta el flujo de trabajo completo"""
        for stage in self.orchestrator.workflow['stages']:
            self.current_stage = stage['name']
            
            if stage['parallel']:
                # Ejecutar agentes en paralelo
                tasks = [
                    self._execute_agent(agent, input_data)
                    for agent in stage['agents']
                ]
                results = await asyncio.gather(*tasks)
            else:
                # Ejecutar agentes secuencialmente
                results = []
                for agent in stage['agents']:
                    result = await self._execute_agent(agent, input_data)
                    results.append(result)
                    input_data.update(result)
            
            self.stage_results[stage['name']] = results
            
        return self.stage_results
    
    async def _execute_agent(self, agent_name: str, input_data: Dict[str, Any]):
        """Ejecuta un agente específico"""
        # Verificar dependencias
        await self._check_dependencies(agent_name)
        
        # Obtener agente
        agent = self.orchestrator.get_agent(agent_name)
        
        # Ejecutar agente
        results = await agent.analyze(input_data)
        
        # Solicitar feedback del supervisor
        feedback = await self._request_supervisor_feedback(agent_name, results)
        
        # Aplicar correcciones si es necesario
        if feedback['needs_correction']:
            results = await self._apply_corrections(agent, results, feedback)
            
        return results

class AgentIntegrationLayer:
    """
    Capa de integración entre agentes
    """
    
    def __init__(self):
        self.data_transformers = {}
        self.result_validators = {}
        
    def register_transformer(self, source_agent: str, 
                           target_agent: str,
                           transformer: callable):
        """Registra transformador de datos entre agentes"""
        key = f"{source_agent}_to_{target_agent}"
        self.data_transformers[key] = transformer
    
    def register_validator(self, agent: str, validator: callable):
        """Registra validador de resultados para un agente"""
        self.result_validators[agent] = validator
    
    async def transform_data(self, source_agent: str,
                           target_agent: str,
                           data: Any) -> Any:
        """Transforma datos entre agentes"""
        key = f"{source_agent}_to_{target_agent}"
        transformer = self.data_transformers.get(key)
        
        if transformer:
            return await transformer(data)
        return data
    
    async def validate_results(self, agent: str, results: Any) -> bool:
        """Valida resultados de un agente"""
        validator = self.result_validators.get(agent)
        
        if validator:
            return await validator(results)
        return True 