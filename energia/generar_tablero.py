"""Genera Tablero_Energia.xlsx a partir de lecturas.csv y medidores.csv.

Uso: python3 generar_tablero.py
Cada día se agregan las lecturas nuevas a lecturas.csv y se vuelve a ejecutar.
El Excel resultante funciona sin internet: todo se calcula con fórmulas.
"""
import csv
from datetime import date, datetime, time, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

BASE = Path(__file__).parent
SALIDA = BASE / "Tablero_Energia.xlsx"

VERDE = "2F7A34"
VERDE_SUAVE = "E2EFE0"
AMBAR_SUAVE = "FBEFD5"
ROJO_SUAVE = "F8E0DD"
GRIS = "7B877D"
LINEA = "DDE3DC"

F = "Arial"
f_base = Font(name=F, size=10)
f_titulo = Font(name=F, size=18, bold=True, color="18201A")
f_sub = Font(name=F, size=10, color=GRIS)
f_head = Font(name=F, size=10, bold=True, color="FFFFFF")
f_label = Font(name=F, size=9, bold=True, color=GRIS)
f_kpi = Font(name=F, size=18, bold=True, color="18201A")
f_input = Font(name=F, size=12, bold=True, color="0000FF")
fill_head = PatternFill("solid", fgColor=VERDE)
fill_input = PatternFill("solid", fgColor="FFFF00")
fill_kpi = PatternFill("solid", fgColor="F3F5F2")
thin = Side(style="thin", color=LINEA)
borde = Border(left=thin, right=thin, top=thin, bottom=thin)
centro = Alignment(horizontal="center", vertical="center", wrap_text=True)

NUM3 = "#,##0.000"
NUM1 = "#,##0.0"


def ip_key(ip):
    return tuple(int(p) for p in ip.split("."))


