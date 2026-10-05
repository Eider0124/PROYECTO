"""Construye la base de datos del proyecto de eficiencia energética a partir de los
datos extraídos del informe 'Informe de eficiencia energética Líneas de producción con
medidores y acceso al sistema ixon' (W. Paniquita, julio 2026).

Genera:
  datos/mediciones.csv   tabla larga: una fila por fecha + entidad + variable
  datos/parametros.csv   factores y escalas que define el informe
  datos/equipos.csv      equipos de la línea 22
  datos/turnos.csv       turno de mayor consumo según el informe
  eficiencia.db          los mismos datos en SQLite
"""
import csv, sqlite3, datetime as dt
from pathlib import Path

BASE = Path(__file__).parent
FUENTE = "Informe Paniquita jul-2026"
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

# (fecha, kWh, calidad, página) · calidad: leido | estimado | atipico | cero | parcial
L22_KWH = [
 ("2026-01-26",72.090,"leido",40),("2026-01-27",106.380,"leido",40),("2026-01-28",108.457,"leido",40),
 ("2026-01-29",105.679,"leido",40),("2026-01-30",74.386,"leido",40),("2026-01-31",27.264,"leido",40),
 ("2026-02-02",111.162,"leido",41),("2026-02-03",115.302,"leido",41),("2026-02-04",101.299,"leido",41),
 ("2026-02-05",113.098,"leido",41),("2026-02-06",113.937,"leido",41),("2026-02-07",731.716,"atipico",41),
 ("2026-02-09",75.192,"leido",41),("2026-02-10",82.366,"leido",41),("2026-02-11",84.545,"leido",41),
 ("2026-02-12",77.089,"leido",41),("2026-02-13",72.666,"leido",41),("2026-02-14",49.787,"leido",41),
 ("2026-02-16",102.391,"leido",42),("2026-02-17",117.130,"leido",42),("2026-02-18",119.866,"leido",42),
 ("2026-02-19",81.335,"leido",42),("2026-02-20",109.950,"leido",42),("2026-02-21",89.113,"leido",42),
 ("2026-02-23",106.517,"leido",42),("2026-02-24",116.289,"leido",42),("2026-02-25",114.605,"leido",42),
 ("2026-02-26",117.962,"leido",42),("2026-02-27",117.937,"leido",42),("2026-02-28",36.967,"leido",42),
 ("2026-03-02",111.572,"leido",43),("2026-03-03",112.742,"leido",43),("2026-03-04",107.625,"leido",43),
 ("2026-03-05",113.568,"leido",43),("2026-03-06",115.156,"leido",43),("2026-03-07",89.650,"leido",43),
 ("2026-03-09",74.099,"leido",43),("2026-03-10",83.903,"leido",43),("2026-03-11",84.373,"leido",43),
 ("2026-03-12",76.234,"leido",43),("2026-03-13",72.307,"leido",43),("2026-03-14",51.167,"leido",43),
 ("2026-03-16",124.240,"leido",44),("2026-03-17",119.295,"leido",44),("2026-03-18",121.465,"leido",44),
 ("2026-03-19",95.924,"leido",44),("2026-03-20",85.605,"leido",44),("2026-03-21",100.815,"leido",44),
 ("2026-03-24",34.292,"leido",44),("2026-03-25",73.402,"leido",44),("2026-03-26",82.859,"leido",44),
 ("2026-03-27",86.964,"leido",44),("2026-03-28",74.708,"leido",44),
 ("2026-04-01",112.608,"leido",45),("2026-04-02",0.0,"cero",45),("2026-04-03",0.0,"cero",45),("2026-04-04",102.321,"leido",45),
 ("2026-04-06",69.107,"leido",45),("2026-04-07",78.193,"leido",45),("2026-04-08",88.541,"leido",45),
 ("2026-04-09",85.529,"leido",45),("2026-04-10",73.750,"leido",45),("2026-04-11",73.471,"leido",45),
 ("2026-04-13",107.514,"leido",46),("2026-04-14",50.840,"leido",46),("2026-04-15",52.928,"leido",46),
 ("2026-04-16",49.888,"leido",46),("2026-04-17",51.702,"leido",46),("2026-04-18",26.608,"leido",46),
 ("2026-04-20",97.386,"leido",46),("2026-04-21",114.672,"leido",46),("2026-04-22",131.706,"leido",46),("2026-04-23",3.604,"parcial",46),
 ("2026-05-11",92.739,"leido",47),("2026-05-12",110.993,"leido",47),("2026-05-13",109.833,"leido",47),
 ("2026-05-14",108.216,"leido",47),("2026-05-15",121.350,"leido",47),("2026-05-16",102.928,"leido",47),
 ("2026-05-19",106.546,"leido",47),("2026-05-20",117.963,"leido",47),("2026-05-21",118.206,"leido",47),
 ("2026-05-22",117.576,"leido",47),("2026-05-23",90.333,"leido",47),
 ("2026-05-25",61.6,"estimado",48),("2026-05-26",72.8,"estimado",48),("2026-05-27",73.5,"estimado",48),
 ("2026-05-28",112.5,"estimado",48),("2026-05-29",115.5,"estimado",48),("2026-05-30",25.6,"estimado",48),
 ("2026-06-01",76.907,"leido",48),("2026-06-02",106.000,"leido",48),("2026-06-03",115.267,"leido",48),
 ("2026-06-04",96.462,"leido",48),("2026-06-05",105.275,"leido",48),("2026-06-06",89.349,"leido",48),
]
NOTAS = {
 "atipico": "6,5 veces lo normal; probable error del medidor o acumulado. Excluir del análisis.",
 "cero": "Jueves/Viernes Santo (festivo). Excluir de promedios.",
 "parcial": "Último registro antes del corte de datos; día incompleto. Excluir.",
 "estimado": "Gráfico sin etiquetas; valor leído del eje (±1 kWh).",
}
# ICE L22 (kWh/t, electricidad + aire comprimido)
L22_ICE = [
 ("2026-03-02",5.701,78),("2026-03-03",6.165,78),("2026-03-04",9.0,78),("2026-03-05",11.109,78),("2026-03-06",11.975,78),("2026-03-07",10.754,78),
 ("2026-03-09",12.023,80),("2026-03-12",28.89,80),("2026-03-13",18.94,80),("2026-03-14",31.95,80),
 ("2026-03-16",16.45,82),("2026-03-17",16.01,82),("2026-03-18",19.25,82),("2026-03-19",20.57,82),("2026-03-20",7.42,82),("2026-03-21",7.31,82),
 ("2026-03-25",8.421,84),("2026-03-26",9.954,84),("2026-03-27",8.954,84),("2026-03-28",5.919,84),
 ("2026-04-06",13.461,86),("2026-04-07",14.346,86),("2026-04-08",15.636,86),("2026-04-09",13.831,86),("2026-04-10",13.971,86),("2026-04-11",15.435,86),
]
# Planta: subestación (Ixon) y EMCALI, kWh/día
SUBESTACION = [
 ("2026-01-26",4741.330,51),("2026-01-27",4343.821,51),("2026-01-28",4171.754,51),("2026-01-29",3834.308,51),("2026-01-30",3862.029,51),("2026-01-31",2187.444,51),
 ("2026-02-01",943.020,52),("2026-02-02",3508.036,52),("2026-02-03",3813.630,52),("2026-02-04",3637.258,52),("2026-02-05",3882.713,52),("2026-02-06",3812.319,52),("2026-02-07",2427.664,52),
 ("2026-02-09",4162.378,52),("2026-02-10",4394.471,52),("2026-02-11",4344.395,52),("2026-02-12",4681.198,52),("2026-02-13",4566.881,52),("2026-02-14",1950.314,52),
 ("2026-02-16",3180,53),("2026-02-17",3563,53),("2026-02-18",3333,53),("2026-02-19",2255,53),("2026-02-20",2938,53),("2026-02-21",3212,53),
 ("2026-02-23",3863,53),("2026-02-24",4150,53),("2026-02-25",3857,53),("2026-02-26",3827,53),("2026-02-27",3811,53),("2026-02-28",2207,53),
]
EMCALI = [
 ("2026-01-26",4789.8,54),("2026-01-27",4469.76,54),("2026-01-28",4299.12,54),("2026-01-29",3933.24,54),("2026-01-30",4059.72,54),("2026-01-31",2299.8,54),
 ("2026-02-01",1020.48,54),("2026-02-02",3622.08,54),("2026-02-03",3887.4,54),("2026-02-04",3716.88,54),("2026-02-05",3974.88,54),("2026-02-06",3904.44,54),("2026-02-07",2522.4,54),
 ("2026-02-16",3265.08,55),("2026-02-17",3674.76,55),("2026-02-18",3459.72,55),("2026-02-19",2369.76,55),("2026-02-20",3010.08,55),("2026-02-21",3323.4,55),
 ("2026-02-23",3976.68,56),("2026-02-24",4271.88,56),("2026-02-25",3956.28,56),("2026-02-26",3948.84,56),("2026-02-27",3918,56),("2026-02-28",2325.48,56),
]

