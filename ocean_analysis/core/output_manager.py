from pathlib import Path
from datetime import datetime
import json
import shutil

class OutputManager:
    """Gestor de outputs para el sistema de análisis oceanográfico"""
    
    def __init__(self, base_dir: str = "outputs_final"):
        self.base_dir = Path(base_dir)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.base_dir / self.session_id
        self.setup_directories()
    
    def setup_directories(self):
        """Crear estructura de directorios para outputs"""
        # Directorios principales
        dirs = {
            'figures': ['ctd_profiles', 'water_masses', 'statistics', 'qa'],
            'data': ['processed', 'qa_results', 'analysis_results'],
            'reports': ['qa', 'analysis', 'final'],
            'logs': ['system', 'agents', 'errors']
        }
        
        for main_dir, subdirs in dirs.items():
            for subdir in subdirs:
                (self.session_dir / main_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    def get_path(self, category: str, subcategory: str, filename: str) -> Path:
        """Obtener ruta completa para un archivo de output"""
        return self.session_dir / category / subcategory / filename
    
    def save_figure(self, fig, name: str, category: str):
        """Guardar figura en la categoría correspondiente"""
        path = self.get_path('figures', category, f"{name}.png")
        fig.savefig(path, dpi=300, bbox_inches='tight')
        return path
    
    def save_data(self, data: dict, name: str, category: str):
        """Guardar datos en formato JSON"""
        path = self.get_path('data', category, f"{name}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return path
    
    def save_report(self, content: str, name: str, category: str):
        """Guardar reporte en formato PDF o texto"""
        path = self.get_path('reports', category, f"{name}.pdf")
        # Implementar lógica de guardado según el formato
        return path
    
    def log_event(self, message: str, level: str = 'info', agent: str = 'system'):
        """Registrar evento en los logs"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_path = self.get_path('logs', 'system', f"{self.session_id}.log")
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} - {level.upper()} - {agent} - {message}\n")
    
    def archive_session(self):
        """Comprimir y archivar la sesión actual"""
        archive_path = self.base_dir / f"archive_{self.session_id}.zip"
        shutil.make_archive(
            str(archive_path.with_suffix('')),
            'zip',
            self.session_dir
        )
        return archive_path 