def leer_datos():
    with open(BASE / "medidores.csv", newline="", encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))
    medidores = [(r["ip"], r["nombre"]) for r in filas]
    # Varios medidores tienen el reloj en UTC; desfase_h lo lleva a hora de Colombia
    desfase = {r["ip"]: int(r.get("desfase_h") or 0) for r in filas}
    lecturas = []
    with open(BASE / "lecturas.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            num = lambda v: float(v) if v.strip() else None
            en_medidor = datetime.fromisoformat(f"{r['fecha']} {r['hora']}")
            local = en_medidor + timedelta(hours=desfase.get(r["ip"], 0))
            lecturas.append((local.date(), r["ip"], local.time(),
                             num(r["kwh"]), num(r["kvarh"]), num(r["kvah"]),
                             en_medidor.strftime("%Y-%m-%d %H:%M")))
    # El cálculo de kW por intervalo compara cada fila con la anterior,
    # así que los datos deben ir ordenados por fecha, medidor y hora.
    lecturas.sort(key=lambda r: (r[0], ip_key(r[1]), r[2]))
    conocidas = {ip for ip, _ in medidores}
    for ip in sorted({r[1] for r in lecturas} - conocidas, key=ip_key):
        medidores.append((ip, ip))
    return medidores, lecturas


def encabezado(ws, fila, columnas, col0=1):
    for i, txt in enumerate(columnas):
        c = ws.cell(fila, col0 + i, txt)
        c.font, c.fill, c.alignment, c.border = f_head, fill_head, centro, borde


def hoja_datos(wb, lecturas):
    ws = wb.create_sheet("Datos")
    cols = ["Fecha", "IP", "Hora", "kWh", "kVARh", "kVAh", "Minuto", "kW intervalo", "Línea", "Hora en el medidor"]
    encabezado(ws, 1, cols)
    for i, (d, ip, t, kwh, kvarh, kvah, crudo) in enumerate(lecturas, start=2):
        ws.cell(i, 1, d).number_format = "yyyy-mm-dd"
        ws.cell(i, 2, ip)
        ws.cell(i, 3, t).number_format = "hh:mm"
        for col, v in ((4, kwh), (5, kvarh), (6, kvah)):
            c = ws.cell(i, col, v)
            c.number_format = NUM3
        ws.cell(i, 7, f"=HOUR(C{i})*60+MINUTE(C{i})")
        ws.cell(i, 8, f'=IF(AND(B{i}=B{i-1},A{i}=A{i-1},D{i}>0,N(D{i-1})>0,G{i}>N(G{i-1})),'
                      f'(D{i}-D{i-1})/((G{i}-G{i-1})/60),"")').number_format = "#,##0.00"
        ws.cell(i, 9, f'=IFERROR(INDEX(Medidores!$B:$B,MATCH(B{i},Medidores!$A:$A,0)),"")')
        ws.cell(i, 10, crudo)
        for col in range(1, 11):
            ws.cell(i, col).font = f_base
    last = max(len(lecturas) + 1, 2)
    tabla = Table(displayName="tDatos", ref=f"A1:J{last}")
    tabla.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws.add_table(tabla)
    for col, w in zip("ABCDEFGHIJ", [12, 15, 8, 14, 14, 14, 9, 13, 18, 19]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"
    return ws


def leer_padres():
    """IP del medidor que contiene a cada uno (vacío si está directo en la frontera)."""
    with open(BASE / "medidores.csv", newline="", encoding="utf-8") as fh:
        return {r["ip"]: (r.get("dentro_de") or "").strip() for r in csv.DictReader(fh)}


def leer_desfases():
    with open(BASE / "medidores.csv", newline="", encoding="utf-8") as fh:
        return {r["ip"]: int(r.get("desfase_h") or 0) for r in csv.DictReader(fh)}


def hoja_medidores(wb, medidores):
    ws = wb.create_sheet("Medidores")
    padres, desfases = leer_padres(), leer_desfases()
    encabezado(ws, 1, ["IP", "Nombre de la línea", "Dentro de (IP)", "Reloj del medidor"])
    for i, (ip, nombre) in enumerate(medidores, start=2):
        ws.cell(i, 1, ip).font = f_base
        c = ws.cell(i, 2, nombre)
        c.font = Font(name=F, size=10, color="0000FF")
        c = ws.cell(i, 3, padres.get(ip) or None)
        c.font = Font(name=F, size=10, color="0000FF")
        ws.cell(i, 4, "UTC (−5 h)" if desfases.get(ip) else "Hora Colombia").font = f_base
        for col in (1, 2, 3, 4):
            ws.cell(i, col).border = borde
    for col, w in zip("ABCD", [16, 24, 16, 18]):
        ws.column_dimensions[col].width = w
    ws["F1"] = "Puedes cambiar los nombres de la columna B; el tablero se actualiza solo."
    ws["F2"] = "Dentro de: medidor que ya incluye este consumo. No se suma dos veces en los totales, salvo que ese medidor no tenga dato."
    for ref in ("F1", "F2"):
        ws[ref].font = f_sub
    return ws


def crit(ip_ref, dia_ref):
    return f"Datos!$B:$B,{ip_ref},Datos!$A:$A,{dia_ref}"


def hoja_tablero(wb, medidores, dias, medidor_inicial):
    ws = wb.active
    ws.title = "Tablero"
    ws.sheet_view.showGridLines = False
    anchos = [2, 20, 14, 16, 8, 8, 9, 12, 12, 12, 10, 8, 10, 10, 9, 12, 11, 15]
    for i, w in enumerate(anchos, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws["B1"] = "Monitoreo de Energía"
    ws["B1"].font = f_titulo
    ws["B2"] = "Data Log de medidores de planta · horas en hora de Colombia (los medidores en UTC se corrigen −5 h)"
    ws["B2"].font = f_sub

    ws["B4"] = "DÍA"
    ws["D4"] = "HORA DE CORTE 24 h"
    ws["F4"] = "MEDIDOR PARA LA GRÁFICA DE 15 MIN"
    for ref in ("B4", "D4", "F4"):
        ws[ref].font = f_label
    ws["B5"] = dias[-1] if dias else None
    ws["B5"].number_format = "yyyy-mm-dd"
    ws["D5"] = time(11, 0)
    ws["D5"].number_format = "hh:mm"
    ws.merge_cells("F5:H5")
    ws["F5"] = medidor_inicial
    for ref in ("B5", "D5", "F5"):
        ws[ref].font, ws[ref].fill, ws[ref].border = f_input, fill_input, borde
        ws[ref].alignment = Alignment(horizontal="center")
    ws["I5"] = '=IFERROR(INDEX(Medidores!$A:$A,MATCH($F$5,Medidores!$B:$B,0)),"")'
    ws["I5"].font = f_sub

    dv_dia = DataValidation(type="list", formula1=f"=Histórico!$A$3:$A${2 + max(len(dias), 1)}", allow_blank=False,
                            error="Elige un día de la lista.", errorTitle="Día no válido")
    dv_med = DataValidation(type="list", formula1="=Medidores!$B$2:$B$200", allow_blank=False,
                            error="Elige un medidor de la lista.", errorTitle="Medidor no válido")
    dv_hora = DataValidation(type="time", operator="between", formula1="0", formula2="0.999",
                             error="Escribe una hora, por ejemplo 14:45.", errorTitle="Hora no válida")
    for dv, ref in ((dv_dia, "B5"), (dv_med, "F5"), (dv_hora, "D5")):
        ws.add_data_validation(dv)
        dv.add(ref)

    n = len(medidores)
    r0, r1 = 12, 12 + n - 1
    kpis = [
        ("B", "CONSUMO DEL PERIODO (kWh)", f"=SUMPRODUCT(W{r0}:W{r1},H{r0}:H{r1})", NUM1),
        ("D", "DEMANDA MEDIA TOTAL (kW)", f"=SUMPRODUCT(W{r0}:W{r1},K{r0}:K{r1})", NUM1),
        ("G", "CONSUMO 24 h AL CORTE (kWh)", f'=IF(COUNT(P{r0}:P{r1})=0,"Falta el día anterior",SUMPRODUCT(X{r0}:X{r1},P{r0}:P{r1}))', NUM1),
        ("J", "FACTOR DE POTENCIA", f'=IFERROR(SUMPRODUCT(W{r0}:W{r1}*ISNUMBER(L{r0}:L{r1}),H{r0}:H{r1})/SUMPRODUCT(W{r0}:W{r1}*ISNUMBER(L{r0}:L{r1}),J{r0}:J{r1}),"")', "0.000"),
        ("M", "MEDIDORES CON AVISO", f'=COUNTIF(D{r0}:D{r1},"<>Normal")&" de "&COUNTA(C{r0}:C{r1})', "@"),
    ]
    for col, label, formula, fmt in kpis:
        ws[f"{col}7"] = label
        ws[f"{col}7"].font = f_label
        c = ws[f"{col}8"]
        c.value, c.font, c.number_format, c.fill = formula, f_kpi, fmt, fill_kpi
        c.alignment = Alignment(horizontal="left")

    cols = ["Línea", "IP", "Estado", "Desde", "Hasta", "Lecturas", "kWh", "kVARh", "kVAh",
            "kW medio", "FP", "kVARh / kWh", "kW máx 15 min", "Hora kW máx", "kWh 24 h al corte",
            "kW medio vs día anterior", "Última lectura kWh", "válidas", "en cero", "con kVAh", "kW medio día ant.", "suma periodo", "suma 24 h"]
    encabezado(ws, 11, cols, col0=2)
    ws.row_dimensions[11].height = 30
    corte = "(HOUR($D$5)*60+MINUTE($D$5))"
    for i in range(n):
        r = r0 + i
        cr = crit(f"$C{r}", "$B$5")
        valid = f'{cr},Datos!$D:$D,">0"'
        ant = crit(f"$C{r}", "$B$5-1")
        valid_ant = f'{ant},Datos!$D:$D,">0"'
        f = {
            "B": f"=Medidores!B{i + 2}",
            "C": f"=Medidores!A{i + 2}",
            "D": (f'=IF(S{r}<2,"Sin datos",IF(T{r}>0,"Lectura en cero",IF(U{r}<2,"Falta kVAh",'
                  f'IF(H{r}<=0.001,"Sin consumo",IF(AND(ISNUMBER(M{r}),M{r}>0.5),"Reactiva > 50 %","Normal")))))'),
            "E": f'=IF(S{r}<2,"",_xlfn.MINIFS(Datos!$G:$G,{valid})/1440)',
            "F": f'=IF(S{r}<2,"",_xlfn.MAXIFS(Datos!$G:$G,{valid})/1440)',
            "G": f"=COUNTIFS({cr})",
            "H": f'=IF(S{r}<2,"",_xlfn.MAXIFS(Datos!$D:$D,{valid})-_xlfn.MINIFS(Datos!$D:$D,{valid}))',
            "I": f'=IF(S{r}<2,"",_xlfn.MAXIFS(Datos!$E:$E,{valid})-_xlfn.MINIFS(Datos!$E:$E,{valid}))',
            "J": f'=IF(U{r}<2,"",_xlfn.MAXIFS(Datos!$F:$F,{cr},Datos!$F:$F,">0")-_xlfn.MINIFS(Datos!$F:$F,{cr},Datos!$F:$F,">0"))',
            "K": f'=IF(H{r}="","",IF(F{r}>E{r},H{r}/((F{r}-E{r})*24),""))',
            "L": f'=IF(OR(H{r}="",J{r}=""),"",IF(J{r}>0,H{r}/J{r},""))',
            "M": f'=IF(OR(H{r}="",I{r}=""),"",IF(H{r}>0,I{r}/H{r},""))',
            "N": f'=IF(S{r}<2,"",_xlfn.MAXIFS(Datos!$H:$H,{cr}))',
            "O": f'=IF(N{r}="","",_xlfn.MINIFS(Datos!$G:$G,{cr},Datos!$H:$H,N{r})/1440)',
            "P": (f'=IF(OR(COUNTIFS({valid},Datos!$G:$G,{corte})=0,COUNTIFS({valid_ant},Datos!$G:$G,{corte})=0),"",'
                  f'SUMIFS(Datos!$D:$D,{valid},Datos!$G:$G,{corte})-SUMIFS(Datos!$D:$D,{valid_ant},Datos!$G:$G,{corte}))'),
            "Q": f'=IF(OR(K{r}="",V{r}=""),"",IF(V{r}>0,K{r}/V{r}-1,""))',
            "R": f'=IF(S{r}=0,"",_xlfn.MAXIFS(Datos!$D:$D,{valid}))',
            "S": f"=COUNTIFS({valid})",
            "T": f"=COUNTIFS({cr},Datos!$D:$D,0)",
            "U": f'=COUNTIFS({cr},Datos!$F:$F,">0")',
            "W": (f'=IF(Medidores!C{i + 2}="",1,IFERROR(IF(INDEX($H${r0}:$H${r1},MATCH(Medidores!C{i + 2},$C${r0}:$C${r1},0))="",1,0),1))'),
            "X": (f'=IF(Medidores!C{i + 2}="",1,IFERROR(IF(INDEX($P${r0}:$P${r1},MATCH(Medidores!C{i + 2},$C${r0}:$C${r1},0))="",1,0),1))'),
            "V": (f'=IF(COUNTIFS({valid_ant})<2,"",IFERROR((_xlfn.MAXIFS(Datos!$D:$D,{valid_ant})-_xlfn.MINIFS(Datos!$D:$D,{valid_ant}))'
                  f'/((_xlfn.MAXIFS(Datos!$G:$G,{valid_ant})-_xlfn.MINIFS(Datos!$G:$G,{valid_ant}))/60),""))'),
        }
        fmts = {"E": "hh:mm", "F": "hh:mm", "H": NUM3, "I": NUM3, "J": NUM3, "K": "#,##0.00",
                "L": "0.000", "M": "0%", "N": "#,##0.00", "O": "hh:mm", "P": NUM1,
                "Q": "+0%;-0%;0%", "R": NUM3}
        for col, formula in f.items():
            c = ws[f"{col}{r}"]
            c.value, c.font, c.border = formula, f_base, borde
            c.number_format = fmts.get(col, "General")
            if col in "DEFGO":
                c.alignment = Alignment(horizontal="center")
    for col in "STUVWX":
        ws.column_dimensions[col].hidden = True

    rng = f"D{r0}:D{r1}"
    estilo = lambda fondo, tinta: dict(fill=PatternFill("solid", fgColor=fondo), font=Font(name=F, color=tinta, bold=True))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'D{r0}="Normal"'], **estilo(VERDE_SUAVE, VERDE)))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'OR(D{r0}="Sin datos",D{r0}="Reactiva > 50 %")'], **estilo(ROJO_SUAVE, "B3261E")))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'D{r0}<>"Normal"'], **estilo(AMBAR_SUAVE, "A46A00")))
    ws.conditional_formatting.add(f"M{r0}:M{r1}", FormulaRule(formula=[f'AND(ISNUMBER(M{r0}),M{r0}>0.5)'], **estilo(ROJO_SUAVE, "B3261E")))
    ws.conditional_formatting.add(f"L{r0}:L{r1}", FormulaRule(formula=[f'AND(ISNUMBER(L{r0}),L{r0}<0.9)'], **estilo(AMBAR_SUAVE, "A46A00")))

    nota = r1 + 2
    notas = [
        "Celdas amarillas: día y medidor se eligen de la lista; la hora de corte se escribe (ej. 11:00).",
        "kWh 24 h al corte = lectura del día a la hora de corte − lectura del día anterior a la misma hora. Requiere ambas lecturas.",
        "kVARh / kWh > 50 %: la línea consume mucha reactiva. EMCALI cobra según la frontera (hoja EMCALI), donde el banco de condensadores compensa.",
        "kW medio vs día anterior compara la demanda media del periodo registrado de cada día. Las lecturas en cero se excluyen.",
        "Totales: las líneas L14–L50 están dentro de Estación planta (hoja Medidores, columna Dentro de) y no se suman dos veces.",
    ]
    for k, txt in enumerate(notas):
        ws[f"B{nota + k}"] = txt
        ws[f"B{nota + k}"].font = f_sub
    chart_row = nota + len(notas) + 1

    bar = BarChart()
    bar.type = "bar"
    bar.title = "Consumo por medidor en el periodo (kWh)"
    bar.style = 2
    bar.add_data(Reference(ws, min_col=8, min_row=11, max_row=r1), titles_from_data=True)
    bar.set_categories(Reference(ws, min_col=2, min_row=r0, max_row=r1))
    bar.legend = None
    bar.y_axis.numFmt = "#,##0"
    bar.y_axis.majorGridlines = None
    bar.x_axis.delete = False
    bar.y_axis.delete = False
    bar.series[0].graphicalProperties.solidFill = VERDE
    bar.series[0].graphicalProperties.line.noFill = True
    bar.height, bar.width = 9, 15
    ws.add_chart(bar, f"B{chart_row}")

    calc = wb["Calc"]
    col = BarChart()
    col.type = "col"
    col.title = "Demanda cada 15 min (kW) del medidor elegido"
    col.style = 2
    col.add_data(Reference(calc, min_col=3, min_row=1, max_row=97), titles_from_data=True)
    col.set_categories(Reference(calc, min_col=2, min_row=2, max_row=97))
    col.legend = None
    col.gapWidth = 20
    col.x_axis.delete = False
    col.y_axis.delete = False
    col.x_axis.tickLblSkip = 8
    col.series[0].graphicalProperties.solidFill = VERDE
    col.series[0].graphicalProperties.line.noFill = True
    col.height, col.width = 9, 17
    ws.add_chart(col, f"I{chart_row}")
    ws.freeze_panes = "A6"


