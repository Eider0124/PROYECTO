"""Extrae la producción por línea del Excel 'KG producidos 2024, 2025 y 2026'
(hoja 'Data PA 2026', un registro por fecha + línea + turno + SKU) y la guarda en datos/.

Uso:  python3 importar_produccion.py <ruta del Excel>

Genera:
  datos/produccion_detalle.csv   un registro por fecha, línea, turno y SKU
  datos/produccion_diaria.csv    kg por día, línea y turno
Después se corre construir_base.py para cargarla en mediciones y en la base SQLite.
"""
import csv, sys, collections
from pathlib import Path
from openpyxl import load_workbook

BASE = Path(__file__).parent

# Nombre de la línea en el Excel -> nombre de la línea en el informe de energía.
# LINEA 10 = "L10_50 Vanish líquido" y LINEA 18 = "L18_21 Mes pack" en el informe.
ENTIDAD = {"LINEA 22": "L22", "LINEA 14": "L14", "LINEA 16": "L16", "LINEA 10": "L10_50",
           "LINEA 18": "L18_21", "LINEA 20": "L20", "LINEA 19": "L19"}


def num(x):
    return x if isinstance(x, (int, float)) else 0.0


def main(ruta):
    wb = load_workbook(ruta, read_only=True, data_only=True)
    ws = wb["Data PA 2026"]
    filas = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] and r[1] in ENTIDAD]
    datos = BASE / "datos"
    with open(datos / "produccion_detalle.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["fecha", "entidad", "linea_excel", "turno", "sku", "descripcion", "cajas",
                    "embalaje", "unidades", "kg_caja", "kg", "mantenimiento"])
        for f, linea, turno, sku, desc, cajas, _, emb, und, kgc, kg in sorted(filas, key=lambda r: (r[0], r[1], r[2], r[3])):
            w.writerow([f.date().isoformat(), ENTIDAD[linea], linea, turno, sku, (desc or "").strip(), num(cajas),
                        emb if isinstance(emb, (int, float)) else "", num(und),
                        kgc if isinstance(kgc, (int, float)) else "", round(num(kg), 3),
                        "si" if "MANTENIMIENTO" in str(desc).upper() else "no"])
    dia = collections.defaultdict(lambda: {"t1": 0.0, "t2": 0.0, "t3": 0.0, "mant": False})
    for r in filas:
        d = dia[(ENTIDAD[r[1]], r[0].date())]
        d[f"t{min(int(r[2]), 3)}"] += num(r[10])
        d["mant"] |= "MANTENIMIENTO" in str(r[4]).upper()
    with open(datos / "produccion_diaria.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["fecha", "entidad", "kg_turno1", "kg_turno2", "kg_turno3", "kg_total", "mantenimiento"])
        for entidad, f in sorted(dia, key=lambda k: (k[1], k[0])):
            d = dia[(entidad, f)]
            w.writerow([f.isoformat(), entidad, round(d["t1"], 3), round(d["t2"], 3), round(d["t3"], 3),
                        round(d["t1"] + d["t2"] + d["t3"], 3), "si" if d["mant"] else "no"])
    print(f"{len(filas)} registros, {len(dia)} días-línea de producción")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
