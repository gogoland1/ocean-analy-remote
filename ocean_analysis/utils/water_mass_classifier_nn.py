import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
from sklearn.utils.class_weight import compute_class_weight
import joblib
import os

def load_and_prepare_data():
    """
    Cargar y preparar datos para el entrenamiento
    """
    # Leer datos
    data = pd.read_csv("ocean_analysis/data_tests/datosgerlache_nut.csv", 
                      sep=';', 
                      decimal='.', 
                      encoding='latin-1')
    
    # Extraer features (T, S, O2)
    features = [
        'Pot. Temp. [ºC]',
        'salinity [PSU]',
        'O2[umol/kg]'
    ]
    
    # Generar etiquetas y obtener máscara de datos válidos
    temp = data['Pot. Temp. [ºC]'].values
    sal = data['salinity [PSU]'].values
    o2 = data['O2[umol/kg]'].values
    
    # Obtener etiquetas y máscara de datos válidos
    labels, valid_mask = label_water_masses(temp, sal, o2)
    
    # Aplicar máscara a los features
    X = data[features].values[valid_mask]
    
    # Normalizar features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, labels, scaler, data

def create_model(input_shape):
    """
    Crear modelo de red neuronal
    """
    model = models.Sequential([
        # Capa de entrada
        layers.Dense(64, activation='relu', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        
        # Capas intermedias
        layers.Dense(32, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        
        layers.Dense(16, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        
        # Capa de salida (4 clases de masas de agua)
        layers.Dense(4, activation='softmax')
    ])
    
    # Compilar modelo
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer,
                 loss='sparse_categorical_crossentropy',
                 metrics=['accuracy'])
    
    return model

def label_water_masses(temp, sal, o2):
    """
    Etiquetar masas de agua según criterios físicos
    """
    total_samples = len(temp)
    labels = np.full(total_samples, -1)  # -1 para no clasificados
    
    # GMW (Glacial Meltwater)
    gmw_mask = ((temp >= -1.5) & (temp <= 1.5) &
                (sal >= 32.8) & (sal <= 33.8) &
                (o2 >= 180))
    
    # mCDW (modified Circumpolar Deep Water)
    mcdw_mask = ((temp >= 0.0) & (temp <= 2.0) &
                 (sal >= 34.3) & (sal <= 34.75) &
                 (o2 < 200))
    
    # HSSW (High Salinity Shelf Water)
    hssw_mask = ((temp >= -2.0) & (temp <= 0.0) &
                 (sal >= 34.5) & (sal <= 34.9) &
                 (o2 >= 180) & (o2 <= 350))
    
    # AASW (Antarctic Surface Water)
    aasw_mask = ((temp >= -1.5) & (temp <= 1.5) &
                 (sal >= 33.6) & (sal <= 34.5) &
                 (o2 >= 230) & (o2 <= 350) &
                 ~gmw_mask)  # No es GMW
    
    # Asignar etiquetas
    labels[aasw_mask] = 0  # AASW
    labels[gmw_mask] = 1   # GMW
    labels[mcdw_mask] = 2  # mCDW
    labels[hssw_mask] = 3  # HSSW
    
    # Imprimir estadísticas
    print("\nEstadísticas de clasificación:")
    print(f"Total de muestras: {total_samples}")
    print(f"AASW (0): {np.sum(aasw_mask)} muestras ({np.sum(aasw_mask)/total_samples*100:.1f}%)")
    print(f"GMW (1): {np.sum(gmw_mask)} muestras ({np.sum(gmw_mask)/total_samples*100:.1f}%)")
    print(f"mCDW (2): {np.sum(mcdw_mask)} muestras ({np.sum(mcdw_mask)/total_samples*100:.1f}%)")
    print(f"HSSW (3): {np.sum(hssw_mask)} muestras ({np.sum(hssw_mask)/total_samples*100:.1f}%)")
    print(f"Sin clasificar: {np.sum(labels == -1)} muestras ({np.sum(labels == -1)/total_samples*100:.1f}%)")
    
    # Obtener máscara de datos válidos
    valid_mask = labels >= 0
    
    return labels[valid_mask], valid_mask

def plot_training_history(history):
    """
    Visualizar el historial de entrenamiento
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Gráfico de pérdida
    ax1.plot(history.history['loss'], label='Entrenamiento')
    ax1.plot(history.history['val_loss'], label='Validación')
    ax1.set_title('Pérdida del Modelo')
    ax1.set_xlabel('Época')
    ax1.set_ylabel('Pérdida')
    ax1.legend()
    ax1.grid(True)
    
    # Gráfico de precisión
    ax2.plot(history.history['accuracy'], label='Entrenamiento')
    ax2.plot(history.history['val_accuracy'], label='Validación')
    ax2.set_title('Precisión del Modelo')
    ax2.set_xlabel('Época')
    ax2.set_ylabel('Precisión')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    os.makedirs('test_outputs', exist_ok=True)
    plt.savefig('test_outputs/training_history.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Cargar y preparar datos
    X_scaled, labels, scaler, data = load_and_prepare_data()
    
    # Dividir en conjuntos de entrenamiento y validación
    X_train, X_val, y_train, y_val = train_test_split(
        X_scaled, labels, test_size=0.2, random_state=42
    )
    
    # Calcular pesos de clases para manejar desbalance
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(y_train),
        y=y_train
    )
    class_weight_dict = dict(enumerate(class_weights))
    
    # Crear y entrenar modelo
    model = create_model(input_shape=(3,))  # 3 features: T, S, O2
    
    history = model.fit(
        X_train, y_train,
        epochs=100,
        batch_size=32,
        validation_data=(X_val, y_val),
        class_weight=class_weight_dict,
        verbose=1
    )
    
    # Evaluar modelo
    test_loss, test_accuracy = model.evaluate(X_val, y_val, verbose=0)
    print(f"\nPrecisión en validación: {test_accuracy:.4f}")
    
    # Guardar modelo y scaler
    model.save('water_mass_classifier.h5')
    joblib.dump(scaler, 'feature_scaler.pkl')
    print("\nModelo guardado como: water_mass_classifier.h5")
    print("Scaler guardado como: feature_scaler.pkl")
    
    # Visualizar entrenamiento
    plot_training_history(history)
    print("\nHistorial de entrenamiento guardado en: test_outputs/training_history.png")

if __name__ == '__main__':
    main() 