def hoja_calc(wb):
    ws = wb.create_sheet("Calc")
    encabezado(ws, 1, ["Minuto fin", "Inicio", "kW"])
    for i in range(96):
        r = i + 2
        mins = (i + 1) * 15
        ws.cell(r, 1, mins)
        # Etiqueta = inicio del intervalo de 15 min que termina en `mins`
        ws.cell(r, 2, f"{(mins - 15) // 60:02d}:{(mins - 15) % 60:02d}")
        cr = "Datos!$B:$B,Tablero!$I$5,Datos!$A:$A,Tablero!$B$5,Datos!$G:$G,$A" + str(r)
        ws.cell(r, 3, f'=IF(COUNTIFS({cr},Datos!$H:$H,">=0")=0,"",SUMIFS(Datos!$H:$H,{cr}))').number_format = "#,##0.00"
        for c in range(1, 4):
            ws.cell(r, c).font = f_base
    ws["E1"] = "Hoja auxiliar para la gráfica de 15 minutos. No hace falta editarla."
    ws["E1"].font = f_sub
    return ws


def total_sin_duplicar(ws, r, medidores, first, lastc):
    """Suma de la fila sin contar dos veces un medidor que ya está dentro de otro (si ese otro tiene dato)."""
    padres = leer_padres()
    col = {ip: ws.cell(r, 2 + k).coordinate for k, (ip, _) in enumerate(medidores)}
    partes = []
    for ip, _ in medidores:
        padre = padres.get(ip)
        if padre in col:
            partes.append(f'IF(ISNUMBER({col[padre]}),0,N({col[ip]}))')
        else:
            partes.append(f'N({col[ip]})')
    return f'=IF(COUNT({first}:{lastc})=0,"",{"+".join(partes)})'


