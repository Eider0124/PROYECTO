# Línea base eléctrica · Línea 22 (envasadora Mespack de doypack)

**Periodo:** 26 de enero a 6 de junio de 2026 · **Fuentes:** medidor Schneider de la L22 (informe Ixon) y Excel de kg producidos (Data PA 2026) · **Alcance:** solo electricidad del medidor de la línea; el aire comprimido se mide para toda la planta y queda fuera hasta definir cómo repartirlo.

La L22 consume unos **95 kWh por día productivo** y **6,36 kWh por tonelada**. Cerca del 78% de ese consumo es fijo y no depende de cuánto se produce. Por eso la línea pierde eficiencia los días de baja producción o de un solo turno.

## 1. Modelo de la línea base

```latex
\text{kWh/día} = 74{,}1 + 1{,}38 \times \text{toneladas producidas}
```

Se calculó con 86 días que tienen energía y producción (R² = 0,29). El ajuste es bajo: la producción explica poco del consumo, lo que confirma que manda la carga fija. Con este modelo se calcula cada mes el consumo esperado y el ahorro real.

## 2. Consumo según cómo operó la línea

| Tipo de día | Días | kWh/día | t/día | kWh/t |
| --- | --- | --- | --- | --- |
| Producción en 2 turnos | 62 | 102,0 | 17,3 | **5,91** |
| Producción en 1 turno | 24 | 75,4 | 8,7 | **8,66** |
| Mantenimiento sin producción | 2 | 84,1 | 0 | — |
| Sin producción (sábados y un martes) | 4 | 31,0 | 0 | — |

Un día de un turno consume el 74% de un día de dos turnos, pero produce la mitad. Eso indica que la línea queda encendida durante el turno en que no produce, o que tiene una carga fija alta mientras trabaja.

### Intensidad según el volumen del día

| Producción del día | kWh/día | kWh/t |
| --- | --- | --- |
| 2,0–8,4 t (25% de días más bajos) | 74,9 | 12,7 |
| 8,4–12,3 t | 99,2 | 9,1 |
| 12,3–18,1 t | 94,2 | 6,7 |
| 18,1–32,6 t (25% de días más altos) | 109,1 | **3,9** |

Los días de alta producción son 3 veces más eficientes que los de baja.

## 3. Oportunidades preliminares

Estimación anual con 260 días productivos al año (152 de enero a julio). Los supuestos de cada fila se deben validar en planta.

| # | Oportunidad | Supuesto | kWh/año |
| --- | --- | --- | --- |
| O1 | Apagar la línea en el turno sin producción los días de un solo turno | Esos días llegan a 5,91 kWh/t, igual que los de 2 turnos (75 → 51 kWh). ≈ 73 días/año | ≈ 1.750 |
| O2 | Reducir la carga fija en días productivos (bandas, selladora y dosificadora en vacío durante paros) | Bajar un 10% los 74 kWh fijos | ≈ 1.900 |
| O3 | Apagado completo en días sin producción de lunes a sábado | De 31 a ≈ 6 kWh/día en ≈ 53 días/año | ≈ 1.300 |
| O4 | Procedimiento de mantenimiento con equipos apagados | De 84 a 31 kWh/día en 8 días/año | ≈ 400 |
| | **Total preliminar** | O1 y O2 se pueden solapar | **≈ 5.400 (≈ 19%)** |

Sobre un consumo anual estimado de unos 28.500 kWh, la meta inicial sería **reducir cerca del 15–19%** y bajar el indicador de 6,4 a unos **5,2 kWh/t**.

## 4. Qué falta para cerrar la línea base

- [ ] **Consumo de los domingos:** el informe no tiene datos de domingo de la L22. Si la línea queda energizada, O3 crece.
- [ ] **Registro de paros con hora y duración:** para saber cuánto de los 74 kWh fijos ocurre con la línea parada.
- [ ] **Horario real de cada turno** y si en los días de un turno la línea queda encendida en el otro.
- [ ] **Tarifa de energía (COP/kWh)** para valorar el ahorro.
- [ ] **Aire comprimido de la planta (Kaeser)** para asignar la parte de la L22.
- [ ] **Datos de placa de la Mespack** (selladora, dosificadora, motores) para un balance por equipo.
- [ ] **Energía después del 6 de junio** para validar el modelo con datos nuevos.
