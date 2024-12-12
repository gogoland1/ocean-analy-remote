# 🌊 Guía de Usuario: Sistema de Análisis Oceanográfico

## 📚 Índice
1. [Introducción](#introducción)
2. [Requisitos Básicos](#requisitos-básicos)
3. [Instalación](#instalación)
4. [Uso Paso a Paso](#uso-paso-a-paso)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [Solución de Problemas](#solución-de-problemas)

## 🎯 Introducción
¡Bienvenido al Sistema de Análisis Oceanográfico! Este sistema utiliza inteligencia artificial para ayudarte a analizar datos oceanográficos de manera sencilla y efectiva. Es como tener un equipo de expertos oceanógrafos trabajando contigo.

## 💻 Requisitos Básicos
- Computadora con Windows, Mac o Linux
- Python 3.8 o superior (no te preocupes, ¡te enseñaremos a instalarlo!)
- Conocimientos básicos de uso de computadora
- Tus datos oceanográficos en formato CSV

## 🔧 Instalación

### Paso 1: Instalar Python
1. Ve a [python.org](https://python.org)
2. Descarga la última versión de Python 3
3. Durante la instalación, **¡importante!** marca la casilla "Add Python to PATH"

### Paso 2: Instalar el Sistema
1. Descarga este proyecto
2. Abre una terminal o símbolo del sistema
3. Navega hasta la carpeta del proyecto
4. Ejecuta:
```bash
pip install -r requirements.txt
```

## 🚀 Uso Paso a Paso

### 1. Preparar tus Datos
- Coloca tu archivo CSV en la carpeta `ocean_analysis/data_tests/`
- Asegúrate de que tu archivo tenga las columnas necesarias:
  - Temperatura
  - Salinidad
  - Oxígeno
  - Profundidad
  - Nutrientes (opcional)

### 2. Análisis Básico
```python
# Ejemplo simple de uso
from ocean_analysis import OceanographicAgentSystem

# Crear el sistema
sistema = OceanographicAgentSystem()

# Analizar datos
resultado = sistema.process_dataset("mi_archivo.csv")
```

### 3. Visualizaciones
Para crear gráficos bonitos de tus datos:

```python
# Crear un mapa de distribución
python plot_surface_distribution.py

# Crear una sección vertical
python plot_vertical_section.py

# Analizar masas de agua
python plot_water_masses_section.py
```

## 📊 Ejemplos Prácticos

### Ejemplo 1: Mapa de Clorofila
```python
# Este código creará un mapa de distribución de clorofila
python plot_surface_distribution.py --variable "Chl-A"
```

### Ejemplo 2: Sección Vertical de Temperatura
```python
# Este código creará una sección vertical de temperatura
python plot_vertical_section.py --variable "temperature"
```

### Ejemplo 3: Clasificación de Masas de Agua
```python
# Este código analizará y clasificará las masas de agua
python water_mass_classifier_nn.py
```

## ❓ Solución de Problemas

### Problema: "No encuentra el archivo"
✅ Solución: Asegúrate de que tu archivo está en la carpeta correcta y el nombre coincide exactamente.

### Problema: "Error al instalar requisitos"
✅ Solución: Intenta instalar los requisitos uno por uno:
```bash
pip install numpy
pip install pandas
pip install matplotlib
```

### Problema: "Gráficos no se ven bien"
✅ Solución: Ajusta el tamaño de la figura:
```python
plt.figure(figsize=(15, 10))
```

## 🎨 Personalización

### Cambiar Colores
Puedes modificar los colores de los gráficos:
```python
colors = ['blue', 'green', 'red', 'purple']  # Usa tus colores favoritos
```

### Ajustar Etiquetas
Personaliza las etiquetas de tus gráficos:
```python
plt.title('Mi Título')
plt.xlabel('Distancia (km)')
plt.ylabel('Profundidad (m)')
```

## 📝 Notas Importantes
- Siempre haz una copia de seguridad de tus datos
- Los gráficos se guardan automáticamente en la carpeta `test_outputs`
- Si necesitas ayuda, ¡no dudes en preguntar!

## 🤝 Soporte
Si tienes dudas o problemas:
1. Revisa esta guía
2. Consulta los ejemplos
3. Pregunta en el foro de la comunidad

## 🌟 Consejos Finales
- Empieza con archivos pequeños para practicar
- Experimenta con diferentes visualizaciones
- Guarda copias de tus mejores gráficos
- ¡Diviértete explorando tus datos oceanográficos!

---
¡Esperamos que esta guía te ayude a sacar el máximo provecho del Sistema de Análisis Oceanográfico! 🌊🔬📊 