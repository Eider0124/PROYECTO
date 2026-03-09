import os
import cv2
import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt

# ================= Configuración =================
DATASET_DIR = './DATASET'

def procesar_y_recortar(img_path, sample_name):
    print(f"\nProcesando {sample_name}...")
    
    # 1. Cargar el nivel de baja resolución (Pirámide)
    with tiff.TiffFile(img_path) as tif:
        nivel_elegido = len(tif.pages) - 1 
        image_rgb = tif.pages[nivel_elegido].asarray()
        
    if image_rgb.ndim == 3 and image_rgb.shape[0] == 3:
        image_rgb = np.transpose(image_rgb, (1, 2, 0))
        
    # ========================================================
    # FASE 1: CREACIÓN DE LA MÁSCARA MULTI-FILTRO
    # ========================================================
    
    # Filtro A: Escala de Grises (Luz)
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    _, mask_gray = cv2.threshold(gray, 235, 255, cv2.THRESH_BINARY_INV)
    
    # Filtro B: Espacio HSV (Color / Saturación)
    hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
    saturacion = hsv[:, :, 1]
    # Usamos Otsu sobre el canal de saturación. ¡Es súper efectivo!
    _, mask_sat = cv2.threshold(saturacion, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Combinar Filtro A y B (Debe ser oscuro Y tener color)
    mask_combinada = cv2.bitwise_and(mask_gray, mask_sat)
    
    # Filtro C: Operaciones Morfológicas (Limpieza de Forma)
    kernel = np.ones((5, 5), np.uint8)
    # 1. 'Closing' (Cierre): Rellena agujeros negros dentro del tejido blanco
    mask_limpia = cv2.morphologyEx(mask_combinada, cv2.MORPH_CLOSE, kernel, iterations=2)
    # 2. 'Opening' (Apertura): Borra puntitos blancos de ruido en el fondo negro
    mask_limpia = cv2.morphologyEx(mask_limpia, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # ========================================================
    # FASE 2: BÚSQUEDA DE CONTORNOS Y RECORTE
    # ========================================================
    
    # Encontrar las "islas" de tejido en la máscara
    contornos, _ = cv2.findContours(mask_limpia, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contornos:
        print(" -> Error: No se detectó tejido en esta imagen.")
        return
        
    # Buscar los límites globales (Caja delimitadora extrema) para no cortar ningún pedazo
    x_min, y_min = image_rgb.shape[1], image_rgb.shape[0]
    x_max, y_max = 0, 0
    
    for cnt in contornos:
        area = cv2.contourArea(cnt)
        if area > 500: # Ignorar contornos ridículamente pequeños (basura)
            x, y, w, h = cv2.boundingRect(cnt)
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            x_max = max(x_max, x + w)
            y_max = max(y_max, y + h)
            
    # Dibujar un rectángulo verde en una copia para visualizar
    img_bbox = image_rgb.copy()
    cv2.rectangle(img_bbox, (x_min, y_min), (x_max, y_max), (0, 255, 0), 3)
    
    # ¡EL RECORTE FINAL! (Cropping usando arrays de Numpy)
    imagen_recortada = image_rgb[y_min:y_max, x_min:x_max]
    
    # ========================================================
    # FASE 3: VISUALIZACIÓN INTERACTIVA
    # ========================================================
    
    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    fig.canvas.manager.set_window_title(f"Recorte Avanzado: {sample_name}")
    
    axes[0].imshow(image_rgb)
    axes[0].set_title(f"Original\n({image_rgb.shape[1]}x{image_rgb.shape[0]})")
    axes[0].axis('off')
    
    axes[1].imshow(mask_limpia, cmap='gray')
    axes[1].set_title("Máscara Refinada\n(Luz + HSV + Morfología)")
    axes[1].axis('off')
    
    axes[2].imshow(img_bbox)
    axes[2].set_title("Contorno y Bounding Box")
    axes[2].axis('off')
    
    axes[3].imshow(imagen_recortada)
    axes[3].set_title(f"Tejido Recortado\n({imagen_recortada.shape[1]}x{imagen_recortada.shape[0]})")
    axes[3].axis('off')
    
    plt.tight_layout()
    print(" -> Mostrando resultado. Cierra la ventana para ver el siguiente.")
    plt.show()

if __name__ == "__main__":
    folders = [f.path for f in os.scandir(DATASET_DIR) if f.is_dir()]
    
    for folder in folders:
        sample_name = os.path.basename(folder)
        all_files = os.listdir(folder)
        
        img_files = [f for f in all_files if f.endswith('.tiff') and '_mask' not in f.lower()]
        
        if img_files:
            img_path = os.path.join(folder, img_files[0])
            procesar_y_recortar(img_path, sample_name)
            
    print("\n¡Prueba de recortes finalizada!")