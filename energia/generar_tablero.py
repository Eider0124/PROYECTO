"""Genera Tablero_Energia.xlsx a partir de lecturas.csv y medidores.csv.

Uso: python3 generar_tablero.py
Cada día se agregan las lecturas nuevas a lecturas.csv y se vuelve a ejecutar.
El Excel resultante funciona sin internet: todo se calcula con fórmulas.
"""
import csv
from datetime import datetime, time, timedelta
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


def hoja_medidores(wb, medidores):
    ws = wb.create_sheet("Medidores")
    encabezado(ws, 1, ["IP", "Nombre de la línea"])
    for i, (ip, nombre) in enumerate(medidores, start=2):
        ws.cell(i, 1, ip).font = f_base
        c = ws.cell(i, 2, nombre)
        c.font = Font(name=F, size=10, color="0000FF")
        for col in (1, 2):
            ws.cell(i, col).border = borde
    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 24
    ws["D1"] = "Puedes cambiar los nombres de la columna B; el tablero se actualiza solo."
    ws["D1"].font = f_sub
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
    ws["D5"] = time(14, 45)
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
        ("B", "CONSUMO DEL PERIODO (kWh)", f"=SUM(H{r0}:H{r1})", NUM1),
        ("D", "DEMANDA MEDIA TOTAL (kW)", f"=SUM(K{r0}:K{r1})", NUM1),
        ("G", "CONSUMO 24 h AL CORTE (kWh)", f'=IF(COUNT(P{r0}:P{r1})=0,"Falta el día anterior",SUM(P{r0}:P{r1}))', NUM1),
        ("J", "FACTOR DE POTENCIA", f'=IFERROR(SUMPRODUCT(--ISNUMBER(L{r0}:L{r1}),H{r0}:H{r1})/SUM(J{r0}:J{r1}),"")', "0.000"),
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
            "kW medio vs día anterior", "Última lectura kWh", "válidas", "en cero", "con kVAh", "kW medio día ant."]
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
    for col in "STUV":
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
        "Celdas amarillas: día y medidor se eligen de la lista; la hora de corte se escribe (ej. 14:45).",
        "kWh 24 h al corte = lectura del día a la hora de corte − lectura del día anterior a la misma hora. Requiere ambas lecturas.",
        "kVARh / kWh > 50 %: la energía reactiva supera el límite de la CREG y se factura. FP en ámbar cuando es menor a 0.90.",
        "kW medio vs día anterior compara la demanda media del periodo registrado de cada día. Las lecturas en cero se excluyen.",
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
        c = ws.cell(r, last_col, f"=SUM({first}:{lastc})")
        c.number_format, c.font, c.border = NUM1, Font(name=F, size=10, bold=True), borde
    for i in range(2, last_col + 1):
        ws.column_dimensions[ws.cell(2, i).column_letter].width = 15
    ws.freeze_panes = "B3"

    # Segunda tabla: consumo de 24 h entre la hora de corte de un día y la del anterior
    t2 = len(dias) + 5
    ws.cell(t2 - 1, 1, "Consumo de 24 h al corte (kWh) · hora de corte en Tablero!D5").font = Font(name=F, size=13, bold=True)
    encabezado(ws, t2, ["Fecha"] + [n for _, n in medidores] + ["Total"])
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
        c = ws.cell(r, last_col, f'=IF(COUNT({first}:{lastc})=0,"",SUM({first}:{lastc}))')
        c.number_format, c.font, c.border = NUM1, Font(name=F, size=10, bold=True), borde

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
        ws.add_chart(ch, f"A{2 * len(dias) + 8}")


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
        ("6. Hora de corte (Tablero!D5): se usa para el consumo de 24 h. Tomando las fotos a las 3:00 p. m., la lectura común de todos es 14:45.", f_base),
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
    # Medidor con más consumo el último día, para que la gráfica abra con datos
    ultimo = [r for r in lecturas if r[0] == dias[-1] and r[3]]
    delta = {}
    for _, ip, _, kwh, *_ in ultimo:
        lo, hi = delta.get(ip, (kwh, kwh))
        delta[ip] = (min(lo, kwh), max(hi, kwh))
    top = max(delta, key=lambda ip: delta[ip][1] - delta[ip][0])
    hoja_tablero(wb, medidores, dias, dict(medidores)[top])
    hoja_instrucciones(wb)
    wb.move_sheet("Tablero", offset=-wb.index(wb["Tablero"]))
    wb.active = 0
    wb.save(SALIDA)
    print(f"OK {SALIDA.name}: {len(lecturas)} lecturas, {len(dias)} días, {len(medidores)} medidores")


if __name__ == "__main__":
    main()
