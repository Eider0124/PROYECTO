import os
import cv2
import numpy as np
import tifffile as tiff
from tqdm import tqdm
import matplotlib.pyplot as plt

# ================= Configuración Ajustada a tu Estructura =================
DATASET_DIR = './DATASET' 
OUTPUT_DIR = './PARCHE_PROCESADO'
PATCH_SIZE = 512
TISSUE_THRESHOLD = 0.4 
PIXEL_WHITE_THRESHOLD = 235 

# --- Variables de Debug ---
DEBUG_MODE = True
DEBUG_LIMIT = 3 # Bajamos a 3 para que no te sature de ventanas al probar
debug_count = 0

IMG_OUT_DIR = os.path.join(OUTPUT_DIR, 'images')
MASK_OUT_DIR = os.path.join(OUTPUT_DIR, 'labels')
os.makedirs(IMG_OUT_DIR, exist_ok=True)
os.makedirs(MASK_OUT_DIR, exist_ok=True)

def show_debug_plot(patch_rgb, gray, binary_mask, threshold_val, tissue_ratio):
    # (Misma función de graficado que antes)
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    axes[0].imshow(patch_rgb)
    axes[0].set_title(f"Original\nTejido: {tissue_ratio:.1%}")
    axes[0].axis('off')
    
    axes[1].imshow(gray, cmap='gray', vmin=0, vmax=255)
    axes[1].set_title("Escala de Grises")
    axes[1].axis('off')
    
    axes[2].imshow(binary_mask, cmap='gray')
    axes[2].set_title(f"Máscara (Tejido <= {threshold_val})")
    axes[2].axis('off')
    
    axes[3].hist(gray.ravel(), bins=256, range=[0, 256], color='gray', alpha=0.7)
    axes[3].axvline(x=threshold_val, color='red', linestyle='dashed', linewidth=2)
    axes[3].set_title("Histograma de Píxeles")
    axes[3].set_xlim([0, 256])
    
    plt.tight_layout()
    plt.show() 

def is_tissue(patch_rgb, threshold_ratio=0.4, pixel_threshold=235, debug=False):
    global debug_count
    gray = cv2.cvtColor(patch_rgb, cv2.COLOR_RGB2GRAY)
    binary_mask = gray <= pixel_threshold
    tissue_pixels = binary_mask.sum()
    tissue_ratio = tissue_pixels / gray.size
    is_valid = tissue_ratio >= threshold_ratio

    if debug and debug_count < DEBUG_LIMIT and is_valid:
        print(f"\n[DEBUG] Evaluando parche útil. Proporción de tejido: {tissue_ratio:.2f}")
        show_debug_plot(patch_rgb, gray, binary_mask, pixel_threshold, tissue_ratio)
        debug_count += 1

    return is_valid

def process_sample(sample_folder):
    sample_name = os.path.basename(sample_folder)
    print(f"\n--- Revisando carpeta: {sample_name} ---")
    
    # Listar todos los archivos en la carpeta
    all_files = os.listdir(sample_folder)
    
    # Buscar imagen principal y máscara (PANDA usa _mask en el nombre de la máscara)
    img_files = [f for f in all_files if f.endswith('.tiff') and '_mask' not in f.lower()]
    lbl_files = [f for f in all_files if f.endswith('.tiff') and '_mask' in f.lower()]
    
    print(f" Imagen encontrada: {img_files}")
    print(f" Máscara encontrada: {lbl_files}")
    
    if not img_files or not lbl_files:
        print(f" [!] Omitiendo {sample_name}: Falta la imagen o la máscara.")
        return

    img_path = os.path.join(sample_folder, img_files[0])
    lbl_path = os.path.join(sample_folder, lbl_files[0])

    print(f" Cargando TIFFs en memoria (esto puede tardar unos segundos)...")
    image = tiff.imread(img_path)
    label = tiff.imread(lbl_path)

    # Ajuste de canales si es necesario
    if image.ndim == 3 and image.shape[0] == 3:
        image = np.transpose(image, (1, 2, 0))
        
    h, w = image.shape[:2]
    print(f" Resolución de la imagen: {w}x{h}")
    patch_count = 0
    
    for y in tqdm(range(0, h, PATCH_SIZE), desc=f"Procesando {sample_name}"):
        for x in range(0, w, PATCH_SIZE):
            img_patch = image[y:y+PATCH_SIZE, x:x+PATCH_SIZE]
            lbl_patch = label[y:y+PATCH_SIZE, x:x+PATCH_SIZE]
            
            if img_patch.shape[0] != PATCH_SIZE or img_patch.shape[1] != PATCH_SIZE:
                continue
                
            if is_tissue(img_patch, TISSUE_THRESHOLD, PIXEL_WHITE_THRESHOLD, debug=DEBUG_MODE):
                patch_name = f"{sample_name}_{y}_{x}.png"
                img_patch_bgr = cv2.cvtColor(img_patch, cv2.COLOR_RGB2BGR)
                
                cv2.imwrite(os.path.join(IMG_OUT_DIR, patch_name), img_patch_bgr)
                cv2.imwrite(os.path.join(MASK_OUT_DIR, patch_name), lbl_patch)
                patch_count += 1
                
    print(f"  -> Se extrajeron {patch_count} parches útiles de {sample_name}")

if __name__ == "__main__":
    folders = [f.path for f in os.scandir(DATASET_DIR) if f.is_dir()]
    if not folders:
        print(f"No se encontraron subcarpetas dentro de {DATASET_DIR}")
        
    for folder in folders:
        process_sample(folder)
    print("\n¡Proceso finalizado!")