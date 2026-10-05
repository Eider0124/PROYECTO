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
| 2 | Feb S4 · págs. 42 y 76 | El informe dice "no hubo producción", pero la línea consumió 107–118 kWh/día de lunes a viernes | Incluido; **verificar con producción** |
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

- [ ] Producción diaria de la L22 (toneladas y unidades) para recalcular el ICE en todo el periodo.
- [ ] Consumo de aire comprimido de la L22 en m³/día desde marzo.
- [ ] Registro de paros y producción de la semana 4 de febrero.
- [ ] Horario real de turnos de la L22 (A, B, C) y consumo por turno.
- [ ] Datos de la L22 después del 6 de junio (renovar Ixon o exportar desde el medidor).
- [ ] Consumo del chiller asignable a la L22.
- [ ] Tarifa de energía (COP/kWh) para valorar ahorros.

## 6. Archivos de la base

| Archivo | Contenido |
| --- | --- |
| `datos/mediciones.csv` | Tabla larga: fecha, entidad, variable, valor, calidad, incluir, página. 178 filas |
| `datos/parametros.csv` | Factores y escalas del informe |
| `datos/equipos.csv` | Equipos de la L22 |
| `datos/turnos.csv` | Turno de mayor consumo (L22 y planta) |
| `eficiencia.db` | Las mismas tablas en SQLite |
| `construir_base.py` | Regenera todo; los datos nuevos se agregan aquí |
| `Linea22_consumo_energetico.xlsx` | Vista en Excel con resúmenes y fórmulas |

Los datos nuevos se agregan como filas de `mediciones` con la misma estructura: `entidad` = línea o planta, `variable` = qué se mide, `fuente` = de dónde viene.