def hoja_historico(wb, medidores, dias):
    ws = wb.create_sheet("Histórico")
    ws["A1"] = "Consumo diario por medidor (kWh en el periodo registrado)"
    ws["A1"].font = Font(name=F, size=13, bold=True)
    encabezado(ws, 2, ["Fecha"] + [n for _, n in medidores] + ["Total"])
    ws.column_dimensions["A"].width = 13
    last_col = len(medidores) + 2
    for d_i, d in enumerate(dias):
        r = 3 + d_i
        ws.cell(r, 1, d).number_format = "yyyy-mm-dd"
        ws.cell(r, 1).font = f_base
        for m_i, (ip, _) in enumerate(medidores):
            cr = f'Datos!$B:$B,"{ip}",Datos!$A:$A,$A{r},Datos!$D:$D,">0"'
            c = ws.cell(r, 2 + m_i, f'=IF(COUNTIFS({cr})<2,"",_xlfn.MAXIFS(Datos!$D:$D,{cr})-_xlfn.MINIFS(Datos!$D:$D,{cr}))')
            c.number_format, c.font, c.border = NUM1, f_base, borde
        first, lastc = ws.cell(r, 2).coordinate, ws.cell(r, last_col - 1).coordinate
        c = ws.cell(r, last_col, total_sin_duplicar(ws, r, medidores, first, lastc))
        c.number_format, c.font, c.border = NUM1, Font(name=F, size=10, bold=True), borde
    for i in range(2, last_col + 1):
        ws.column_dimensions[ws.cell(2, i).column_letter].width = 15
    ws.freeze_panes = "B3"

    # Segunda tabla: consumo de 24 h entre la hora de corte de un día y la del anterior
    t2 = len(dias) + 5
    ws.cell(t2 - 1, 1, "Consumo de 24 h al corte (kWh) · hora de corte en Tablero!D5").font = Font(name=F, size=13, bold=True)
    encabezado(ws, t2, ["Fecha"] + [n for _, n in medidores] + ["Total", "EMCALI", "Diferencia", "Diferencia %"])
    corte = "(HOUR(Tablero!$D$5)*60+MINUTE(Tablero!$D$5))"
    for d_i, d in enumerate(dias):
        r = t2 + 1 + d_i
        ws.cell(r, 1, d).number_format = "yyyy-mm-dd"
        ws.cell(r, 1).font = f_base
        for m_i, (ip, _) in enumerate(medidores):
            hoy = f'Datos!$B:$B,"{ip}",Datos!$A:$A,$A{r},Datos!$D:$D,">0",Datos!$G:$G,{corte}'
            ayer = f'Datos!$B:$B,"{ip}",Datos!$A:$A,$A{r}-1,Datos!$D:$D,">0",Datos!$G:$G,{corte}'
            c = ws.cell(r, 2 + m_i, f'=IF(OR(COUNTIFS({hoy})=0,COUNTIFS({ayer})=0),"",SUMIFS(Datos!$D:$D,{hoy})-SUMIFS(Datos!$D:$D,{ayer}))')
            c.number_format, c.font, c.border = NUM1, f_base, borde
        first, lastc = ws.cell(r, 2).coordinate, ws.cell(r, last_col - 1).coordinate
        c = ws.cell(r, last_col, total_sin_duplicar(ws, r, medidores, first, lastc))
        c.number_format, c.font, c.border = NUM1, Font(name=F, size=10, bold=True), borde
        # EMCALI en la misma ventana: horas >= corte del día anterior + horas < corte del día
        hc = "HOUR(Tablero!$D$5)"
        tot, em = ws.cell(r, last_col).coordinate, ws.cell(r, last_col + 1).coordinate
        f_em = (f'=IF(OR(COUNTIFS(EMCALI!$A:$A,$A{r}-1)<24,COUNTIFS(EMCALI!$A:$A,$A{r})<24),"",'
                f'SUMIFS(EMCALI!$C:$C,EMCALI!$A:$A,$A{r}-1,EMCALI!$B:$B,">="&{hc})+SUMIFS(EMCALI!$C:$C,EMCALI!$A:$A,$A{r},EMCALI!$B:$B,"<"&{hc}))')
        extras = [(f_em, NUM1), (f'=IF(OR({tot}="",{em}=""),"",{em}-{tot})', NUM1),
                  (f'=IF(OR({tot}="",{em}=""),"",IF({em}>0,({em}-{tot})/{em},""))', "0.0%")]
        for k, (formula, fmt) in enumerate(extras, start=1):
            c = ws.cell(r, last_col + k, formula)
            c.number_format, c.font, c.border = fmt, f_base, borde
    for k in range(1, 4):
        ws.column_dimensions[ws.cell(t2, last_col + k).column_letter].width = 13
    nota = t2 + len(dias) + 1
    ws.cell(nota, 1, "Diferencia = EMCALI − total de medidores (las líneas L no se suman aparte porque ya están dentro de Estación planta). "
                     "EMCALI usa horas completas: con corte 11:00 toma de 11:00 a 11:00.").font = f_sub

    if dias:
        ch = BarChart()
        ch.type = "col"
        ch.title = "Consumo total por día (kWh)"
        ch.add_data(Reference(ws, min_col=last_col, min_row=2, max_row=2 + len(dias)), titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=1, min_row=3, max_row=2 + len(dias)))
        ch.legend = None
        ch.x_axis.delete = False
        ch.y_axis.delete = False
        ch.x_axis.number_format = "yyyy-mm-dd"
        ch.series[0].graphicalProperties.solidFill = VERDE
        ch.height, ch.width = 8, 18
        ws.add_chart(ch, f"A{2 * len(dias) + 9}")


TURNOS = [  # (nombre, horario real, horas de EMCALI asignadas, horas por día, actividad)
    ("A", "07:00 – 14:30", "07:00 – 14:00", 7, "Producción"),
    ("B", "14:00 – 21:30", "14:00 – 21:00", 7, "Producción"),
    ("C", "23:40 – 07:10", "23:00 – 07:00", 8, "Mantenimiento y mezcla"),
    ("Entre turnos", "21:30 – 23:40", "21:00 – 23:00", 2, "Sin personal"),
    ("Sin turno", "Domingo y noche del sábado", "—", 24, "Planta parada"),
]


def leer_emcali():
    ruta = BASE / "emcali_horario.csv"
    if not ruta.exists():
        return []
    num = lambda v: float(v) if v.strip() else None
    with open(ruta, newline="", encoding="utf-8") as fh:
        return [(date.fromisoformat(r["fecha"]), int(r["hora_inicio"][:2]), num(r["kwh"]),
                 num(r["kvarh_inductiva"]), num(r["kvarh_capacitiva"])) for r in csv.DictReader(fh)]


