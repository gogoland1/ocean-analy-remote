@pytest.mark.asyncio
async def test_report_generation(analyst_agent, sample_data):
    """Probar la generación de reportes"""
    output_dir = Path("test_output/reports")
    
    # Ejecutar análisis
    await analyst_agent.analyze(sample_data)
    
    # Generar reporte PDF
    pdf_path = await analyst_agent.generate_complete_report(
        output_dir, format='pdf'
    )
    assert pdf_path.exists()
    assert pdf_path.suffix == '.pdf'
    
    # Generar paquete ZIP
    zip_path = await analyst_agent.generate_complete_report(
        output_dir, format='zip'
    )
    assert zip_path.exists()
    assert zip_path.suffix == '.zip'
    
    # Verificar contenido del ZIP
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        files = zipf.namelist()
        assert 'analysis_summary.json' in files
        assert any(f.startswith('figures/') for f in files)
        
        # Verificar resumen JSON
        with zipf.open('analysis_summary.json') as f:
            summary = json.load(f)
            assert 'timestamp' in summary
            assert 'analysis_results' in summary
            assert 'figure_inventory' in summary 