# Estudio del informe de consumo energético · Línea 22

**Documento:** "Informe de eficiencia energética Líneas de producción con medidores y acceso al sistema ixon", Wilson Paniquita B., Reckitt Benckiser, planta Cali, julio 2026 (92 págs.).
**Periodo con datos:** 26 de enero al 6 de junio de 2026 (la licencia de Ixon venció a mediados de junio).

## 1. Qué contiene el informe

| Parte | Páginas | Contenido |
| --- | --- | --- |
| Introducción, objetivos, metodología | 2–5 | Barrido de consumo de 7 líneas con medidor Schneider + plataforma Ixon; aire con Kaeser; planta con subestación (4 celdas) y EMCALI |
| Consumo diario por línea | 6–50 | Gráficos semana a semana: L14, L16, L10_50, L18_21, **L22 (págs. 40–48)**, L20 |
| Subestación y EMCALI | 50–57 | Consumo diario de planta (ene S4 a feb S4) y turno de mayor consumo por mes |
| Comparación y distribución | 58–66 | Subestación vs EMCALI, Sankey, equipos por línea |
| Aire comprimido e ICE | 67–87 | Conversión 0,15 kWh/m³; ICE diario por línea (**L22 en págs. 78–86**) |
| Análisis y conclusiones | 88–92 | Análisis de L14, L16, L21, L50 y turnos de febrero (**la L22 no tiene análisis propio**) |

## 2. Línea 22 Megatron (Doypack)

- **Equipos:** 7 bandas transportadoras, mesa giratoria, dosificadora volumétrica, selladora térmica, selladora de cajas, etiquetado wrap-around compartido, cilindros neumáticos y válvulas solenoides.
- **Servicios:** tiene chiller y no tiene aire acondicionado. El consumo del chiller **no** está en el medidor de la línea.
- **Medición:** energía activa diaria (kWh) con medidor Schneider; aire comprimido solo desde marzo (el informe no publica los m³ de la L22).

### Línea base extraída (días válidos)

| Indicador | Valor |
| --- | --- |
| Días con dato válido | 92 |
| Consumo total medido | 8.427 kWh |
| Promedio diario | 91,6 kWh/día |
| Promedio lunes a viernes | 96,1 kWh/día |
| Promedio sábado | 68,7 kWh/día |
| Semana típica (5 × L-V + sábado) | ≈ 549 kWh/semana |
| Anual estimado (solo electricidad) | ≈ 28.500 kWh/año |
| Anual estimado con aire (23,82%) | ≈ 37.500 kWh/año |
| ICE promedio (26 días, mar–abr) | 13,6 kWh/t (baja eficiencia) |
| Días con ICE ≥ 12 | 14 de 26 |
| Turno de mayor consumo (feb) | A, las 4 semanas |
| Participación en la planta | ≈ 2,5% del consumo de la planta |

## 3. Problemas de calidad de datos

| # | Fecha / página | Problema | Cómo quedó en la base |
| --- | --- | --- | --- |
| 1 | 7 feb · pág. 41 | 731,7 kWh, 6,5 veces lo normal | `atipico`, excluido |
| 2 | Feb S4 · págs. 42 y 76 | El informe dice "no hubo producción", pero la línea consumió 107–118 kWh/día de lunes a viernes | **Resuelto:** el Excel de producción muestra 29,7–31,7 t/día ese lunes a viernes. El error está en el informe |
| 3 | Ene S4 · págs. 40 y 69 | La sección de ICE dice "no hubo mediciones", pero sí hay consumo | Incluido |
| 4 | 2–3 abr · pág. 45 | 0 kWh (Jueves y Viernes Santo) | `cero`, excluido de promedios |
| 5 | 23 abr · pág. 46 | 3,6 kWh, corte de datos | `parcial`, excluido |
| 6 | May S1 · pág. 47 | Título sin gráfico: no hay datos | Sin filas |
| 7 | May S4 · pág. 48 | Gráfico sin etiquetas | `estimado` (±1 kWh desde el eje) |
| 8 | 6 feb · pág. 41 | Etiqueta tapada por la línea: 113,937 o 113,987 | 113,937 (diferencia despreciable) |
| 9 | Mar S2 · pág. 80 | ICE sin martes ni miércoles, aunque hubo consumo | Solo 4 días de ICE |
| 10 | Pág. 80 | Títulos "L21" y "L22" repetidos y vacíos | Sin efecto |
| 11 | EMCALI feb S2 · pág. 55 | Repite el gráfico de la semana 1 | Excluido (no hay dato real) |

