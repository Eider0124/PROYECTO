import os
import cv2
import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt

# ================= Configuración =================
DATASET_DIR = './DATASET'
OUTPUT_DIR = './HISTOGRAMAS_WSI_NIVELES'
PIXEL_WHITE_THRESHOLD = 235

os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_wsi_pyramid_histogram(img_path, save_path, sample_name):
    print(f"\nExplorando archivo TIFF de {sample_name}...")
    
    # 1. Abrir el archivo TIFF para ver sus niveles (sin cargarlo todo a la RAM)
    with tiff.TiffFile(img_path) as tif:
        num_niveles = len(tif.pages)
        print(f" -> Este TIFF contiene {num_niveles} niveles de resolución.")
        
        # Seleccionamos la página con la menor resolución (la última)
        # En el dataset PANDA, usualmente el nivel 2 (la 3ra página) es el más pequeño
        nivel_elegido = num_niveles - 1 
        
        print(f" -> Cargando el Nivel {nivel_elegido}...")
        image_low_res = tif.pages[nivel_elegido].asarray()
        
    # 2. Ajustar canales si PANDA lo entrega como (Canales, Alto, Ancho)
    if image_low_res.ndim == 3 and image_low_res.shape[0] == 3:
        image_low_res = np.transpose(image_low_res, (1, 2, 0))
        
    print(f" -> Resolución final cargada: {image_low_res.shape[1]}x{image_low_res.shape[0]}")
    
    # 3. Conversiones de color (de RGB a Escala de Grises)
    gray = cv2.cvtColor(image_low_res, cv2.COLOR_RGB2GRAY)
    
    # 4. Máscara binaria global
    binary_mask = gray <= PIXEL_WHITE_THRESHOLD
    tissue_ratio = binary_mask.sum() / gray.size
    
    print(f" Generando gráfica (Tejido estimado: {tissue_ratio:.1%})...")
    
    # 5. Graficar
    fig, axes = plt.subplots(1, 4, figsize=(18, 5))
    
    axes[0].imshow(image_low_res)
    axes[0].set_title(f"{sample_name}\n(Nivel {nivel_elegido})")
    axes[0].axis('off')
    
    axes[1].imshow(gray, cmap='gray', vmin=0, vmax=255)
    axes[1].set_title("Escala de Grises")
    axes[1].axis('off')
    
    axes[2].imshow(binary_mask, cmap='gray')
    axes[2].set_title(f"Tejido (<= {PIXEL_WHITE_THRESHOLD})")
    axes[2].axis('off')
    
    axes[3].hist(gray.ravel(), bins=256, range=[0, 256], color='gray', alpha=0.7)
    axes[3].axvline(x=PIXEL_WHITE_THRESHOLD, color='red', linestyle='dashed', linewidth=2, label='Umbral 235')
    axes[3].set_title("Histograma Global (Baja Res)")
    axes[3].set_xlim([0, 256])
    axes[3].legend()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
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
            save_path = os.path.join(OUTPUT_DIR, f"piramide_analisis_{sample_name}.png")
            analyze_wsi_pyramid_histogram(img_path, save_path, sample_name)
            
    print("\n¡Análisis completado! Revisa la carpeta HISTOGRAMAS_WSI_NIVELES.")