def hoja_emcali(wb, emcali):
    ws = wb.create_sheet("EMCALI")
    cols = ["Fecha", "Hora inicio", "kWh", "kVARh inductiva", "kVARh capacitiva", "Día (1=lun)", "Turno", "Inductiva sobre 50 %"]
    encabezado(ws, 1, cols)
    for i, (d, h, kwh, ind, cap) in enumerate(emcali, start=2):
        ws.cell(i, 1, d).number_format = "yyyy-mm-dd"
        ws.cell(i, 2, h)
        for col, v in ((3, kwh), (4, ind), (5, cap)):
            ws.cell(i, col, v).number_format = "#,##0.00"
        ws.cell(i, 6, f"=WEEKDAY(A{i},2)")
        # Lunes a sábado: C 23–07 (el C de la noche del domingo ya es del lunes), A 07–14, B 14–21
        ws.cell(i, 7, f'=IF(F{i}=7,IF(B{i}>=23,"C","Sin turno"),IF(B{i}<7,"C",IF(B{i}<14,"A",IF(B{i}<21,"B",'
                      f'IF(B{i}<23,"Entre turnos",IF(F{i}=6,"Sin turno","C"))))))')
        ws.cell(i, 8, f'=IF(D{i}="","",MAX(0,D{i}-0.5*C{i}))').number_format = "#,##0.00"
        for col in range(1, 9):
            ws.cell(i, col).font = f_base
    last = max(len(emcali) + 1, 2)
    tabla = Table(displayName="tEmcali", ref=f"A1:H{last}")
    tabla.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws.add_table(tabla)
    for col, w in zip("ABCDEFGH", [12, 11, 11, 15, 16, 11, 14, 18]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"
    ws["J1"] = "Datos horarios de EMCALI. Hora inicio 7 = de 07:00 a 08:00. Celdas vacías: el reporte de reactiva aún no incluye esa hora."
    ws["J2"] = "Inductiva sobre 50 % = kVARh inductiva − 50 % de los kWh de esa hora (lo que la CREG permite facturar)."
    for ref in ("J1", "J2"):
        ws[ref].font = f_sub


def hoja_turnos(wb, emcali):
    ws = wb.create_sheet("Turnos")
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Consumo por turno (datos de EMCALI)"
    ws["A1"].font = Font(name=F, size=14, bold=True)
    ws["A2"] = "Turnos de lunes a sábado. Producción en A y B; en C se hace mantenimiento y la mezcla del día siguiente. Cada hora de EMCALI se asigna al turno que la ocupa la mayor parte."
    ws["A2"].font = f_sub
    head = ["Turno", "Actividad", "Horario", "Horas EMCALI", "kWh total", "Horas registradas", "kW medio",
            "kWh promedio por turno", "% del consumo", "kVARh inductiva", "kVARh / kWh", "Inductiva sobre 50 %"]
    encabezado(ws, 4, head)
    r0 = 5
    for k, (t, real, asign, hdia, actividad) in enumerate(TURNOS):
        r = r0 + k
        crit_t = f'EMCALI!$G:$G,"{t}"'
        vals = [
            (t, "General"), (actividad, "General"), (real, "General"), (asign, "General"),
            (f"=SUMIFS(EMCALI!$C:$C,{crit_t})", "#,##0"),
            (f'=COUNTIFS({crit_t},EMCALI!$C:$C,"<>")', "#,##0"),
            (f'=IF(F{r}=0,"",E{r}/F{r})', "#,##0.0"),
            (f'=IF(F{r}=0,"",G{r}*{hdia})', "#,##0"),
            (f'=IF(SUM($E${r0}:$E${r0 + len(TURNOS) - 1})=0,"",E{r}/SUM($E${r0}:$E${r0 + len(TURNOS) - 1}))', "0.0%"),
            (f"=SUMIFS(EMCALI!$D:$D,{crit_t})", "#,##0"),
            (f'=IFERROR(J{r}/SUMIFS(EMCALI!$C:$C,{crit_t},EMCALI!$D:$D,"<>"),"")', "0.0%"),
            (f"=SUMIFS(EMCALI!$H:$H,{crit_t})", "#,##0.0"),
        ]
        for c_i, (v, fmt) in enumerate(vals, start=1):
            c = ws.cell(r, c_i, v)
            c.number_format, c.font, c.border = fmt, f_base, borde
    rt = r0 + len(TURNOS)
    ws.cell(rt, 1, "Total").font = Font(name=F, size=10, bold=True)
    for col, fmt in ((5, "#,##0"), (6, "#,##0"), (10, "#,##0"), (12, "#,##0.0")):
        L = get_column_letter(col)
        c = ws.cell(rt, col, f"=SUM({L}{r0}:{L}{rt - 1})")
        c.number_format, c.font, c.border = fmt, Font(name=F, size=10, bold=True), borde
    ws.cell(rt + 1, 1, "kWh promedio por turno = kW medio × horas del turno. kVARh / kWh solo cuenta horas con dato de reactiva.").font = f_sub
    for col, w in zip("ABCDEFGHIJKL", [14, 22, 26, 15, 12, 12, 10, 14, 12, 14, 12, 15]):
        ws.column_dimensions[col].width = w
    ws.row_dimensions[4].height = 30

    bar = BarChart()
    bar.type = "bar"
    bar.title = "kW medio por turno"
    bar.add_data(Reference(ws, min_col=7, min_row=4, max_row=rt - 1), titles_from_data=True)
    bar.set_categories(Reference(ws, min_col=1, min_row=r0, max_row=rt - 1))
    bar.legend = None
    bar.x_axis.delete = False
    bar.y_axis.delete = False
    bar.y_axis.majorGridlines = None
    bar.series[0].graphicalProperties.solidFill = VERDE
    bar.series[0].graphicalProperties.line.noFill = True
    bar.height, bar.width = 7, 14
    ws.add_chart(bar, "N4")

    # Tabla diaria por turno (día calendario)
    t0 = rt + 4
    ws.cell(t0 - 1, 1, "kWh por día y turno (día calendario: el C de 00:00 a 07:00 y de 23:00 a 24:00)").font = Font(name=F, size=12, bold=True)
    nombres = [t for t, *_ in TURNOS]
    encabezado(ws, t0, ["Fecha", "Día"] + nombres + ["Total día"])
    fechas = sorted({e[0] for e in emcali})
    dias_sem = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
    for j, d in enumerate(fechas):
        r = t0 + 1 + j
        ws.cell(r, 1, d).number_format = "yyyy-mm-dd"
        ws.cell(r, 2, dias_sem[d.weekday()])
        for k, t in enumerate(nombres):
            c = ws.cell(r, 3 + k, f'=SUMIFS(EMCALI!$C:$C,EMCALI!$A:$A,$A{r},EMCALI!$G:$G,"{t}")')
            c.number_format, c.border = "#,##0", borde
        L1, L2 = get_column_letter(3), get_column_letter(2 + len(nombres))
        c = ws.cell(r, 3 + len(nombres), f"=SUM({L1}{r}:{L2}{r})")
        c.number_format, c.border, c.font = "#,##0", borde, Font(name=F, size=10, bold=True)
        for col in range(1, 3 + len(nombres)):
            ws.cell(r, col).font = f_base
            ws.cell(r, col).border = borde
    if fechas:
        tot_col = 3 + len(nombres)
        ch = BarChart()
        ch.type = "col"
        ch.title = "Consumo diario de la planta según EMCALI (kWh)"
        ch.add_data(Reference(ws, min_col=tot_col, min_row=t0, max_row=t0 + len(fechas)), titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=1, min_row=t0 + 1, max_row=t0 + len(fechas)))
        ch.legend = None
        ch.x_axis.delete = False
        ch.y_axis.delete = False
        ch.x_axis.number_format = "dd/mm"
        ch.x_axis.tickLblSkip = 7
        ch.gapWidth = 30
        ch.series[0].graphicalProperties.solidFill = VERDE
        ch.series[0].graphicalProperties.line.noFill = True
        ch.height, ch.width = 8, 22
        ws.add_chart(ch, "N20")
    ws.freeze_panes = "A5"


