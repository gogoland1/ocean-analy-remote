import pytest
from pathlib import Path
from agents.parser import ParserAgent, ParserError
import pandas as pd
import json
import xarray as xr

TEST_DATA_DIR = Path("D:/agent_oceanic/ocean_analysis/data_tests")

@pytest.fixture
def parser_agent():
    return ParserAgent()

@pytest.mark.asyncio
async def test_csv_files_exist():
    """Verificar que los archivos de prueba existen"""
    csv_files = list(TEST_DATA_DIR.glob("*.csv"))
    assert len(csv_files) == 3, "Deberían existir 3 archivos CSV de prueba"

@pytest.mark.asyncio
async def test_parse_all_csv_files(parser_agent):
    """Probar el parsing de todos los archivos CSV disponibles"""
async def test_netcdf_parsing(parser_agent):
    # Asumiendo un archivo de prueba en data/test/
    test_file = Path("data/test/sample.nc")
    result = await parser_agent.parse(test_file)
    
    assert 'metadata' in result
    assert 'data' in result
    assert result['format'] == 'netcdf'

@pytest.mark.asyncio
async def test_csv_variable_identification(parser_agent):
    test_file = Path("data/test/sample.csv")
    result = await parser_agent.parse(test_file)
    
    assert 'variable_mapping' in result['metadata']
    mapping = result['metadata']['variable_mapping']
    
    # Verificar identificación de variables comunes
    if 'temperature' in result['metadata']['variables']:
        assert 'temperature' in mapping

@pytest.mark.asyncio
async def test_unsupported_format(parser_agent):
    with pytest.raises(ValueError):
        await parser_agent.parse("invalid_file.xyz") 

@pytest.mark.asyncio
async def test_outlier_detection(parser_agent):
    """Probar la detección de outliers"""
    for csv_file in TEST_DATA_DIR.glob("*.csv"):
        result = await parser_agent.parse(csv_file)
        
        assert 'outliers' in result['metadata']
        
        # Verificar estructura del análisis de outliers
        for var_name, outlier_info in result['metadata']['outliers'].items():
            assert 'n_outliers' in outlier_info
            assert 'outlier_indices' in outlier_info
            assert 'outlier_percentage' in outlier_info
            
            # Imprimir información útil
            if outlier_info['n_outliers'] > 0:
                print(f"\nOutliers encontrados en {csv_file.name}, variable {var_name}:")
                print(f"Cantidad: {outlier_info['n_outliers']}")
                print(f"Porcentaje: {outlier_info['outlier_percentage']:.2f}%")

@pytest.mark.asyncio
async def test_missing_data_analysis(parser_agent):
    """Probar el análisis de datos faltantes"""
    for csv_file in TEST_DATA_DIR.glob("*.csv"):
        result = await parser_agent.parse(csv_file)
        
        assert 'missing_data' in result['metadata']
        missing_analysis = result['metadata']['missing_data']
        
        # Verificar estructura del análisis
        assert 'summary' in missing_analysis
        assert 'patterns' in missing_analysis
        assert 'consecutive_gaps' in missing_analysis
        
        # Imprimir resumen de datos faltantes
        print(f"\nAnálisis de datos faltantes en {csv_file.name}:")
        print(f"Variables con datos faltantes:")
        for var, info in missing_analysis['summary'].items():
            if info['missing_count'] > 0:
                print(f"- {var}: {info['missing_percentage']:.2f}% faltante")
                
        print(f"Filas completas: {missing_analysis['patterns']['rows_complete']}")
        print(f"Filas con algún dato faltante: {missing_analysis['patterns']['rows_with_any_missing']}")

@pytest.mark.asyncio
async def test_quality_summary(parser_agent):
    """Probar el resumen de calidad de datos"""
    for csv_file in TEST_DATA_DIR.glob("*.csv"):
        result = await parser_agent.parse(csv_file)
        
        assert 'quality_summary' in result
        summary = result['quality_summary']
        
        print(f"\nResumen de calidad para {csv_file.name}:")
        print(f"Total de variables: {summary['total_variables']}")
        print(f"Variables identificadas: {summary['identified_variables']}")
        print("Problemas encontrados:")
        print(f"- Variables con outliers: {summary['data_quality']['variables_with_outliers']}")
        print(f"- Variables con datos faltantes: {summary['data_quality']['variables_with_missing']}")
        print(f"- Variables fuera de rango: {summary['data_quality']['variables_out_of_range']}")

