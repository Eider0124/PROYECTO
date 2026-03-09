import os
import cv2
import random
import matplotlib.pyplot as plt

# ================= Configuración =================
PATCHES_DIR = './PARCHE_PROCESADO_V0/images'
OUTPUT_DIR = './HISTOGRAMAS_PRESENTACION' # Aquí se guardarán las fotos para tu presentación
PIXEL_WHITE_THRESHOLD = 235 # El umbral que usamos
NUM_MUESTRAS = 5 # Cuántos parches al azar quieres graficar

os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_and_save_plot(img_path, save_path):
    # Cargar la imagen (cv2 la carga en BGR, la pasamos a RGB para Matplotlib)
    img_bgr = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    # Escala de grises
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # Máscara binaria (Tejido <= umbral)
    binary_mask = gray <= PIXEL_WHITE_THRESHOLD
    
    # Calcular % de tejido
    tissue_ratio = binary_mask.sum() / gray.size
    
    # Crear la figura
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    
    # 1. Original
    axes[0].imshow(img_rgb)
    axes[0].set_title(f"Parche Original\nTejido: {tissue_ratio:.1%}")
    axes[0].axis('off')
    
    # 2. Grises
    axes[1].imshow(gray, cmap='gray', vmin=0, vmax=255)
    axes[1].set_title("Escala de Grises")
    axes[1].axis('off')
    
    # 3. Máscara
    axes[2].imshow(binary_mask, cmap='gray')
    axes[2].set_title(f"Máscara (Tejido <= {PIXEL_WHITE_THRESHOLD})")
    axes[2].axis('off')
    
    # 4. Histograma
    axes[3].hist(gray.ravel(), bins=256, range=[0, 256], color='gray', alpha=0.7)
    axes[3].axvline(x=PIXEL_WHITE_THRESHOLD, color='red', linestyle='dashed', linewidth=2, label='Umbral')
    axes[3].set_title("Histograma")
    axes[3].set_xlim([0, 256])
    axes[3].legend()
    
    plt.tight_layout()
    
    # Guardar la figura para la presentación y luego mostrarla
    plt.savefig(save_path, dpi=300, bbox_inches='tight') # dpi=300 para alta calidad en tu presentación
    print(f" Guardado: {save_path}")
    plt.show() # Cierra la ventana para ver el siguiente

if __name__ == "__main__":
    # Obtener todos los parches generados
    todas_las_imagenes = [f for f in os.listdir(PATCHES_DIR) if f.endswith('.png')]
    
    if not todas_las_imagenes:
        print(f"No se encontraron imágenes en {PATCHES_DIR}")
    else:
        # Seleccionar muestras al azar
        muestras = random.sample(todas_las_imagenes, min(NUM_MUESTRAS, len(todas_las_imagenes)))
        
        print(f"Generando histogramas para {len(muestras)} parches al azar...")
        
        for i, nombre_img in enumerate(muestras):
            img_path = os.path.join(PATCHES_DIR, nombre_img)
            save_path = os.path.join(OUTPUT_DIR, f"analisis_{i+1}_{nombre_img}")
            
            analyze_and_save_plot(img_path, save_path)
            
        print(f"\n¡Listo! Revisa la carpeta {OUTPUT_DIR} para ver las imágenes de tu presentación.")