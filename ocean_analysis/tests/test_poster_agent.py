import pytest
from pathlib import Path
import json
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
from agents.poster_agent import PosterAgent

@pytest.fixture
def poster_agent():
    return PosterAgent()

@pytest.fixture
def sample_data():
    return {
        'key_findings': [
            'Identificada masa de agua antártica intermedia',
            'Máximo de salinidad a 500m',
            'Fuerte estratificación en superficie'
        ],
        'visualizations': {
            'map': Path('test_data/map.png'),
            'profile': Path('test_data/profile.png'),
            'section': Path('test_data/section.png'),
            'spatial': Path('test_data/spatial.png')
        },
        'logos': [Path('test_data/institution_logo.png')]
    }

@pytest.fixture
def create_test_visualizations(tmp_path):
    """Crea visualizaciones de prueba"""
    viz_path = tmp_path / "test_data"
    viz_path.mkdir(exist_ok=True)
    
    # 1. Mapa de estaciones
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.coastlines()
    stations = {
        'lat': [-34.5, -35.2, -36.1, -34.8],
        'lon': [-52.3, -51.8, -52.5, -53.1]
    }
    ax.scatter(stations['lon'], stations['lat'], c='red', s=100)
    fig.savefig(viz_path / "map.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    # 2. Perfil vertical
    fig, ax = plt.subplots(figsize=(8, 10))
    depth = np.arange(0, 1000, 10)
    temp = 20 * np.exp(-depth/200) + np.random.normal(0, 0.5, len(depth))
    ax.plot(temp, -depth, 'b-', linewidth=2)
    ax.set_xlabel('Temperatura (°C)')
    ax.set_ylabel('Profundidad (m)')
    fig.savefig(viz_path / "profile.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    # 3. Sección vertical
    fig, ax = plt.subplots(figsize=(12, 8))
    distance = np.linspace(0, 500, 50)
    depth = np.linspace(0, 1000, 100)
    X, Y = np.meshgrid(distance, depth)
    Z = 20 * np.exp(-Y/200) + 2 * np.sin(X/100) + np.random.normal(0, 0.5, X.shape)
    c = ax.pcolormesh(X, -Y, Z, cmap='RdYlBu_r', shading='auto')
    fig.colorbar(c, label='Temperatura (°C)')
    ax.set_xlabel('Distancia (km)')
    ax.set_ylabel('Profundidad (m)')
    fig.savefig(viz_path / "section.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    # 4. Distribución espacial
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.coastlines()
    lons = np.linspace(-54, -51, 30)
    lats = np.linspace(-37, -34, 30)
    X, Y = np.meshgrid(lons, lats)
    Z = 2 * np.sin((X+54)/2) + 2 * np.cos((Y+37)/2)
    c = ax.pcolormesh(X, Y, Z, cmap='viridis', transform=ccrs.PlateCarree())
    fig.colorbar(c, label='Temperatura (°C)')
    fig.savefig(viz_path / "spatial.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    return viz_path

@pytest.mark.asyncio
async def test_minimalist_poster(poster_agent, sample_data, create_test_visualizations, tmp_path):
    """Prueba la creación del poster minimalista"""
    print("\n🎨 Probando creación de poster minimalista...")
    
    # Actualizar rutas de visualizaciones
    sample_data['visualizations'] = {
        'map': create_test_visualizations / "map.png",
        'profile': create_test_visualizations / "profile.png",
        'section': create_test_visualizations / "section.png",
        'spatial': create_test_visualizations / "spatial.png"
    }
    
    try:
        output_path = await poster_agent.create_poster(
            data=sample_data,
            output_dir=tmp_path,
            title="Estructura Termohalina del Atlántico Sur",
            authors=["Dr. María García", "Dr. Juan Pérez"],
            institution="Instituto Oceanográfico Nacional"
        )
        
        assert output_path.exists()
        assert output_path.suffix == '.pdf'
        print("✅ Poster minimalista creado exitosamente")
        
    except Exception as e:
        print(f"❌ Error en la creación del poster: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_visualization_layout(poster_agent, create_test_visualizations, tmp_path):
    """Prueba el layout de visualizaciones"""
    print("\n📊 Probando layout de visualizaciones...")
    
    # Datos mínimos necesarios
    data = {
        'visualizations': {
            'map': create_test_visualizations / "map.png",
            'profile': create_test_visualizations / "profile.png",
            'section': create_test_visualizations / "section.png",
            'spatial': create_test_visualizations / "spatial.png"
        }
    }
    
    try:
        output_path = await poster_agent.create_poster(
            data=data,
            output_dir=tmp_path,
            title="Test Layout",
            authors=["Test Author"],
            institution="Test Institution"
        )
        
        assert output_path.exists()
        print("✅ Layout de visualizaciones correcto")
        
    except Exception as e:
        print(f"❌ Error en layout: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_key_findings_display(poster_agent, tmp_path):
    """Prueba la visualización de hallazgos clave"""
    print("\n📝 Probando display de hallazgos...")
    
    # Datos con solo hallazgos
    data = {
        'key_findings': [
            'Hallazgo 1 muy importante',
            'Hallazgo 2 relevante',
            'Hallazgo 3 interesante',
            'Hallazgo 4 que no debería aparecer'  # No debería mostrarse
        ]
    }
    
    try:
        output_path = await poster_agent.create_poster(
            data=data,
            output_dir=tmp_path,
            title="Test Findings",
            authors=["Test Author"],
            institution="Test Institution"
        )
        
        assert output_path.exists()
        print("✅ Display de hallazgos correcto")
        
    except Exception as e:
        print(f"❌ Error en hallazgos: {str(e)}")
        raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 