Festivos sin dato (lunes): 23 de marzo y 18 de mayo.

## 4. Hallazgos útiles para el esquema

1. **Consumo sin producción.** La semana 4 de febrero (≈ 573 kWh de lunes a viernes) es la primera oportunidad: si la línea estuvo encendida sin producir, ese consumo es desperdicio.
2. **Días no productivos de la planta.** El domingo 1 de febrero la planta consumió 943 kWh (subestación) y 1.020 kWh (EMCALI), cerca del 25% de un día hábil. Esto confirma la sospecha del informe.
3. **ICE variable.** Va de 5,7 a 32 kWh/t. Las semanas de baja producción (mar S2) disparan el ICE, señal de consumo fijo alto que no depende de lo producido.
4. **Semanas de un solo turno.** Del 14 al 18 de abril el consumo bajó a unos 50 kWh/día.
5. **Factores del informe:** 1 m³ de aire ≈ 0,15 kWh; el aire es el 23,82% del consumo de las líneas; los medidores cubren el 60–65% del consumo de las líneas y el resto (chiller, A.A., mezclas) no se mide.
6. **Escala de ICE:** 3–6 muy eficiente · 6–12 intermedio · 12–20 baja eficiencia · más de 20 ineficiente.

## 5. Datos que faltan para la línea base

- [x] Producción diaria de la L22 (recibida: Excel KG producidos, ver sección 7).
- [ ] Aire comprimido: **no existe medición por línea**, solo de toda la planta (compresores Kaeser). Hay que asignar a la L22 una parte del aire de la planta (ver sección 7, hallazgo 4).
- [x] Producción de la semana 4 de febrero (sí hubo, ver sección 7).
- [ ] Registro de paros con duración y causa.
- [ ] Energía de la L22 del 24 al 29 de abril, del 4 al 8 de mayo y desde el 7 de junio (hay producción pero no energía).
- [ ] Horario real de turnos de la L22 (A, B, C) y consumo por turno.
- [ ] Datos de la L22 después del 6 de junio (renovar Ixon o exportar desde el medidor).
- [ ] Consumo del chiller asignable a la L22.
- [ ] Tarifa de energía (COP/kWh) para valorar ahorros.

## 7. Producción 2026 (Excel "KG producidos 2024, 2025 y 2026")

**Fuente:** hoja `Data PA 2026`, un registro por fecha, turno y SKU. La hoja "1. Kg real 2026" es una tabla dinámica de la misma hoja; los totales de la L22 coinciden en los 71 días que muestra.

- **Periodo:** 2 de enero al 4 de agosto de 2026, 161 días con registro (154 con kg > 0), 2 turnos.
- **Total producido:** 2.333 t. Turno 1: 1.247 t (53,4%); turno 2: 1.086 t.
- **Productos:** Vanish 450 ml, 300 ml y 130 ml (blanco y rosado) y Saniplex 200 ml.
- **Mantenimiento programado** (SKU 22): 13–14 ene, 10–11 mar, 25–26 may, 27–28 jul.

| Mes | t producidas |
| --- | --- |
| Enero | 362 |
| Febrero | 378 |
| Marzo | 318 |
| Abril | 351 |
| Mayo | 307 |
| Junio | 246 |
| Julio | 335 |
| Agosto (hasta el 4) | 35 |

### Energía frente a producción (86 días con ambos datos)

| Indicador | Valor |
| --- | --- |
| Intensidad eléctrica del periodo | **6,36 kWh/t** (solo electricidad del medidor) |
| Mediana diaria | 7,8 kWh/t (rango 3,4–26,1) |
| Modelo de consumo diario | kWh = **74,1 + 1,38 × t** (R² = 0,29) |
| Producción promedio | 14,9 t/día |