def leer_produccion():
    ruta = BASE / "produccion_kg.csv"
    if not ruta.exists():
        return []
    with open(ruta, newline="", encoding="utf-8") as fh:
        return [(date.fromisoformat(r["fecha"]), r["linea"], int(r["turno"]), float(r["kg"])) for r in csv.DictReader(fh)]


def hoja_datos_prod(wb, prod):
    ws = wb.create_sheet("DatosProd")
    encabezado(ws, 1, ["Fecha", "Línea", "Turno", "kg", "Mes"])
    for i, (d, linea, turno, kg) in enumerate(prod, start=2):
        ws.cell(i, 1, d).number_format = "yyyy-mm-dd"
        ws.cell(i, 2, linea)
        ws.cell(i, 3, turno)
        ws.cell(i, 4, kg).number_format = "#,##0.0"
        ws.cell(i, 5, f"=MONTH(A{i})")
        for col in range(1, 6):
            ws.cell(i, col).font = f_base
    tabla = Table(displayName="tProd", ref=f"A1:E{max(len(prod) + 1, 2)}")
    tabla.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws.add_table(tabla)
    for col, w in zip("ABCDE", [12, 9, 8, 12, 7]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"
    ws["G1"] = "Kg producidos por día, línea y turno (archivo KG producidos 2026, hoja Data PA 2026). Turno 1 = A, turno 2 = B."
    ws["G1"].font = f_sub


def hoja_produccion(wb, prod, emcali):
    ws = wb.create_sheet("Producción")
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Energía por tonelada producida (kWh/t)"
    ws["A1"].font = Font(name=F, size=14, bold=True)
    ws["A2"] = ("kWh de EMCALI (toda la planta) ÷ kg producidos. Solo se calcula en días con producción registrada "
                "y EMCALI completo. Turno A = 07–14 h, turno B = 14–21 h; por turno solo si produjo 5 t o más.")
    ws["A2"].font = f_sub
    if not emcali:
        return
    fechas = []
    d, fin = min(e[0] for e in emcali), max([e[0] for e in emcali] + [p[0] for p in prod])
    while d <= fin:
        fechas.append(d)
        d += timedelta(days=1)
    t0 = 12
    t1 = t0 + len(fechas)
    rng = lambda col: f"${col}${t0 + 1}:${col}${t1}"
    resumen = [
        ("DÍAS CON DATO COMPLETO", f'=COUNT({rng("G")})', "0"),
        ("kWh/t PROMEDIO PLANTA", f'=IFERROR(SUMIFS({rng("F")},{rng("G")},">0")/SUMIFS({rng("E")},{rng("G")},">0")*1000,"")', "0.0"),
        ("kWh/t TURNO A", f'=IFERROR(SUMIFS({rng("H")},{rng("I")},">0")/SUMIFS({rng("C")},{rng("I")},">0")*1000,"")', "0.0"),
        ("kWh/t TURNO B", f'=IFERROR(SUMIFS({rng("J")},{rng("K")},">0")/SUMIFS({rng("D")},{rng("K")},">0")*1000,"")', "0.0"),
        ("MEJOR DÍA (kWh/t)", f'=IF(COUNT({rng("G")})=0,"",MIN({rng("G")}))', "0.0"),
        ("PEOR DÍA (kWh/t)", f'=IF(COUNT({rng("G")})=0,"",MAX({rng("G")}))', "0.0"),
    ]
    for k, (label, formula, fmt) in enumerate(resumen):
        col = get_column_letter(1 + 2 * k)
        ws[f"{col}4"] = label
        ws[f"{col}4"].font = f_label
        c = ws[f"{col}5"]
        c.value, c.number_format, c.font, c.fill = formula, fmt, f_kpi, fill_kpi

    ws.cell(t0 - 1, 1, "Detalle diario").font = Font(name=F, size=12, bold=True)
    head = ["Fecha", "Día", "kg turno A", "kg turno B", "kg total", "kWh día (EMCALI)", "kWh/t día",
            "kWh turno A", "kWh/t A", "kWh turno B", "kWh/t B", "Nota"]
    encabezado(ws, t0, head)
    ws.row_dimensions[t0].height = 30
    dias_sem = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
    for j, d in enumerate(fechas):
        r = t0 + 1 + j
        kgc = lambda t: f"SUMIFS(DatosProd!$D:$D,DatosProd!$A:$A,$A{r},DatosProd!$C:$C,{t})"
        emc = lambda t, n: (f'=IF(COUNTIFS(EMCALI!$A:$A,$A{r},EMCALI!$G:$G,"{t}",EMCALI!$C:$C,"<>")<{n},"",'
                            f'SUMIFS(EMCALI!$C:$C,EMCALI!$A:$A,$A{r},EMCALI!$G:$G,"{t}"))')
        vals = [
            (d, "yyyy-mm-dd"), (dias_sem[d.weekday()], "General"),
            (f"={kgc(1)}", "#,##0"), (f"={kgc(2)}", "#,##0"),
            (f"=SUMIFS(DatosProd!$D:$D,DatosProd!$A:$A,$A{r})", "#,##0"),
            (f'=IF(COUNTIFS(EMCALI!$A:$A,$A{r},EMCALI!$C:$C,"<>")<24,"",SUMIFS(EMCALI!$C:$C,EMCALI!$A:$A,$A{r}))', "#,##0"),
            (f'=IF(OR(F{r}="",E{r}=0),"",F{r}/E{r}*1000)', "0.0"),
            (emc("A", 7), "#,##0"), (f'=IF(OR(H{r}="",C{r}<5000),"",H{r}/C{r}*1000)', "0.0"),
            (emc("B", 7), "#,##0"), (f'=IF(OR(J{r}="",D{r}<5000),"",J{r}/D{r}*1000)', "0.0"),
            (f'=IF(AND(E{r}=0,F{r}=""),"Sin datos",IF(E{r}=0,"Sin producción registrada",IF(F{r}="","EMCALI incompleto","")))', "General"),
        ]
        for c_i, (v, fmt) in enumerate(vals, start=1):
            c = ws.cell(r, c_i, v)
            c.number_format, c.font, c.border = fmt, f_base, borde
    for col, w in zip("ABCDEFGHIJKL", [12, 6, 11, 11, 11, 13, 10, 12, 9, 12, 9, 24]):
        ws.column_dimensions[col].width = w
    ws.conditional_formatting.add(f"G{t0 + 1}:G{t1}", FormulaRule(formula=[f'AND(ISNUMBER(G{t0 + 1}),G{t0 + 1}>$C$5*1.25)'],
                                  fill=PatternFill("solid", fgColor=AMBAR_SUAVE), font=Font(name=F, color="A46A00", bold=True)))
    ws.cell(t1 + 1, 1, "En ámbar: días con kWh/t más de 25 % por encima del promedio de la planta.").font = f_sub

    ch = BarChart()
    ch.type = "col"
    ch.title = "kWh por tonelada producida, por día"
    ch.add_data(Reference(ws, min_col=7, min_row=t0, max_row=t1), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=t0 + 1, max_row=t1))
    ch.legend = None
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.x_axis.number_format = "dd/mm"
    ch.x_axis.tickLblSkip = 7
    ch.gapWidth = 40
    ch.series[0].graphicalProperties.solidFill = VERDE
    ch.series[0].graphicalProperties.line.noFill = True
    ch.height, ch.width = 8, 20
    ws.add_chart(ch, "N4")

    # kg por línea y mes (2026)
    lineas = sorted({p[1] for p in prod}, key=lambda x: int(x[1:]))
    meses = sorted({p[0].month for p in prod})
    m0 = 4
    ws.cell(m0 - 1, 27, "Kg producidos por línea y mes (2026)").font = Font(name=F, size=12, bold=True)
    nombres_mes = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    encabezado(ws, m0, ["Línea"] + [nombres_mes[m - 1] for m in meses], col0=27)
    for i, linea in enumerate(lineas + ["Total"]):
        r = m0 + 1 + i
        ws.cell(r, 27, linea).font = f_base
        for k, m in enumerate(meses):
            f = (f'=SUMIFS(DatosProd!$D:$D,DatosProd!$B:$B,"{linea}",DatosProd!$E:$E,{m})' if linea != "Total"
                 else f'=SUMIFS(DatosProd!$D:$D,DatosProd!$E:$E,{m})')
            c = ws.cell(r, 28 + k, f)
            c.number_format, c.font, c.border = "#,##0", f_base if linea != "Total" else Font(name=F, size=10, bold=True), borde
    ws.column_dimensions["AA"].width = 9
    ws.freeze_panes = "A6"


