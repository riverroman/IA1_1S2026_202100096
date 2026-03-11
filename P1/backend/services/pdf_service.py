import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)

# ── Paleta visual coherente con el tema de la app ─────────────────────
C_DARK    = colors.HexColor("#0D1B2A")
C_CARD    = colors.HexColor("#152336")
C_ACCENT  = colors.HexColor("#00C9A7")
C_WARNING = colors.HexColor("#F4A261")
C_DANGER  = colors.HexColor("#E05C6A")
C_TEXT    = colors.HexColor("#E8F0F7")
C_MUTED   = colors.HexColor("#7A9BB5")
C_WHITE   = colors.white

URGENCY_COLOR = {
    "Alta":  C_DANGER,
    "Media": C_WARNING,
    "Baja":  C_ACCENT,
}


class PDFService:

    def generar(self, paquete: dict, ruta: str = None) -> str:
        """
        Genera el informe PDF del paquete de diagnóstico.
        Devuelve la ruta del archivo generado.
        """
        if ruta is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_safe = paquete["nombre"].replace(" ", "_")
            ruta = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                f"informe_{nombre_safe}_{ts}.pdf"
            )

        doc = SimpleDocTemplate(
            ruta,
            pagesize=letter,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        styles = self._estilos()
        story  = []

        # ── Portada / header ──────────────────────────────────────────
        story += self._header(paquete, styles)
        story.append(Spacer(1, 14))

        # ── Resumen del paciente ──────────────────────────────────────
        story += self._resumen_paciente(paquete, styles)
        story.append(Spacer(1, 14))

        # ── Síntomas reportados ───────────────────────────────────────
        story += self._seccion_sintomas(paquete, styles)
        story.append(Spacer(1, 14))

        # ── Resultados ────────────────────────────────────────────────
        if not paquete["resultados"]:
            story.append(Paragraph("No se encontró diagnóstico con afinidad ≥ 30%.",
                                   styles["body_muted"]))
        else:
            for i, r in enumerate(paquete["resultados"]):
                story += self._card_resultado(r, i + 1, styles)
                story.append(Spacer(1, 12))

        # ── Pie de página / sello ─────────────────────────────────────
        story += self._footer(paquete, styles)

        doc.build(story)
        return ruta

    # ══════════════════════════════════════════════════════════════════
    # SECCIONES
    # ══════════════════════════════════════════════════════════════════

    def _header(self, paquete, styles):
        elements = []

        # Tabla con logo + info
        logo_text = Paragraph("<b><font color='#00C9A7'>Medi</font>Logic</b>",
                               styles["logo"])
        info_text = Paragraph(
            f"<font color='#7A9BB5'>Informe de Diagnóstico Médico<br/>"
            f"Fecha: {paquete['fecha']}</font>",
            styles["body_muted"]
        )

        header_table = Table(
            [[logo_text, info_text]],
            colWidths=[3 * inch, 4.5 * inch]
        )
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_CARD),
            ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 16),
            ("RIGHTPADDING", (0, 0), (-1, -1), 16),
            ("TOPPADDING",   (0, 0), (-1, -1), 14),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 14),
            ("LINEBELOW",  (0, 0), (-1, 0), 3, C_ACCENT),
        ]))
        elements.append(header_table)
        return elements

    def _resumen_paciente(self, paquete, styles):
        elements = []
        elements.append(Paragraph("Datos del Paciente", styles["section_title"]))
        elements.append(HRFlowable(width="100%", thickness=1,
                                    color=C_ACCENT, spaceAfter=8))

        rows = [
            ["Paciente",   paquete["nombre"]],
            ["Fecha",      paquete["fecha"]],
            ["Diagnósticos encontrados", str(paquete["total"])],
        ]
        if paquete.get("alergias"):
            rows.append(["Alergias", ", ".join(paquete["alergias"])])
        if paquete.get("cronicas"):
            rows.append(["Condiciones crónicas", ", ".join(paquete["cronicas"])])

        data = [[Paragraph(f"<b>{k}</b>", styles["table_label"]),
                 Paragraph(v, styles["table_value"])]
                for k, v in rows]

        t = Table(data, colWidths=[2 * inch, 5.5 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), C_CARD),
            ("TEXTCOLOR",    (0, 0), (-1, -1), C_TEXT),
            ("ROWBACKGROUNDS",(0, 0),(-1, -1), [C_CARD, colors.HexColor("#1C2E42")]),
            ("LEFTPADDING",  (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING",   (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(t)
        return elements

    def _seccion_sintomas(self, paquete, styles):
        elements = []
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Síntomas Reportados", styles["section_title"]))
        elements.append(HRFlowable(width="100%", thickness=1,
                                    color=C_ACCENT, spaceAfter=8))

        col_sev = {"leve": "#00C9A7", "moderado": "#F4A261", "severo": "#E05C6A"}
        sintomas_data = []
        row = []
        for i, (s, nivel) in enumerate(paquete["sintomas"]):
            color_hex = col_sev.get(nivel, "#7A9BB5")
            cell = Paragraph(
                f"{s.replace('_', ' ').capitalize()} "
                f"<font color='{color_hex}'>[{nivel}]</font>",
                styles["body"]
            )
            row.append(cell)
            if len(row) == 3:
                sintomas_data.append(row)
                row = []
        if row:
            while len(row) < 3:
                row.append(Paragraph("", styles["body"]))
            sintomas_data.append(row)

        if sintomas_data:
            t = Table(sintomas_data, colWidths=[2.5 * inch] * 3)
            t.setStyle(TableStyle([
                ("BACKGROUND",   (0, 0), (-1, -1), C_CARD),
                ("LEFTPADDING",  (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING",   (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
            ]))
            elements.append(t)
        return elements

    def _card_resultado(self, r, idx, styles):
        elements = []
        urg     = r["urgencia"]
        uc      = URGENCY_COLOR.get(urg, C_MUTED)
        pct     = float(r["porcentaje"])

        # ── Título del resultado ──────────────────────────────────────
        titulo = Table(
            [[
                Paragraph(f"<b>#{idx}  {r['nombre_ui']}</b>", styles["result_title"]),
                Paragraph(f"<b>{urg}</b>", styles["badge"]),
            ]],
            colWidths=[5 * inch, 2.5 * inch]
        )
        titulo.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), C_CARD),
            ("LEFTPADDING",  (0, 0), (0, 0),   16),
            ("RIGHTPADDING", (1, 0), (1, 0),   12),
            ("TOPPADDING",   (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
            ("LINEABOVE",    (0, 0), (-1, 0),  3, uc),
            ("ALIGN",        (1, 0), (1, 0),   "RIGHT"),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(titulo)

        # Descripción
        if r.get("descripcion"):
            desc_t = Table(
                [[Paragraph(r["descripcion"], styles["body_muted"])]],
                colWidths=[7.5 * inch]
            )
            desc_t.setStyle(TableStyle([
                ("BACKGROUND",   (0,0),(-1,-1), C_CARD),
                ("LEFTPADDING",  (0,0),(-1,-1), 16),
                ("TOPPADDING",   (0,0),(-1,-1), 0),
                ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ]))
            elements.append(desc_t)

        # ── Afinidad + barra ──────────────────────────────────────────
        bar_filled = int(pct / 100 * 40)
        bar_empty  = 40 - bar_filled
        bar_str    = "█" * bar_filled + "░" * bar_empty

        aff_data = [[
            Paragraph(f"<b>Afinidad: {pct}%</b>", styles["afinidad"]),
            Paragraph(f"<font color='#{uc.hexval()[2:]}'>{bar_str}</font>",
                       styles["bar"]),
        ]]
        aff_t = Table(aff_data, colWidths=[1.8 * inch, 5.7 * inch])
        aff_t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), C_CARD),
            ("LEFTPADDING",  (0,0),(-1,-1), 16),
            ("TOPPADDING",   (0,0),(-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ]))
        elements.append(aff_t)

        # ── Acción ───────────────────────────────────────────────────
        accion_t = Table(
            [[Paragraph(f"<b>→  {r['accion']}</b>", styles["accion"])]],
            colWidths=[7.5 * inch]
        )
        accion_t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), colors.HexColor("#0D2420") if urg=="Baja"
                                            else colors.HexColor("#2A1D10") if urg=="Media"
                                            else colors.HexColor("#2A1520")),
            ("LEFTPADDING",  (0,0),(-1,-1), 16),
            ("TOPPADDING",   (0,0),(-1,-1), 10),
            ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ]))
        elements.append(accion_t)

        # ── Medicamento ───────────────────────────────────────────────
        med   = r.get("medicamento", "ninguno")
        todos = r.get("todos_meds", [])
        med_display = str(med).replace("_", " ").title() if med != "ninguno" \
                      else "Ninguno disponible — revisar alergias"
        otros = [str(m).replace("_", " ").title() for m in todos if m != med]

        med_rows = [
            [Paragraph("<b>Medicamento sugerido:</b>", styles["table_label"]),
             Paragraph(f"<b>{med_display}</b>", styles["med_name"])],
        ]
        if otros:
            med_rows.append([
                Paragraph("Alternativas:", styles["table_label"]),
                Paragraph(", ".join(otros), styles["body_muted"]),
            ])

        med_t = Table(med_rows, colWidths=[2 * inch, 5.5 * inch])
        med_t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), C_CARD),
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_CARD, colors.HexColor("#1C2E42")]),
            ("LEFTPADDING",  (0,0),(-1,-1), 16),
            ("TOPPADDING",   (0,0),(-1,-1), 7),
            ("BOTTOMPADDING",(0,0),(-1,-1), 7),
            ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ]))
        elements.append(med_t)

        # ── Síntomas coincidentes / ausentes ─────────────────────────
        coins = [str(s).replace("_", " ") for s in r.get("coinciden", [])]
        ausen = [str(s).replace("_", " ") for s in r.get("ausentes", [])]

        coins_txt = "\n".join(f"• {s}" for s in coins) if coins else "—"
        ausen_txt = "\n".join(f"• {s}" for s in ausen) if ausen else "—"

        sym_t = Table(
            [[
                Paragraph(f"<b>Síntomas coincidentes</b><br/>"
                          f"<font color='#00C9A7'>{coins_txt.replace(chr(10), '<br/>')}</font>",
                          styles["body"]),
                Paragraph(f"<b>Síntomas no reportados</b><br/>"
                          f"<font color='#7A9BB5'>{ausen_txt.replace(chr(10), '<br/>')}</font>",
                          styles["body"]),
            ]],
            colWidths=[3.75 * inch, 3.75 * inch]
        )
        sym_t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), C_CARD),
            ("LEFTPADDING",  (0,0),(-1,-1), 16),
            ("TOPPADDING",   (0,0),(-1,-1), 10),
            ("BOTTOMPADDING",(0,0),(-1,-1), 10),
            ("VALIGN",       (0,0),(-1,-1), "TOP"),
            ("LINEAFTER",    (0,0),(0,-1),  1, colors.HexColor("#1F3448")),
        ]))
        elements.append(sym_t)

        # ── Reglas Prolog ─────────────────────────────────────────────
        reglas = r.get("reglas", [])
        if reglas:
            reg_data = [[Paragraph(reg, styles["mono"])] for reg in reglas]
            reg_t = Table(reg_data, colWidths=[7.5 * inch])
            reg_t.setStyle(TableStyle([
                ("BACKGROUND",   (0,0),(-1,-1), colors.HexColor("#1C2E42")),
                ("ROWBACKGROUNDS",(0,0),(-1,-1),
                 [colors.HexColor("#1C2E42"), colors.HexColor("#152336")]),
                ("LEFTPADDING",  (0,0),(-1,-1), 14),
                ("TOPPADDING",   (0,0),(-1,-1), 5),
                ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ]))

            reg_header = Table(
                [[Paragraph("<b>⚙  Reglas Prolog activadas</b>", styles["body_muted"])]],
                colWidths=[7.5 * inch]
            )
            reg_header.setStyle(TableStyle([
                ("BACKGROUND",   (0,0),(-1,-1), C_CARD),
                ("LEFTPADDING",  (0,0),(-1,-1), 14),
                ("TOPPADDING",   (0,0),(-1,-1), 8),
                ("BOTTOMPADDING",(0,0),(-1,-1), 4),
            ]))
            elements.append(reg_header)
            elements.append(reg_t)

        return [KeepTogether(elements[:4])] + elements[4:]

    def _footer(self, paquete, styles):
        elements = [
            Spacer(1, 20),
            HRFlowable(width="100%", thickness=1, color=C_MUTED),
            Spacer(1, 8),
        ]
        footer_t = Table(
            [[
                Paragraph("<b>MediLogic</b> — Sistema de Apoyo Diagnóstico",
                          styles["footer"]),
                Paragraph(
                    "⚠ Este informe es de carácter preliminar y no sustituye "
                    "la consulta con un profesional médico.",
                    styles["footer_warn"]
                ),
            ]],
            colWidths=[3 * inch, 4.5 * inch]
        )
        footer_t.setStyle(TableStyle([
            ("VALIGN", (0,0),(-1,-1), "TOP"),
        ]))
        elements.append(footer_t)
        return elements

    # ══════════════════════════════════════════════════════════════════
    # ESTILOS
    # ══════════════════════════════════════════════════════════════════

    def _estilos(self):
        base = getSampleStyleSheet()

        def ps(name, **kw):
            defaults = dict(
                fontName="Helvetica",
                fontSize=10,
                textColor=C_TEXT,
                leading=14,
                spaceAfter=2,
            )
            defaults.update(kw)
            return ParagraphStyle(name, **defaults)

        return {
            "logo": ps("logo", fontName="Helvetica-Bold", fontSize=22,
                        textColor=C_TEXT),
            "section_title": ps("section_title", fontName="Helvetica-Bold",
                                 fontSize=12, textColor=C_ACCENT, spaceAfter=4),
            "result_title":  ps("result_title", fontName="Helvetica-Bold",
                                 fontSize=13, textColor=C_TEXT),
            "badge":         ps("badge", fontName="Helvetica-Bold", fontSize=10,
                                 textColor=C_DARK),
            "body":          ps("body", fontSize=10, textColor=C_TEXT),
            "body_muted":    ps("body_muted", fontSize=9, textColor=C_MUTED),
            "table_label":   ps("table_label", fontName="Helvetica-Bold",
                                 fontSize=9, textColor=C_MUTED),
            "table_value":   ps("table_value", fontSize=10, textColor=C_TEXT),
            "afinidad":      ps("afinidad", fontName="Helvetica-Bold",
                                 fontSize=11, textColor=C_ACCENT),
            "bar":           ps("bar", fontName="Courier", fontSize=9,
                                 textColor=C_ACCENT),
            "accion":        ps("accion", fontName="Helvetica-Bold",
                                 fontSize=11, textColor=C_ACCENT),
            "med_name":      ps("med_name", fontName="Helvetica-Bold",
                                 fontSize=11, textColor=C_ACCENT),
            "mono":          ps("mono", fontName="Courier", fontSize=8,
                                 textColor=C_MUTED),
            "footer":        ps("footer", fontSize=8, textColor=C_MUTED),
            "footer_warn":   ps("footer_warn", fontSize=8, textColor=C_WARNING),
        }