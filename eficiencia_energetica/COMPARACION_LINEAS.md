# Comparación de consumo entre líneas

**Fuentes:** informe de consumo energético (Ixon, julio 2026) y Excel de kg producidos (Data PA 2026). Solo electricidad del medidor de cada línea.

La L22 es la línea que más electricidad consume de las que tienen medidor: casi el doble que la siguiente. Frente a la L14, que hace el mismo tipo de producto, gasta lo mismo por tonelada extra producida, pero tiene el **doble de consumo fijo**.

## 1. Consumo reciente (11 de mayo a 6 de junio de 2026, 23 días)

| Línea | kWh en el periodo | kWh/día | t producidas | kWh/t |
| --- | --- | --- | --- | --- |
| **L22 Doypack Megatron** | **2.247** | **97,7** | 319,5 | 7,0 |
| L20 Doypack polvos | 1.266 | 55,0 | 158,7 | 8,0 |
| L14 Doypack 1 | 1.061 | 46,1 | 252,8 | 4,2 |
| L10_50 Vanish líquido | 887 | 38,6 | 359,8 | 2,5 |
| L16 Sachet | 880 | 38,3 | 48,0 | 18,3 |
| L18_21 Mes pack | 796 | 34,6 | 77,2 | 10,3 |

La L22 consumió el 31% de la electricidad medida de estas 6 líneas en ese periodo.

**Equivalencias de nombres.** Las líneas del Excel se asignaron a las del informe así: LINEA 10 → L10_50 y LINEA 18 → L18_21. **Falta confirmarlo.**

**Valores estimados.** La L18_21 tiene la semana del 25 al 30 de mayo leída del eje del gráfico (sin etiquetas).

## 2. L22 frente a L14 (26 de enero a 6 de junio, 86 días con energía y producción)

| Indicador | L22 | L14 |
| --- | --- | --- |
| Consumo medio por día productivo | 94,6 kWh | 54,1 kWh |
| Producción media por día | 14,9 t | 13,5 t |
| kWh/t del periodo | **6,36** | **4,01** |
| Modelo de consumo diario | 74,1 + 1,38 × t | 37,2 + 1,25 × t |
| Consumo fijo por día | **74 kWh** | **37 kWh** |
| Parte fija del consumo | 78% | 69% |
| Día de 2 turnos | 102 kWh · 17,3 t · 5,9 kWh/t | 56 kWh · 14,5 t · 3,9 kWh/t |
| Día de 1 turno | 75 kWh · 8,7 t · 8,7 kWh/t | 41 kWh · 7,4 t · 5,5 kWh/t |
| Sábado sin producción | 26–37 kWh | 7–17 kWh |
| Jueves y Viernes Santo | 0 kWh (apagada) | 2,3 kWh |

### Qué significa

1. **El consumo variable es igual.** Cada tonelada adicional cuesta 1,4 kWh en la L22 y 1,3 en la L14. Producir no es lo caro.
2. **La diferencia está en lo fijo.** La L22 gasta unos 37 kWh/día más que la L14 solo por estar operando, haya mucha o poca producción.
3. **Potencial de referencia.** Si la L22 bajara su consumo fijo al nivel de la L14, ahorraría ≈ 37 kWh × 260 días ≈ **9.600 kWh/año**, cerca de un tercio de su consumo. Es un límite superior: depende de que las máquinas sean comparables.
4. **En espera también consume más.** Los sábados sin producción la L22 consume entre 2 y 4 veces lo de la L14.
5. **Pero se puede apagar.** En Semana Santa la L22 quedó totalmente apagada (0 kWh). El apagado completo es posible.

### Cuidado al comparar

- No sabemos qué envasadora tiene la L14. Si es otra marca o modelo, parte de la diferencia es propia de la máquina.
- Los productos son distintos (L22: 450 y 130 ml; L14: 300 y 800 ml), aunque los dos son doypacks de líquidos.
- El 13–14 de marzo la L14 consumió 70 y 43 kWh sin producción registrada. Hay que revisar si es un error del Excel o consumo real.

## 3. Datos pendientes para cerrar la comparación

- [ ] Marca y modelo de la envasadora de la L14 y su potencia instalada.
- [ ] Qué equipos de la L22 quedan encendidos en espera (resistencias, refrigeración del armario, bandas, dosificador).
- [ ] Confirmar las equivalencias LINEA 10 ↔ L10_50 y LINEA 18 ↔ L18_21.