@pytest.mark.asyncio
async def test_multiple_outlier_detection_methods(parser_agent):
    """Probar los diferentes métodos de detección de outliers"""
    for csv_file in TEST_DATA_DIR.glob("*.csv"):
        result = await parser_agent.parse(csv_file)
        
        for var_name, outlier_info in result['metadata']['outliers'].items():
            print(f"\nAnálisis de outliers para {csv_file.name}, variable {var_name}:")
            
            # Comparar resultados de diferentes métodos
            print("Outliers detectados por método:")
            print(f"- Desviación estándar: {outlier_info['std_method']['n_outliers']}")
            print(f"- IQR: {outlier_info['iqr_method']['n_outliers']}")
            print(f"- Z-score modificado: {outlier_info['zscore_method']['n_outliers']}")
            
            # Analizar consenso
            consensus = outlier_info['consensus']
            print("\nAnálisis de consenso:")
            print(f"- Outliers por consenso: {consensus['n_consensus_outliers']}")
            print(f"- Outliers posibles (todos los métodos): {consensus['n_all_possible_outliers']}")
            
            # Verificar estructura de la información
            assert 'std_method' in outlier_info
            assert 'iqr_method' in outlier_info
            assert 'zscore_method' in outlier_info
            assert 'consensus' in outlier_info

@pytest.mark.asyncio
async def test_outlier_severity(parser_agent):
    """Probar el cálculo de severidad de outliers"""
    for csv_file in TEST_DATA_DIR.glob("*.csv"):
        result = await parser_agent.parse(csv_file)
        
        for var_name, outlier_info in result['metadata']['outliers'].items():
            consensus_outliers = outlier_info['consensus']['consensus_outliers']
            
            if consensus_outliers:
                print(f"\nOutliers más severos en {csv_file.name}, variable {var_name}:")
                data = result['data'][var_name]
                
                # Calcular y mostrar severidad para cada outlier por consenso
                severities = [
                    (idx, parser_agent._calculate_outlier_severity(data, idx))
                    for idx in consensus_outliers
                ]
                
                # Ordenar por severidad
                severities.sort(key=lambda x: x[1], reverse=True)
                
                # Mostrar los 5 outliers más severos
                for idx, severity in severities[:5]:
                    value = data.iloc[idx]
                    print(f"Índice: {idx}, Valor: {value:.2f}, Severidad: {severity:.2f}")

@pytest.mark.asyncio
async def test_distribution_analysis(parser_agent):
    """Probar el análisis de distribución de datos"""
    output_dir = TEST_DATA_DIR / "distribution_plots"
    
    for csv_file in TEST_DATA_DIR.glob("*.csv"):
        result = await parser_agent.parse(csv_file)
        
        # Generar análisis de distribución
        distribution_analysis = parser_agent.generate_distribution_analysis(output_dir)
        
        print(f"\nAnálisis de distribución para {csv_file.name}:")
        for var_name, analysis in distribution_analysis.items():
            dist_stats = analysis['distribution_stats']
            
            print(f"\nVariable: {var_name}")
            print(f"Estadísticas de distribución:")
            print(f"- Media: {dist_stats['mean']:.2f}")
            print(f"- Mediana: {dist_stats['median']:.2f}")
            print(f"- Desviación estándar: {dist_stats['std']:.2f}")
            print(f"- Asimetría: {dist_stats['skewness']:.2f}")
            print(f"- Kurtosis: {dist_stats['kurtosis']:.2f}")
            
            # Verificar test de normalidad
            normality = dist_stats['normality_test']
            print(f"\nTest de Normalidad ({normality['test_name']}):")
            print(f"- p-valor: {normality['p_value']:.4f}")
            
            # Verificar que se generó el gráfico
            if 'plot_path' in analysis:
                print(f"Gráfico generado en: {analysis['plot_path']}")
                assert Path(analysis['plot_path']).exists()

        # Verificar estructura del análisis
        for analysis in distribution_analysis.values():
            assert 'distribution_stats' in analysis
            assert 'histogram_stats' in analysis
            assert 'bin_counts' in analysis['histogram_stats']
            assert 'bin_edges' in analysis['histogram_stats']

