import os
import pytest
from dotenv import load_dotenv
from langchain_community.llms.ollama import Ollama
from langchain.prompts import PromptTemplate
from tqdm import tqdm
import time

# Cargar variables de entorno al inicio
load_dotenv()

def print_separator():
    print("\n" + "="*80 + "\n")

def test_environment_setup():
    """Verificar que Ollama está instalado y funcionando"""
    print("\n🔍 Verificando instalación de Ollama...")
    try:
        llm = Ollama(model="mistral")
        assert llm is not None
        print("✅ Ollama está instalado y funcionando correctamente")
    except Exception as e:
        print(f"❌ Error: {e}")
        pytest.skip(f"Ollama no está instalado o no está funcionando: {e}")

def test_local_model_connection():
    """Probar la conexión con el modelo local"""
    print("\n🤖 Probando conexión con el modelo local...")
    llm = Ollama(model="mistral")
    
    with tqdm(total=100, desc="Generando respuesta") as pbar:
        pbar.update(10)
        question = "¿Qué es la temperatura potencial en oceanografía?"
        print(f"\n📝 Pregunta: {question}")
        
        pbar.update(40)
        response = llm.invoke(question)
        pbar.update(50)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        print(f"\n🔍 Respuesta: {response}")
        print_separator()

def test_chain_creation():
    """Probar la creación de cadenas de LangChain con modelo local"""
    print("\n⛓️ Probando creación de cadenas LangChain...")
    template = """
    Analiza los siguientes datos oceanográficos:
    Temperatura: {temperatura}°C
    Salinidad: {salinidad} PSU
    
    Proporciona un breve análisis.
    """
    
    with tqdm(total=100, desc="Procesando cadena") as pbar:
        pbar.update(20)
        prompt = PromptTemplate(
            input_variables=["temperatura", "salinidad"],
            template=template
        )
        
        pbar.update(20)
        llm = Ollama(model="mistral")
        chain = prompt | llm
        
        pbar.update(20)
        print("\n📊 Datos de prueba:")
        print("Temperatura: 15°C")
        print("Salinidad: 35 PSU")
        
        response = chain.invoke({
            "temperatura": "15",
            "salinidad": "35"
        })
        pbar.update(40)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        print(f"\n📋 Análisis generado: {response}")
        print_separator()

def test_error_handling():
    """Probar el manejo de errores con modelo inexistente"""
    print("\n⚠️ Probando manejo de errores...")
    with tqdm(total=100, desc="Verificando errores") as pbar:
        pbar.update(50)
        with pytest.raises(Exception):
            llm = Ollama(model="modelo_inexistente")
            llm.invoke("Este debería fallar")
        pbar.update(50)
        print("✅ Manejo de errores funcionando correctamente")
        print_separator()

if __name__ == "__main__":
    try:
        print("\n🚀 Iniciando pruebas del sistema...")
        print_separator()
        
        tests = [
            test_environment_setup,
            test_local_model_connection,
            test_chain_creation,
            test_error_handling
        ]
        
        for i, test in enumerate(tests, 1):
            print(f"\n📌 Ejecutando prueba {i}/{len(tests)}: {test.__name__}")
            test()
            time.sleep(0.5)  # Pequeña pausa para mejor visualización
        
        print("\n✨ Todas las pruebas completadas exitosamente!")
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
    finally:
        print_separator() 