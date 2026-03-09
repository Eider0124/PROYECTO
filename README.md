Pipeline de Preprocesamiento para Patología Digital

Descripción General:

Este proyecto contiene un conjunto de scripts diseñados para automatizar el preprocesamiento de Imágenes de Láminas Enteras (WSI - Whole Slide Images) en formato TIFF de altísima resolución. El objetivo principal es limpiar, recortar y extraer únicamente el tejido útil de las muestras médicas, eliminando el fondo de cristal y los artefactos, para preparar los datos antes de entrenar modelos de Deep Learning.

Características Principales:

Máscara Multi-Filtro Inteligente: 

Combina umbralización por luz (escala de grises) y por color (saturación HSV con el método de Otsu) para aislar perfectamente el tejido, ignorando sombras del escáner.

Limpieza Morfológica: 

Usa operaciones matemáticas (Cierre y Apertura) para rellenar huecos internos en el tejido y eliminar ruido (polvo o manchas) en el fondo.

Recorte Automático (Bounding Box): 

Detecta los contornos de la máscara y recorta la imagen gigante a su tamaño mínimo indispensable, ahorrando memoria.

Extracción de Parches (Smart Patching): 

Divide las imágenes en cuadrículas de 512x512 píxeles. Incluye un sistema "Quick-Skip" que ignora parches vacíos al instante para ahorrar CPU, y solo guarda en disco aquellos recuadros que contengan al menos un 20% de tejido real.

Tecnologías Utilizadas:


Python > * OpenCV (cv2): Para visión por computadora, filtros y contornos.


NumPy: Para operaciones matriciales de alto rendimiento.

Tifffile: Para la lectura eficiente de imágenes médicas piramidales.
