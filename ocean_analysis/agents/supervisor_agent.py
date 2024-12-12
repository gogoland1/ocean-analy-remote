from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import asyncio
from datetime import datetime
import json
import logging
from .parser_agent import ParserAgent
from .qa_agent import QAAgent
from .analyst_agent import AnalystAgent
from .stats_agent import StatsAgent
from .water_mass_agent import WaterMassAgent
from .report_agent import ReportAgent
from .poster_agent import PosterAgent
from .researcher_agent import ResearcherAgent

class SupervisorAgent:
    """
    Agente supervisor que actúa como product manager y coordinador general
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = None
        self.agents = {}
        self.workflow_status = {}
        self.feedback_history = []
        self.report_reviews = []
        
    async def initialize_workflow(self, 
                                data_path: Path,
                                config: Dict[str, Any]) -> None:
        """
        Inicializa el flujo de trabajo y configura los agentes
        """
        self.config = config
        self.logger.info("Iniciando workflow de análisis oceanográfico")
        
        # Registrar agentes
        self.agents = {
            'parser': self._initialize_parser_agent(),
            'qa': self._initialize_qa_agent(),
            'analyst': self._initialize_analyst_agent(),
            'stats': self._initialize_stats_agent(),
            'water_mass': self._initialize_water_mass_agent(),
            'report': self._initialize_report_agent(),
            'poster': self._initialize_poster_agent(),
            'researcher': self._initialize_researcher_agent()
        }
        
        # Configurar agentes
        await self._configure_agents(data_path)
        
        # Entrevistar agentes para verificar preparación
        await self._interview_agents()
        
        # Iniciar workflow
        self.workflow_status = {
            'start_time': datetime.now(),
            'status': 'initialized',
            'current_stage': 'data_parsing',
            'completed_stages': [],
            'pending_stages': [
                'data_parsing',
                'quality_control',
                'analysis',
                'statistics',
                'water_mass_analysis',
                'reporting'
            ]
        }
        
    def _initialize_parser_agent(self) -> ParserAgent:
        """Inicializa el agente parser"""
        agent = ParserAgent()
        if 'data' in self.config:
            agent.configure(self.config['data'])
        return agent
    
    def _initialize_qa_agent(self) -> QAAgent:
        """Inicializa el agente QA"""
        agent = QAAgent()
        if 'qa' in self.config:
            agent.configure(self.config['qa'])
        return agent
    
    def _initialize_analyst_agent(self) -> AnalystAgent:
        """Inicializa el agente analyst"""
        agent = AnalystAgent()
        if 'analysis' in self.config:
            agent.configure(self.config['analysis'])
        return agent
    
    def _initialize_stats_agent(self) -> StatsAgent:
        """Inicializa el agente stats"""
        agent = StatsAgent()
        if 'analysis' in self.config:
            agent.configure(self.config['analysis'])
        return agent
    
    def _initialize_water_mass_agent(self) -> WaterMassAgent:
        """Inicializa el agente water mass"""
        agent = WaterMassAgent()
        if 'water_masses' in self.config:
            agent.configure(self.config['water_masses'])
        return agent
    
    def _initialize_report_agent(self) -> ReportAgent:
        """Inicializa el agente report"""
        agent = ReportAgent()
        if 'output' in self.config:
            agent.configure(self.config['output'])
        return agent
    
    def _initialize_poster_agent(self) -> PosterAgent:
        """Inicializa el agente poster"""
        agent = PosterAgent()
        if 'output' in self.config:
            agent.configure(self.config['output'])
        return agent
    
    def _initialize_researcher_agent(self) -> ResearcherAgent:
        """Inicializa el agente researcher"""
        agent = ResearcherAgent()
        if 'research' in self.config:
            agent.configure(self.config['research'])
        return agent
    
    async def _configure_agents(self, data_path: Path) -> None:
        """Configura los agentes con datos y parámetros específicos"""
        try:
            # Verificar que el archivo de datos existe
            if not data_path.exists():
                raise FileNotFoundError(f"No se encontró el archivo de datos: {data_path}")
            
            # Configurar rutas y parámetros específicos
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'set_data_path'):
                    agent.set_data_path(data_path)
                    
                if hasattr(agent, 'initialize'):
                    await agent.initialize()
                    
        except Exception as e:
            self.logger.error(f"Error configurando agentes: {str(e)}")
            raise
    
    async def _interview_agents(self) -> None:
        """
        Entrevista a cada agente para verificar su preparación y configuración
        """
        for agent_name, agent in self.agents.items():
            self.logger.info(f"Entrevistando agente: {agent_name}")
            
            # Verificar configuración
            config_status = await self._verify_agent_config(agent)
            if not config_status:
                raise ValueError(f"Error en configuración del agente {agent_name}")
            
            # Verificar inicialización
            if hasattr(agent, 'initialize'):
                try:
                    await agent.initialize()
                except Exception as e:
                    self.logger.error(f"Error inicializando agente {agent_name}: {str(e)}")
                    raise
    
    async def _verify_agent_config(self, agent: Any) -> bool:
        """
        Verifica la configuración de un agente
        
        Args:
            agent: Agente a verificar
            
        Returns:
            bool: True si la configuración es válida
        """
        try:
            # Verificar que el agente tenga método configure
            if not hasattr(agent, 'configure'):
                self.logger.error(f"Agente {agent.__class__.__name__} no tiene método configure")
                return False
            
            # Verificar que el agente tenga atributo config
            if not hasattr(agent, 'config'):
                self.logger.error(f"Agente {agent.__class__.__name__} no tiene atributo config")
                return False
            
            # Verificar que config sea un diccionario
            if not isinstance(agent.config, dict):
                self.logger.error(f"Config del agente {agent.__class__.__name__} no es un diccionario")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error verificando configuración: {str(e)}")
            return False
    
    async def coordinate_analysis(self) -> Dict[str, Any]:
        """
        Coordina el proceso completo de análisis
        """
        try:
            # Parsing de datos
            parsed_data = await self._coordinate_parsing()
            
            # Control de calidad
            qa_results = await self._coordinate_qa(parsed_data)
            
            # Análisis principales
            analysis_results = await self._coordinate_analysis_phase(qa_results)
            
            # Análisis estadísticos
            stats_results = await self._coordinate_stats(analysis_results)
            
            # Análisis de masas de agua
            water_mass_results = await self._coordinate_water_mass_analysis(analysis_results)
            
            # Generar reporte
            report = await self._coordinate_reporting(
                parsed_data,
                qa_results,
                analysis_results,
                stats_results,
                water_mass_results
            )
            
            return {
                'status': 'completed',
                'results': {
                    'parsing': parsed_data,
                    'qa': qa_results,
                    'analysis': analysis_results,
                    'statistics': stats_results,
                    'water_masses': water_mass_results,
                    'report': report
                },
                'workflow_status': self.workflow_status
            }
            
        except Exception as e:
            self.logger.error(f"Error en coordinación: {str(e)}")
            raise
    
    async def review_report(self, report_path: Path, 
                          user_feedback: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Revisa el informe final y proporciona feedback
        """
        review_results = {
            'timestamp': datetime.now(),
            'status': 'pending',
            'feedback': [],
            'recommendations': [],
            'approval_status': 'pending'
        }
        
        # Realizar revisión automática
        auto_review = await self._perform_automated_review(report_path)
        review_results['automated_review'] = auto_review
        
        # Incorporar feedback del usuario si existe
        if user_feedback:
            review_results['user_feedback'] = user_feedback
            
        # Evaluar criterios de calidad
        quality_evaluation = await self._evaluate_report_quality(report_path)
        review_results['quality_evaluation'] = quality_evaluation
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(
            auto_review,
            quality_evaluation,
            user_feedback
        )
        review_results['recommendations'] = recommendations
        
        # Determinar estado de aprobación
        approval_status = self._determine_approval_status(
            auto_review,
            quality_evaluation,
            user_feedback
        )
        review_results['approval_status'] = approval_status
        
        # Registrar revisión
        self.report_reviews.append(review_results)
        
        return review_results
    
    def provide_feedback(self, stage: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Proporciona feedback sobre resultados específicos
        """
        feedback = {
            'stage': stage,
            'timestamp': datetime.now(),
            'evaluation': self._evaluate_results(stage, results),
            'recommendations': self._generate_stage_recommendations(stage, results),
            'quality_metrics': self._calculate_quality_metrics(stage, results)
        }
        
        self.feedback_history.append(feedback)
        return feedback
    
    def _evaluate_results(self, stage: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evalúa resultados según criterios específicos por etapa
        """
        evaluation = {
            'completeness': self._check_completeness(stage, results),
            'quality': self._assess_quality(stage, results),
            'consistency': self._verify_consistency(stage, results),
            'issues': self._identify_issues(stage, results)
        }
        
        return evaluation
    
    def _calculate_quality_metrics(self, stage: str, 
                                 results: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcula métricas de calidad específicas por etapa
        """
        metrics = {}
        
        if stage == 'parsing':
            metrics.update(self._calculate_parsing_metrics(results))
        elif stage == 'qa':
            metrics.update(self._calculate_qa_metrics(results))
        elif stage == 'analysis':
            metrics.update(self._calculate_analysis_metrics(results))
        elif stage == 'reporting':
            metrics.update(self._calculate_report_metrics(results))
            
        return metrics
    
    def _determine_approval_status(self, auto_review: Dict,
                                 quality_eval: Dict,
                                 user_feedback: Optional[Dict]) -> str:
        """
        Determina el estado de aprobación del informe
        """
        # Criterios mínimos de calidad
        quality_threshold = 0.8
        
        # Evaluar revisión automática
        auto_score = self._calculate_auto_review_score(auto_review)
        
        # Evaluar calidad
        quality_score = self._calculate_quality_score(quality_eval)
        
        # Considerar feedback del usuario
        user_score = 1.0
        if user_feedback:
            user_score = self._calculate_user_feedback_score(user_feedback)
            
        # Calcular score final
        final_score = (auto_score * 0.4 + quality_score * 0.4 + user_score * 0.2)
        
        if final_score >= quality_threshold:
            return 'approved'
        elif final_score >= quality_threshold * 0.8:
            return 'needs_minor_revision'
        else:
            return 'needs_major_revision'
    
    async def verify_outputs(self, output_dir: Path) -> bool:
        """
        Verifica que todos los outputs necesarios estén presentes
        
        Args:
            output_dir: Directorio de outputs
            
        Returns:
            bool: True si todos los outputs están presentes
        """
        try:
            # Lista de archivos requeridos
            required_files = [
                'figures/ctd_profiles.png',
                'figures/ts_diagram.png',
                'figures/vertical_sections.png',
                'figures/spatial_distribution.png'
            ]
            
            # Verificar cada archivo
            missing_files = []
            for file in required_files:
                file_path = output_dir / file
                if not file_path.exists():
                    self.logger.warning(f"No se encuentra el archivo: {file}")
                    missing_files.append(file)
            
            if missing_files:
                self.logger.warning(f"Faltan los siguientes archivos: {missing_files}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error verificando outputs: {str(e)}")
            return False