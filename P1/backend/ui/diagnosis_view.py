import tkinter as tk
from ui.theme import COLORS, FONTS

URGENCY_COLORS = {
    "alta":   "#E05C6A",
    "media":  "#F4A261",
    "baja":   "#00C9A7",
}

def styled_button(parent, text, command, secondary=False):
    bg = COLORS["bg_input"] if secondary else COLORS["accent"]
    fg = COLORS["text_secondary"] if secondary else COLORS["bg_dark"]
    hover_bg = COLORS["border"] if secondary else COLORS["accent_hover"]

    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, font=FONTS["button"],
        relief="flat", bd=0, padx=24, pady=10,
        cursor="hand2", activebackground=hover_bg, activeforeground=fg,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


class DiagnosisView(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.controller = controller
        self.result_frames = []
        self.build_ui()

    def build_ui(self):

        # ── Barra lateral ─────────────────────────────────────────────
        sidebar = tk.Frame(self, bg=COLORS["bg_card"], width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Frame(sidebar, bg=COLORS["accent"], height=4).pack(fill="x")

        logo_frame = tk.Frame(sidebar, bg=COLORS["bg_card"])
        logo_frame.pack(pady=(40, 10))

        tk.Label(logo_frame, text="Medi", font=FONTS["logo"],
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")
        tk.Label(logo_frame, text="Logic", font=FONTS["logo"],
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(side="left")

        tk.Label(sidebar, text="Sistema de Diagnóstico\nMédico Inteligente",
                 font=("Helvetica", 10), bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"], justify="center").pack(pady=(0, 40))

        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=30)

        tk.Label(sidebar, text="RESULTADO", font=("Helvetica", 9, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(pady=(20, 4))
        tk.Label(sidebar, text="Diagnóstico Generado", font=FONTS["heading"],
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack()

        # Nombre del paciente en sidebar
        self.nombre_label = tk.Label(sidebar, text="",
                                      font=FONTS["subtitle"],
                                      bg=COLORS["bg_card"],
                                      fg=COLORS["text_secondary"],
                                      wraplength=220)
        self.nombre_label.pack(pady=(20, 0), padx=20)

        tk.Frame(sidebar, bg=COLORS["bg_card"]).pack(expand=True)

        styled_button(
            sidebar, text="← Nueva Consulta",
            command=lambda: self.controller.show_frame(
                __import__("ui.patient_view").patient_view.PatientView
            ),
            secondary=True,
        ).pack(pady=(0, 30), padx=30, fill="x")

        # ── Área principal ────────────────────────────────────────────
        main = tk.Frame(self, bg=COLORS["bg_dark"])
        main.pack(side="left", fill="both", expand=True, padx=60, pady=50)

        # Header
        self.title_label = tk.Label(main, text="Resultados del Diagnóstico",
                                     font=FONTS["title"], bg=COLORS["bg_dark"],
                                     fg=COLORS["text_primary"])
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(main, text="",
                                        font=FONTS["body_sm"], bg=COLORS["bg_dark"],
                                        fg=COLORS["text_secondary"])
        self.subtitle_label.pack(anchor="w", pady=(4, 0))

        tk.Frame(main, bg=COLORS["accent"], height=2, width=60).pack(anchor="w", pady=(8, 20))

        # Área de scroll para resultados
        scroll_outer = tk.Frame(main, bg=COLORS["bg_dark"])
        scroll_outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(scroll_outer, bg=COLORS["bg_dark"],
                           highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(scroll_outer, orient="vertical",
                                  command=canvas.yview)

        self.scroll_frame = tk.Frame(canvas, bg=COLORS["bg_dark"])
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Scroll con rueda del ratón
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(
            int(-1 * (e.delta / 120)), "units"
        ))

    def mostrar_resultados(self, resultados, nombre):
        # Limpiar resultados anteriores
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.nombre_label.config(text=nombre)
        self.subtitle_label.config(
            text=f"Paciente: {nombre}  —  {len(resultados) if resultados else 0} resultado(s)"
        )

        if not resultados:
            no_result = tk.Frame(self.scroll_frame, bg=COLORS["bg_card"],
                                  padx=30, pady=30)
            no_result.pack(fill="x", pady=(0, 12))

            tk.Label(no_result, text="⚠", font=("Helvetica", 28),
                     bg=COLORS["bg_card"], fg=COLORS["warning"]).pack()
            tk.Label(no_result, text="No se encontró diagnóstico",
                     font=FONTS["heading"], bg=COLORS["bg_card"],
                     fg=COLORS["text_primary"]).pack(pady=(8, 4))
            tk.Label(no_result,
                     text="Los síntomas ingresados no coinciden con ningún patrón conocido.",
                     font=FONTS["body_sm"], bg=COLORS["bg_card"],
                     fg=COLORS["text_secondary"]).pack()
            return

        for i, r in enumerate(resultados):
            self._crear_card_resultado(r, i)

    def _crear_card_resultado(self, r, index):
        urgencia = str(r.get("U", "")).lower()
        urgencia_color = URGENCY_COLORS.get(urgencia, COLORS["text_muted"])
        afinidad = r.get("P", 0)

        card = tk.Frame(self.scroll_frame, bg=COLORS["bg_card"], padx=28, pady=22)
        card.pack(fill="x", pady=(0, 12))

        # Borde izquierdo con color de urgencia
        accent_bar = tk.Frame(card, bg=urgencia_color, width=4)
        accent_bar.pack(side="left", fill="y", padx=(0, 20))

        content = tk.Frame(card, bg=COLORS["bg_card"])
        content.pack(side="left", fill="both", expand=True)

        # Fila superior: enfermedad + badge urgencia
        top_row = tk.Frame(content, bg=COLORS["bg_card"])
        top_row.pack(fill="x")

        tk.Label(
            top_row,
            text=f"#{index+1}  {r.get('E', 'Desconocido')}",
            font=FONTS["heading"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_primary"],
        ).pack(side="left")

        # Badge de urgencia
        badge = tk.Label(
            top_row,
            text=f"  Urgencia: {r.get('U', '—')}  ",
            font=("Helvetica", 9, "bold"),
            bg=urgencia_color,
            fg=COLORS["bg_dark"],
            padx=8,
            pady=3,
        )
        badge.pack(side="right")

        # Barra de afinidad
        bar_frame = tk.Frame(content, bg=COLORS["bg_card"])
        bar_frame.pack(fill="x", pady=(12, 4))

        tk.Label(bar_frame, text="Afinidad:", font=FONTS["body_sm"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side="left")
        tk.Label(bar_frame, text=f"  {afinidad}%", font=("Helvetica", 11, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(side="left")

        # Barra visual de afinidad
        bar_bg = tk.Frame(content, bg=COLORS["bg_input"], height=6)
        bar_bg.pack(fill="x", pady=(0, 4))
        bar_bg.update_idletasks()

        try:
            pct = min(max(float(afinidad), 0), 100) / 100
        except (ValueError, TypeError):
            pct = 0

        bar_fill = tk.Frame(bar_bg, bg=urgencia_color, height=6)
        bar_fill.place(relwidth=pct, relheight=1)