Por mes, con los días que tienen ambos datos: enero 4,3 · febrero 6,0 · marzo 6,5 · abril 7,1 · mayo 7,7 · junio 5,6 kWh/t. La intensidad sube cuando baja la producción.

### Hallazgos

1. **El consumo casi no depende de lo que se produce.** Unos 74 kWh/día son fijos y cada tonelada solo agrega 1,4 kWh. En un día promedio, cerca del 78% del consumo es fijo (74 de 95 kWh). Es la principal oportunidad del esquema.
2. **Mantenimiento con consumo de día productivo.** El 10 y 11 de marzo hubo mantenimiento sin producción y la línea consumió 84 kWh/día, casi lo mismo que produciendo.
3. **Consumo base sin producción.** Los sábados y días sin producción la línea consume entre 25 y 37 kWh (31 ene, 28 feb, 24 mar, 30 may).
4. **El ICE del informe incluye mucho aire.** El ICE del informe es en promedio 1,5 veces el kWh/t eléctrico. Si el informe usó estos mismos kg, el aire comprimido sería cerca del 36% de la energía de la L22 (≈ 51 kWh/día, ≈ 340 m³/día). Es más que el 23,82% general del informe. Como el aire solo se mide para toda la planta, este 36% (y el ICE del informe) depende de cómo el informe repartió el aire entre líneas, y ese método no está explicado. **Para la L22 hay que estimar el aire con un reparto propio** (por producción, por inventario neumático o con una medición temporal en el ramal de la línea).
5. **Confirmado el error del 7 de febrero.** Ese sábado se produjeron 11,6 t, un día normal; los 731,7 kWh son error del medidor.
6. **Producción sin energía medida:** 30 mar, 24–29 abr y 4–8 may (11 días, ≈ 258 t), además de todo lo posterior al 6 de junio.

### Calidad del Excel de producción

- Los SKU 3331339 y 3331340 (Saniplex 200 ml) tienen embalaje 6 y 12,851 kg/caja. Seis unidades de 200 ml pesan cerca de 1,3 kg, así que el embalaje o el peso por caja está mal. Los kg pueden estar bien si el peso por caja es el correcto (otros 200 ml x64 pesan 14,158 kg/caja). Afecta 24 registros.
- Las filas de mantenimiento tienen `#N/A` en embalaje y kg/caja (sin efecto: 0 kg).
- 18 registros de la L22 tienen 0 kg (mantenimiento o arranques sin cajas).

## 8. Archivos de la base

| Archivo | Contenido |
| --- | --- |
| `datos/mediciones.csv` | Tabla larga: fecha, entidad, variable, valor, calidad, incluir, página. 3.386 filas: energía de L22 y L14 completas y de L16, L10_50, L18_21 y L20 del 11 may al 6 jun; ICE de L22 y L14; producción de 7 líneas; planta |
| `datos/produccion_detalle.csv` | Producción por fecha, línea, turno y SKU (1.826 registros) |
| `datos/produccion_diaria.csv` | kg por día, línea y turno |
| `importar_produccion.py` | Extrae la producción de cada línea del Excel de kg producidos |
| `COMPARACION_LINEAS.md` | Consumo reciente de todas las líneas y comparación L22 vs L14 |
| `datos/parametros.csv` | Factores y escalas del informe |
| `datos/equipos.csv` | Equipos de la L22 |
| `datos/turnos.csv` | Turno de mayor consumo (L22 y planta) |
| `eficiencia.db` | Las mismas tablas en SQLite |
| `construir_base.py` | Regenera todo; los datos nuevos se agregan aquí |
| `Linea22_consumo_energetico.xlsx` | Vista en Excel con resúmenes y fórmulas |

Los datos nuevos se agregan como filas de `mediciones` con la misma estructura: `entidad` = línea o planta, `variable` = qué se mide, `fuente` = de dónde viene.