LINEAS_HIST = [  # (nombre en el tablero, IP o código del informe, línea en producción)
    ("L14", "192.168.50.5", "L14"), ("L16", "192.168.50.7", "L16"), ("L19", "L19", "L19"),
    ("L20", "192.168.50.6", "L20"), ("L21 (L18-21)", "192.168.50.4", "L18"),
    ("L22", "192.168.1.168", "L22"), ("L50", "192.168.50.3", None),
]


def leer_informes():
    ruta = BASE / "lecturas_informes.csv"
    if not ruta.exists():
        return []
    num = lambda v: float(v) if str(v).strip() else None
    with open(ruta, newline="", encoding="utf-8") as fh:
        return [(date.fromisoformat(r["fecha"]), r["ip"], num(r["kwh"]), num(r["kvarh"]), num(r["kvah"]), r["fuente"], r["nota"])
                for r in csv.DictReader(fh)]


def hoja_datos_informes(wb, informes):
    ws = wb.create_sheet("DatosInformes")
    encabezado(ws, 1, ["Fecha", "IP", "Medidor", "kWh", "kVARh", "kVAh", "Archivo", "Nota"])
    for i, (d, ip, kwh, kvarh, kvah, fuente, nota) in enumerate(informes, start=2):
        ws.cell(i, 1, d).number_format = "yyyy-mm-dd"
        ws.cell(i, 2, ip)
        ws.cell(i, 3, f'=IFERROR(INDEX(Medidores!$B:$B,MATCH(B{i},Medidores!$A:$A,0)),B{i})')
        for col, v in ((4, kwh), (5, kvarh), (6, kvah)):
            ws.cell(i, col, v).number_format = NUM3
        ws.cell(i, 7, fuente)
        ws.cell(i, 8, nota or None)
        for col in range(1, 9):
            ws.cell(i, col).font = f_base
    tabla = Table(displayName="tInformes", ref=f"A1:H{max(len(informes) + 1, 2)}")
    tabla.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws.add_table(tabla)
    for col, w in zip("ABCDEFGH", [12, 15, 18, 13, 13, 13, 30, 36]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"
    ws["J1"] = ("Lecturas diarias de los informes semanales (carpeta INFORME LINEAS), una por día hábil, tomadas en la mañana "
                "(entre 6:45 y 10:30 aprox.). Julio venía sin punto decimal; agosto y septiembre en MWh: todo está convertido a kWh.")
    ws["J2"] = "L19 no tiene IP en la red de medidores: se identifica como L19. Las correcciones de digitación se explican en la columna Nota."
    for ref in ("J1", "J2"):
        ws[ref].font = f_sub


def hoja_historico_lineas(wb, informes):
    ws = wb.create_sheet("Histórico líneas")
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Histórico de líneas (informes semanales)"
    ws["A1"].font = Font(name=F, size=14, bold=True)
    ws["A2"] = "kWh por día de cada línea, promediado entre la primera y la última lectura de cada semana (días hábiles)."
    ws["A2"].font = f_sub
    if not informes:
        return
    lunes0 = min(i[0] for i in informes)
    lunes0 -= timedelta(days=lunes0.weekday())
    semanas = []
    while lunes0 <= max(i[0] for i in informes):
        semanas.append(lunes0)
        lunes0 += timedelta(days=7)
    t0 = 4
    encabezado(ws, t0, ["Semana (lunes)"] + [n for n, *_ in LINEAS_HIST] + ["Total líneas"])
    for j, lun in enumerate(semanas):
        r = t0 + 1 + j
        ws.cell(r, 1, lun).number_format = "yyyy-mm-dd"
        ws.cell(r, 1).font = f_base
        for k, (_, ip, _) in enumerate(LINEAS_HIST):
            c_ = f'DatosInformes!$B:$B,"{ip}",DatosInformes!$A:$A,">="&$A{r},DatosInformes!$A:$A,"<"&($A{r}+7)'
            f = (f'=IF(COUNTIFS({c_})<2,"",(_xlfn.MAXIFS(DatosInformes!$D:$D,{c_})-_xlfn.MINIFS(DatosInformes!$D:$D,{c_}))'
                 f'/(_xlfn.MAXIFS(DatosInformes!$A:$A,{c_})-_xlfn.MINIFS(DatosInformes!$A:$A,{c_})))')
            c = ws.cell(r, 2 + k, f)
            c.number_format, c.font, c.border = NUM1, f_base, borde
        L1, L2 = get_column_letter(2), get_column_letter(1 + len(LINEAS_HIST))
        c = ws.cell(r, 2 + len(LINEAS_HIST), f'=IF(COUNT({L1}{r}:{L2}{r})=0,"",SUM({L1}{r}:{L2}{r}))')
        c.number_format, c.font, c.border = NUM1, Font(name=F, size=10, bold=True), borde
    t1 = t0 + len(semanas)
    ws.cell(t1 + 1, 1, "kWh/día. Vacío: menos de 2 lecturas esa semana. La semana del 14/09 no tiene informe.").font = f_sub
    ws.column_dimensions["A"].width = 15
    for k in range(len(LINEAS_HIST) + 1):
        ws.column_dimensions[get_column_letter(2 + k)].width = 13

    # kWh por tonelada por línea en un periodo elegible
    b0 = t1 + 4
    ws.cell(b0 - 1, 1, "kWh por tonelada de cada línea (solo electricidad de la línea)").font = Font(name=F, size=12, bold=True)
    ws.cell(b0, 1, "Desde (lectura)").font = f_label
    ws.cell(b0, 3, "Hasta (lectura)").font = f_label
    for col, v in ((2, date(2026, 7, 14)), (4, date(2026, 8, 5))):
        c = ws.cell(b0, col, v)
        c.number_format, c.font, c.fill, c.border = "yyyy-mm-dd", f_input, fill_input, borde
    ws.cell(b0, 6, "Energía = lectura Hasta − lectura Desde. Kg = producción desde el día Desde hasta el día anterior a Hasta "
                   "(las lecturas son de la mañana).").font = f_sub
    h0 = b0 + 2
    encabezado(ws, h0, ["Línea", "kWh", "kg producidos", "kWh/t"])
    for k, (nombre, ip, lp) in enumerate(LINEAS_HIST):
        r = h0 + 1 + k
        desde, hasta = f"$B${b0}", f"$D${b0}"
        lect = lambda d: f'SUMIFS(DatosInformes!$D:$D,DatosInformes!$B:$B,"{ip}",DatosInformes!$A:$A,{d})'
        cnt = lambda d: f'COUNTIFS(DatosInformes!$B:$B,"{ip}",DatosInformes!$A:$A,{d})'
        vals = [
            (nombre, "General"),
            (f'=IF(OR({cnt(desde)}=0,{cnt(hasta)}=0),"",{lect(hasta)}-{lect(desde)})', NUM1),
            ((f'=SUMIFS(DatosProd!$D:$D,DatosProd!$B:$B,"{lp}",DatosProd!$A:$A,">="&{desde},DatosProd!$A:$A,"<"&{hasta})'
              if lp else "Sin dato"), "#,##0"),
            (f'=IF(OR(B{r}="",NOT(ISNUMBER(C{r}))),"",IF(C{r}>0,B{r}/C{r}*1000,""))', "0.00"),
        ]
        for c_i, (v, fmt) in enumerate(vals, start=1):
            c = ws.cell(r, c_i, v)
            c.number_format, c.font, c.border = fmt, f_base, borde
    h1 = h0 + len(LINEAS_HIST)
    ws.cell(h1 + 1, 1, "L21 (L18-21) se compara con la producción de la LINEA 18. L50 no aparece en la base de producción.").font = f_sub

    bar = BarChart()
    bar.type = "bar"
    bar.title = "kWh por tonelada por línea"
    bar.add_data(Reference(ws, min_col=4, min_row=h0, max_row=h1), titles_from_data=True)
    bar.set_categories(Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1))
    bar.legend = None
    bar.x_axis.delete = False
    bar.y_axis.delete = False
    bar.y_axis.majorGridlines = None
    bar.series[0].graphicalProperties.solidFill = VERDE
    bar.series[0].graphicalProperties.line.noFill = True
    bar.height, bar.width = 7, 13
    ws.add_chart(bar, f"F{b0 + 2}")

    tot = Reference(ws, min_col=2 + len(LINEAS_HIST), min_row=t0, max_row=t1)
    ch = BarChart()
    ch.type = "col"
    ch.title = "kWh por día de todas las líneas, por semana"
    ch.add_data(tot, titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=t0 + 1, max_row=t1))
    ch.legend = None
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.x_axis.number_format = "dd/mm"
    ch.series[0].graphicalProperties.solidFill = VERDE
    ch.series[0].graphicalProperties.line.noFill = True
    ch.height, ch.width = 7, 16
    ws.add_chart(ch, "L4")
    ws.freeze_panes = "B5"