@pytest.mark.asyncio
async def test_workflow_initialization(parser_agent):
    """Probar la inicialización del flujo de trabajo"""
    # Simular selección de tipo de datos
    async def mock_get_data_type():
        return DataType.CSV
    
    parser_agent._get_data_type = mock_get_data_type
    
    # Simular selección de validaciones
    async def mock_configure_validations(data_type):
        return {
            'check_structure': True,
            'check_metadata': True,
            'check_variables': True,
            'outliers': True,
            'distribution': True
        }
    
    parser_agent._configure_validations = mock_configure_validations
    
    # Inicializar workflow
    config = await parser_agent.initialize_workflow()
    
    # Verificar configuración
    assert config['data_type'] == DataType.CSV
    assert 'info' in config
    assert 'validations' in config
    
    # Probar parsing con configuración
    for csv_file in TEST_DATA_DIR.glob("*.csv"):
        result = await parser_agent.parse_with_config(csv_file)
        
        # Verificar que se aplicaron las validaciones configuradas
        assert 'outliers' in result
        assert 'distribution' in result
        
        print(f"\nResultados del parsing configurado para {csv_file.name}:")
        print(f"Tipo de datos: {config['data_type'].value}")
        print("Validaciones aplicadas:")
        for validation, enabled in config['validations'].items():
            if enabled:
                print(f"- {validation}")

@pytest.mark.asyncio
async def test_data_export(parser_agent):
    """Probar la exportación de resultados"""
    output_dir = TEST_DATA_DIR / "exports"
    
    for csv_file in TEST_DATA_DIR.glob("*.csv"):
        # Procesar archivo
        result = await parser_agent.parse(csv_file)
        
        # Exportar resultados
        export_paths = await parser_agent.export_results(
            output_dir,
            formats=['csv', 'json', 'html']
        )
        
        print(f"\nExportación de resultados para {csv_file.name}:")
        
        # Verificar que se generaron los archivos
        for fmt, path in export_paths.items():
            assert Path(path).exists()
            print(f"- Archivo {fmt.upper()} generado: {path}")
        
        # Verificar contenido del resumen
        with open(export_paths['summary'], 'r', encoding='utf-8') as f:
            summary_content = f.read()
            print("\nResumen de exportación:")
            print(summary_content)
        
        # Verificar JSON
        with open(export_paths['json'], 'r', encoding='utf-8') as f:
            analysis_results = json.load(f)
            assert 'metadata' in analysis_results
            assert 'quality_summary' in analysis_results
            
        # Verificar CSV
        df_exported = pd.read_csv(export_paths['csv'])
        assert len(df_exported) == len(result['data'])

@pytest.mark.asyncio
async def test_oceanographic_export(parser_agent):
    """Probar la exportación en formatos oceanográficos"""
    output_dir = TEST_DATA_DIR / "exports"
    
    for csv_file in TEST_DATA_DIR.glob("*.csv"):
        # Procesar archivo
        result = await parser_agent.parse(csv_file)
        
        # Exportar en ambos formatos
        export_paths = await parser_agent.export_results(
            output_dir,
            formats=['csv', 'nc']
        )
        
        print(f"\nExportación de datos oceanográficos para {csv_file.name}:")
        
        # Verificar CSV
        csv_path = export_paths['csv']
        assert csv_path.exists()
        
        # Leer y verificar metadata en CSV
        with open(csv_path, 'r') as f:
            header_lines = [next(f) for _ in range(3)]
            assert all(line.startswith('#') for line in header_lines)
        
        # Verificar NetCDF
        nc_path = export_paths['nc']
        assert nc_path.exists()
        
        # Leer y verificar estructura NetCDF
        ds = xr.open_dataset(nc_path)
        print("\nEstructura del archivo NetCDF:")
        print(f"Variables: {list(ds.variables)}")
        print(f"Dimensiones: {dict(ds.dims)}")
        print("\nAtributos globales:")
        for attr, value in ds.attrs.items():
            print(f"- {attr}: {value}")
            
        # Verificar atributos de variables
        for var in ds.variables:
            print(f"\nAtributos de {var}:")
            for attr, value in ds[var].attrs.items():
                print(f"- {attr}: {value}")