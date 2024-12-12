import pytest
from pathlib import Path
from ocean_analysis.core.output_manager import OutputManager

def test_output_structure():
    """Verificar que se crea la estructura correcta de directorios"""
    output_manager = OutputManager("test_outputs")
    
    # Verificar directorios principales
    assert (output_manager.session_dir / "figures").exists()
    assert (output_manager.session_dir / "data").exists()
    assert (output_manager.session_dir / "reports").exists()
    assert (output_manager.session_dir / "logs").exists()
    
    # Verificar subdirectorios
    assert (output_manager.session_dir / "figures" / "ctd_profiles").exists()
    assert (output_manager.session_dir / "data" / "processed").exists()
    assert (output_manager.session_dir / "reports" / "final").exists()

def test_output_saving():
    """Verificar que se pueden guardar outputs correctamente"""
    output_manager = OutputManager("test_outputs")
    
    # Probar guardado de datos
    test_data = {"test": "data"}
    data_path = output_manager.save_data(test_data, "test", "processed")
    assert data_path.exists()
    
    # Probar logging
    output_manager.log_event("Test event")
    log_path = output_manager.get_path('logs', 'system', f"{output_manager.session_id}.log")
    assert log_path.exists() 