import os
import cv2
import numpy as np
import tifffile as tiff

# ================= Configuración =================
DATASET_DIR = './DATASET'
OUTPUT_DIR = './PARCHES_UTILES_V1'
PATCH_SIZE = 512
UMBRAL_TEJIDO_MINIMO = 0.20 # El parche debe tener al menos 20% de tejido para guardarse

os.makedirs(OUTPUT_DIR, exist_ok=True)

def procesar_y_extraer_parches(img_path, sample_name):
    print(f"\n--- Analizando {sample_name} a máxima resolución ---")
    
    # Crear carpeta específica para esta muestra
    sample_out_dir = os.path.join(OUTPUT_DIR, sample_name)
    os.makedirs(sample_out_dir, exist_ok=True)
    
    # 1. Cargar el nivel de MÁXIMA resolución (Nivel 0)
    print(" -> Cargando Nivel 0 en RAM (esto puede tomar unos segundos)...")
    with tiff.TiffFile(img_path) as tif:
        # Cargar a memoria. Si tu PC sufre aquí, avísame para usar una técnica de lectura por bloques
        img_full = tif.pages[0].asarray()
        
    if img_full.ndim == 3 and img_full.shape[0] == 3:
        img_full = np.transpose(img_full, (1, 2, 0))
        
    alto, ancho, _ = img_full.shape
    print(f" -> Resolución gigantesca: {ancho}x{alto} píxeles.")
    
    parches_guardados = 0
    parches_totales = 0
    
    # 2. Recorrer la imagen con una cuadrícula (Sliding Window)
    for y in range(0, alto, PATCH_SIZE):
        for x in range(0, ancho, PATCH_SIZE):
            
            # Extraer el parche. Si estamos en el borde y sobra espacio, lo ignoramos para mantener 512x512
            parche_rgb = img_full[y:y+PATCH_SIZE, x:x+PATCH_SIZE]
            
            if parche_rgb.shape[0] != PATCH_SIZE or parche_rgb.shape[1] != PATCH_SIZE:
                continue
                
            parches_totales += 1
            
            # ========================================================
            # QUICK-SKIP: ¿Es puro cristal blanco?
            # Si el promedio de luz es muy cercano a 255, lo saltamos para ahorrar CPU
            # ========================================================
            if np.mean(parche_rgb) > 240:
                continue
                
            # ========================================================
            # FASE 1: FILTRADO FINO EN EL PARCHE
            # ========================================================
            
            # A) Luz (Grises)
            gray = cv2.cvtColor(parche_rgb, cv2.COLOR_RGB2GRAY)
            _, mask_gray = cv2.threshold(gray, 235, 255, cv2.THRESH_BINARY_INV)
            
            # B) Color (Saturación HSV)
            hsv = cv2.cvtColor(parche_rgb, cv2.COLOR_RGB2HSV)
            saturacion = hsv[:, :, 1]
            try:
                # Usamos Otsu. En parches muy pálidos Otsu puede fallar si no hay variación,
                # por eso el try-except por seguridad.
                _, mask_sat = cv2.threshold(saturacion, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            except:
                mask_sat = saturacion > 15 # Umbral manual de respaldo
                
            # Combinación y limpieza (Morfología)
            mask_combinada = cv2.bitwise_and(mask_gray, mask_sat)
            kernel = np.ones((5, 5), np.uint8)
            mask_limpia = cv2.morphologyEx(mask_combinada, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            # ========================================================
            # FASE 2: DECISIÓN DE GUARDADO
            # ========================================================
            
            # ¿Qué porcentaje del recuadro es realmente tejido útil?
            pixeles_tejido = cv2.countNonZero(mask_limpia)
            area_total = PATCH_SIZE * PATCH_SIZE
            ratio_tejido = pixeles_tejido / area_total
            
            # Solo si el parche tiene más del 20% (0.20) de tejido lo guardamos
            if ratio_tejido >= UMBRAL_TEJIDO_MINIMO:
                nombre_archivo = f"patch_{x}_{y}_tejido_{int(ratio_tejido*100)}pct.png"
                ruta_guardado = os.path.join(sample_out_dir, nombre_archivo)
                
                # Para entrenar la red, guardamos el parche en color (RGB), no la máscara.
                # cv2 guarda en BGR, así que lo invertimos para que los colores se vean bien en Windows
                parche_bgr = cv2.cvtColor(parche_rgb, cv2.COLOR_RGB2BGR)
                cv2.imwrite(ruta_guardado, parche_bgr)
                parches_guardados += 1

    # Liberar memoria de la imagen gigante
    del img_full
    print(f" -> ¡Listo! De {parches_totales} parches posibles, se guardaron {parches_guardados} con tejido útil.")

if __name__ == "__main__":
    folders = [f.path for f in os.scandir(DATASET_DIR) if f.is_dir()]
    
    for folder in folders:
        sample_name = os.path.basename(folder)
        all_files = os.listdir(folder)
        
        img_files = [f for f in all_files if f.endswith('.tiff') and '_mask' not in f.lower()]
        
        if img_files:
            img_path = os.path.join(folder, img_files[0])
            procesar_y_extraer_parches(img_path, sample_name)
            
    print("\n¡Extracción de parches finalizada! Revisa la carpeta 'PARCHES_UTILES'.")