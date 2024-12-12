import pytest
from pathlib import Path
import numpy as np
import pandas as pd
from agents.qa_agent import QAAgent, QualityFlag

@pytest.fixture
def qa_agent():
    return QAAgent()

@pytest.fixture
def sample_data():
    # Crear datos de prueba
    np.random.seed(42)
    n_samples = 100
    
    data = pd.DataFrame({
        'temperature': np.random.normal(15, 2, n_samples),
        'salinity': np.random.normal(35, 0.5, n_samples),
        'pressure': np.arange(0, n_samples * 10, 10)
    })
    
    # Agregar algunos problemas de calidad
    data.loc[10, 'temperature'] = 50  # Valor fuera de rango
    data.loc[20:25, 'salinity'] = 35.5  # Valores atascados
    data.loc[30, 'temperature'] = np.nan  # Valor faltante
    
    return data

@pytest.mark.asyncio
async def test_qa_visualizations(qa_agent, sample_data):
    """Probar generación de visualizaciones"""
    metadata = {'variable_mapping': {
        'temperature': 'temperature',
        'salinity': 'salinity',
        'pressure': 'pressure'
    }}
    
    # Ejecutar QA
    await qa_agent.run_qa(sample_data, metadata)
    
    # Generar visualizaciones
    output_dir = Path("test_output/qa_plots")
    plot_paths = qa_agent.generate_qa_visualizations(output_dir)
    
    # Verificar que se generaron los plots
    assert plot_paths['ts_diagram'].exists()
    assert all(path.exists() for path in plot_paths['profile_plots'].values())

@pytest.mark.asyncio
async def test_correction_recommendations(qa_agent, sample_data):
    """Probar recomendaciones de corrección"""
    metadata = {'variable_mapping': {
        'temperature': 'temperature',
        'salinity': 'salinity'
    }}
    
    # Ejecutar QA
    await qa_agent.run_qa(sample_data, metadata)
    
    # Obtener recomendaciones
    recommendations = qa_agent.generate_correction_recommendations()
    
    # Verificar estructura
    assert 'temperature' in recommendations
    assert 'salinity' in recommendations
    
    # Verificar que se detectaron los problemas insertados
    temp_recs = recommendations['temperature']
    assert any(rec['issue'] == 'physical_limits' for rec in temp_recs)
    
    sal_recs = recommendations['salinity']
    assert any(rec['issue'] == 'stuck_values' for rec in sal_recs)

@pytest.mark.asyncio
async def test_international_standards(qa_agent, sample_data):
    """Probar aplicación de estándares internacionales"""
    metadata = {'variable_mapping': {
        'temperature': 'temperature',
        'salinity': 'salinity'
    }}
    
    # Ejecutar QA
    await qa_agent.run_qa(sample_data, metadata)
    
    # Aplicar estándares
    standards_results = qa_agent.apply_international_standards()
    
    # Verificar estructura
    assert 'gtspp' in standards_results
    assert 'woce' in standards_results
    assert 'argo' in standards_results
    
    # Verificar resultados GTSPP
    gtspp = standards_results['gtspp']
    assert 'temperature' in gtspp
    assert 'salinity' in gtspp 