def semana(d):
    return f"{d.isocalendar()[0]}-S{d.isocalendar()[1]:02d}"

def main():
    filas = []
    def add(fecha, entidad, variable, unidad, valor, calidad, pagina, nota=""):
        d = dt.date.fromisoformat(fecha)
        incluir = "no" if calidad in ("atipico", "cero", "parcial") else "si"
        filas.append(dict(fecha=fecha, dia=DIAS[d.weekday()], semana_iso=semana(d), mes=d.month,
                          entidad=entidad, variable=variable, unidad=unidad, valor=valor,
                          calidad=calidad, incluir=incluir, fuente=FUENTE, pagina=pagina, nota=nota))
    for f, v, c, p in L22_KWH:
        add(f, "L22", "energia_activa", "kWh/dia", v, c, p, NOTAS.get(c, ""))
    for f, v, p in L22_ICE:
        add(f, "L22", "ice", "kWh/t", v, "leido", p)
    for f, v, p in SUBESTACION:
        add(f, "PLANTA", "energia_activa_subestacion", "kWh/dia", v, "leido", p,
            "Domingo, día no productivo." if f == "2026-02-01" else "")
    for f, v, p in EMCALI:
        add(f, "PLANTA", "energia_activa_emcali", "kWh/dia", v, "leido", p,
            "Domingo, día no productivo." if f == "2026-02-01" else "")
    datos = BASE / "datos"; datos.mkdir(exist_ok=True)
    campos = list(filas[0].keys())
    with open(datos / "mediciones.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos); w.writeheader(); w.writerows(filas)

    parametros = [
        ("conversion_aire", 0.15, "kWh/m3", "Promedio de 0,12-0,18 kWh por m3 de aire comprimido (pág. 67)"),
        ("participacion_aire", 0.2382, "fraccion", "Aire comprimido = 23,82% del consumo de las líneas medidas (pág. 67)"),
        ("ice_muy_eficiente_max", 6, "kWh/t", "ICE 3-6 = muy eficiente (pág. 68)"),
        ("ice_intermedio_max", 12, "kWh/t", "ICE 6-12 = intermedio"),
        ("ice_baja_max", 20, "kWh/t", "ICE 12-20 = baja eficiencia; >20 ineficiente"),
        ("planta_semana_ixon", 21700, "kWh/semana", "Promedio 4 semanas, subestación Ixon (pág. 58)"),
        ("planta_semana_emcali", 22600, "kWh/semana", "Promedio 4 semanas, EMCALI (pág. 58)"),
        ("lineas_medidas_participacion", "0,60-0,65", "fraccion", "Medidores + aire = 60-65% del consumo de las líneas (pág. 60)"),
        ("chiller_aa_mezclas_participacion", "0,35-0,40", "fraccion", "Chillers, A.A. y mezclas no medidos (pág. 60)"),
    ]
    with open(datos / "parametros.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["parametro", "valor", "unidad", "nota"]); w.writerows(parametros)

    equipos = [
        ("L22", "Bandas transportadoras", 7, "electrico", "Motores eléctricos"),
        ("L22", "Mesa giratoria", 1, "ambos", "Motor + neumática"),
        ("L22", "Dosificadora volumétrica", None, "ambos", "Motores, variadores y actuadores"),
        ("L22", "Selladora térmica", 1, "electrico", "Resistencias"),
        ("L22", "Selladora de cajas", 1, "ambos", ""),
        ("L22", "Etiquetado wrap-around", 1, "ambos", "Compartido con otras líneas"),
        ("L22", "Cilindros neumáticos", None, "aire", ""),
        ("L22", "Válvulas solenoides", None, "electrico", ""),
    ]
    with open(datos / "equipos.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["linea", "equipo", "cantidad", "energetico", "nota"]); w.writerows(equipos)

    turnos = [("L22", "2026-02", f"S{i}", "A", "pág. 89") for i in range(1, 5)] + [("L22", "2026-02", "mes", "A", "pág. 89")]
    turnos += [("PLANTA", m, "mes", t, "págs. 56-57") for m, t in
               [("2026-02", "B"), ("2026-03", "A"), ("2026-04", "A"), ("2026-05", "B"), ("2026-06", "B")]]
    with open(datos / "turnos.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["entidad", "mes", "periodo", "turno_mayor_consumo", "pagina"]); w.writerows(turnos)

    db = BASE / "eficiencia.db"
    if db.exists(): db.unlink()
    con = sqlite3.connect(db)
    for nombre in ["mediciones", "parametros", "equipos", "turnos"]:
        with open(datos / f"{nombre}.csv", encoding="utf-8") as fh:
            r = list(csv.reader(fh))
        con.execute(f"CREATE TABLE {nombre} ({', '.join(c + ' TEXT' if c not in ('valor','pagina','mes','cantidad') else c + ' REAL' for c in r[0])})")
        con.executemany(f"INSERT INTO {nombre} VALUES ({','.join('?'*len(r[0]))})", [[x if x != "" else None for x in row] for row in r[1:]])
    con.commit(); con.close()
    print(f"{len(filas)} mediciones guardadas")

if __name__ == "__main__":
    main()