def hoja_instrucciones(wb):
    ws = wb.create_sheet("Instrucciones")
    ws.column_dimensions["A"].width = 110
    lineas = [
        ("Cómo usar este tablero", Font(name=F, size=13, bold=True)),
        ("1. En la hoja Tablero, elige el día en la celda amarilla B5 y el medidor para la gráfica en E5.", f_base),
        ("2. Para agregar lecturas a mano: pega las filas al final de la hoja Datos (Fecha, IP, Hora, kWh, kVARh, kVAh).", f_base),
        ("   Las columnas Minuto, kW intervalo y Línea se calculan solas. Mantén las filas ordenadas por Fecha, IP y Hora (de menor a mayor).", f_base),
        ("3. Si agregas un día nuevo a mano, escribe también esa fecha al final de la columna A de la hoja Histórico y copia las fórmulas de la fila anterior.", f_base),
        ("4. Los nombres de las líneas se cambian en la hoja Medidores.", f_base),
        ("5. Reloj de los medidores: varios guardan la hora en UTC (5 horas adelante). La hoja Medidores indica el desfase de cada uno", f_base),
        ("   y las horas de Datos ya están en hora de Colombia; la columna Hora en el medidor conserva la hora original.", f_base),
        ("6. Hora de corte (Tablero!D5): se usa para el consumo de 24 h. Debe ser una hora que aparezca en las fotos de todos los días (hoy: 11:00).", f_base),
        ("7. EMCALI y Turnos: los datos horarios de EMCALI se cargan desde emcali_horario.csv. La hoja Turnos reparte el consumo en A, B y C.", f_base),
        ("8. Producción: kg por día, línea y turno en produccion_kg.csv (hoja DatosProd). La hoja Producción calcula kWh por tonelada con EMCALI.", f_base),
        ("9. Histórico líneas: lecturas de los informes semanales (lecturas_informes.csv, hoja DatosInformes). Cambia las fechas amarillas para calcular kWh/t de otro periodo.", f_base),
        ("Requiere Excel 2019 o Microsoft 365 (usa las funciones MAXIFS y MINIFS). No necesita internet.", f_sub),
        ("Fuente de los datos: fotos de la pantalla Data Log de cada medidor, transcritas.", f_sub),
    ]
    for i, (txt, font) in enumerate(lineas, start=1):
        ws.cell(i, 1, txt).font = font


def main():
    medidores, lecturas = leer_datos()
    dias = sorted({r[0] for r in lecturas})
    wb = Workbook()
    hoja_datos(wb, lecturas)
    hoja_medidores(wb, medidores)
    hoja_calc(wb)
    hoja_historico(wb, medidores, dias)
    emcali = leer_emcali()
    hoja_emcali(wb, emcali)
    hoja_turnos(wb, emcali)
    prod = leer_produccion()
    hoja_datos_prod(wb, prod)
    hoja_produccion(wb, prod, emcali)
    informes = leer_informes()
    hoja_datos_informes(wb, informes)
    hoja_historico_lineas(wb, informes)
    # Medidor con más consumo el último día, para que la gráfica abra con datos
    ultimo = [r for r in lecturas if r[0] == dias[-1] and r[3]]
    delta = {}
    for _, ip, _, kwh, *_ in ultimo:
        lo, hi = delta.get(ip, (kwh, kwh))
        delta[ip] = (min(lo, kwh), max(hi, kwh))
    top = max(delta, key=lambda ip: delta[ip][1] - delta[ip][0])
    hoja_tablero(wb, medidores, dias, dict(medidores)[top])
    hoja_instrucciones(wb)
    wb.move_sheet("Turnos", offset=wb.index(wb["Histórico"]) + 1 - wb.index(wb["Turnos"]))
    wb.move_sheet("Producción", offset=wb.index(wb["Turnos"]) + 1 - wb.index(wb["Producción"]))
    wb.move_sheet("Histórico líneas", offset=wb.index(wb["Producción"]) + 1 - wb.index(wb["Histórico líneas"]))
    wb.move_sheet("Tablero", offset=-wb.index(wb["Tablero"]))
    wb.active = 0
    wb.save(SALIDA)
    print(f"OK {SALIDA.name}: {len(lecturas)} lecturas, {len(dias)} días, {len(medidores)} medidores")


if __name__ == "__main__":
    main()
