import os
import cv2
import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt

# ================= Configuración =================
DATASET_DIR = './DATASET'
OUTPUT_DIR = './HISTOGRAMAS_WSI' # Nueva carpeta para estos análisis
PIXEL_WHITE_THRESHOLD = 235

os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_wsi_histogram(img_path, save_path, sample_name):
    print(f"\nCargando imagen original de {sample_name}...")
    
    # 1. Cargar la imagen gigante
    image = tiff.imread(img_path)
    if image.ndim == 3 and image.shape[0] == 3:
        image = np.transpose(image, (1, 2, 0))
        
    # 2. SUBMUESTREO CRÍTICO (Tomamos 1 de cada 20 píxeles en X y Y)
    # Esto evita el colapso de la memoria RAM
    img_small = image[::20, ::20] 
    
    # 3. Conversiones de color
    # tifffile carga en RGB nativo. Lo pasamos a gris usando la fórmula de OpenCV
    gray = cv2.cvtColor(img_small, cv2.COLOR_RGB2GRAY)
    
    # 4. Máscara binaria global
    binary_mask = gray <= PIXEL_WHITE_THRESHOLD
    tissue_ratio = binary_mask.sum() / gray.size
    
    print(f" Generando gráfica (Tejido estimado: {tissue_ratio:.1%})...")
    
    # 5. Graficar
    fig, axes = plt.subplots(1, 4, figsize=(18, 5))
    
    axes[0].imshow(img_small)
    axes[0].set_title(f"{sample_name}\n(Vista Macro)")
    axes[0].axis('off')
    
    axes[1].imshow(gray, cmap='gray', vmin=0, vmax=255)
    axes[1].set_title("Escala de Grises")
    axes[1].axis('off')
    
    axes[2].imshow(binary_mask, cmap='gray')
    axes[2].set_title(f"Tejido (<= {PIXEL_WHITE_THRESHOLD})")
    axes[2].axis('off')
    
    axes[3].hist(gray.ravel(), bins=256, range=[0, 256], color='gray', alpha=0.7)
    axes[3].axvline(x=PIXEL_WHITE_THRESHOLD, color='red', linestyle='dashed', linewidth=2, label='Umbral 235')
    axes[3].set_title("Histograma Global")
    axes[3].set_xlim([0, 256])
    axes[3].legend()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close() # Cerramos la figura en memoria para no saturar la PC
    print(f" -> Guardado exitosamente en: {save_path}")

if __name__ == "__main__":
    folders = [f.path for f in os.scandir(DATASET_DIR) if f.is_dir()]
    
    for folder in folders:
        sample_name = os.path.basename(folder)
        all_files = os.listdir(folder)
        
        # Buscar la imagen principal (ignorando la máscara)
        img_files = [f for f in all_files if f.endswith('.tiff') and '_mask' not in f.lower()]
        
        if img_files:
            img_path = os.path.join(folder, img_files[0])
            save_path = os.path.join(OUTPUT_DIR, f"macro_analisis_{sample_name}.png")
            analyze_wsi_histogram(img_path, save_path, sample_name)
            
    print("\n¡Análisis WSI completado! Revisa la carpeta HISTOGRAMAS_WSI.")