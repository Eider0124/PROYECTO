import os
import cv2
import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt

# ================= Configuración =================
DATASET_DIR = './DATASET'
PIXEL_WHITE_THRESHOLD = 235

def interactive_comparison(img_path, sample_name):
    print(f"\nCargando y procesando {sample_name}...")
    
    # 1. Cargar el nivel de baja resolución (Pirámide)
    with tiff.TiffFile(img_path) as tif:
        nivel_elegido = len(tif.pages) - 1 
        image_low_res = tif.pages[nivel_elegido].asarray()
        
    if image_low_res.ndim == 3 and image_low_res.shape[0] == 3:
        image_low_res = np.transpose(image_low_res, (1, 2, 0))
        
    # 2. Convertir a Escala de Grises
    gray = cv2.cvtColor(image_low_res, cv2.COLOR_RGB2GRAY)
    
    # ---------------------------------------------------------
    # CÁLCULO DE MÁSCARAS
    # ---------------------------------------------------------
    # Método A: Umbral Fijo
    mask_fijo = gray <= PIXEL_WHITE_THRESHOLD
    
    # Método B: Umbral Otsu
    otsu_val, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    otsu_val = int(otsu_val)
    mask_otsu = gray <= otsu_val
    
    # ---------------------------------------------------------
    # VENTANA INTERACTIVA (2 Filas x 4 Columnas)
    # ---------------------------------------------------------
    fig, axes = plt.subplots(2, 4, figsize=(18, 9))
    fig.canvas.manager.set_window_title(f"Comparación: {sample_name}")
    
    # --- Fila 0: Umbral Fijo ---
    axes[0, 0].imshow(image_low_res)
    axes[0, 0].set_title(f"Original ({sample_name})")
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(gray, cmap='gray', vmin=0, vmax=255)
    axes[0, 1].set_title("Escala de Grises")
    axes[0, 1].axis('off')
    
    axes[0, 2].imshow(mask_fijo, cmap='gray')
    axes[0, 2].set_title(f"Máscara Fija (<= {PIXEL_WHITE_THRESHOLD})")
    axes[0, 2].axis('off')
    
    # AQUI ESTÁ EL CAMBIO: log=True
    axes[0, 3].hist(gray.ravel(), bins=256, range=[0, 256], color='gray', alpha=0.7, log=True)
    axes[0, 3].axvline(x=PIXEL_WHITE_THRESHOLD, color='red', linestyle='dashed', linewidth=2)
    axes[0, 3].set_title(f"Umbral Fijo ({PIXEL_WHITE_THRESHOLD}) - Escala Log")
    axes[0, 3].set_xlim([0, 256])
    
    # --- Fila 1: Otsu ---
    axes[1, 0].imshow(image_low_res)
    axes[1, 0].set_title("Original (Referencia)")
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(gray, cmap='gray', vmin=0, vmax=255)
    axes[1, 1].set_title("Escala de Grises")
    axes[1, 1].axis('off')
    
    axes[1, 2].imshow(mask_otsu, cmap='gray')
    axes[1, 2].set_title(f"Máscara Otsu (<= {otsu_val})")
    axes[1, 2].axis('off')
    
    # AQUI ESTÁ EL CAMBIO: log=True
    axes[1, 3].hist(gray.ravel(), bins=256, range=[0, 256], color='gray', alpha=0.7, log=True)
    axes[1, 3].axvline(x=otsu_val, color='blue', linestyle='dashed', linewidth=2)
    axes[1, 3].set_title(f"Umbral Dinámico Otsu ({otsu_val}) - Escala Log")
    axes[1, 3].set_xlim([0, 256])
    
    plt.tight_layout()
    print(" -> Mostrando ventana interactiva. Revisa los detalles (puedes usar la lupa).")
    print(" -> Cierra la ventana gráfica para avanzar a la siguiente imagen...")
    
    # Esto despliega la ventana y pausa el código hasta que la cierres
    plt.show() 

if __name__ == "__main__":
    folders = [f.path for f in os.scandir(DATASET_DIR) if f.is_dir()]
    
    for folder in folders:
        sample_name = os.path.basename(folder)
        all_files = os.listdir(folder)
        
        img_files = [f for f in all_files if f.endswith('.tiff') and '_mask' not in f.lower()]
        
        if img_files:
            img_path = os.path.join(folder, img_files[0])
            interactive_comparison(img_path, sample_name)
            
    print("\n¡Has terminado de revisar todas las imágenes!")