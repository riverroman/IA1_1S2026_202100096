import tkinter as tk
from tkinter import messagebox
from services.diagnostic_service import DiagnosticService
from ui.diagnosis_view import DiagnosisView
from ui.theme import COLORS, FONTS

def _btn(parent, text, command, secondary=False):
    bg  = COLORS["bg_input"] if secondary else COLORS["accent"]
    fg  = COLORS["text_secondary"] if secondary else COLORS["bg_dark"]
    hbg = COLORS["border"] if secondary else COLORS["accent_hover"]
    b = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                  font=FONTS["button"], relief="flat", bd=0,
                  padx=24, pady=10, cursor="hand2",
                  activebackground=hbg, activeforeground=fg)
    b.bind("<Enter>", lambda e: b.config(bg=hbg))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b

class PatientView(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.controller    = controller
        self.service       = DiagnosticService()
        self._sintoma_vars  = {} 
        self._severidad_vars= {} 
        self._cronicas_vars = {}  
        self._canvas_ref   = None
        self.build_ui()

    # ══════════════════════════════════════════════════════════════════
    def build_ui(self):
        # ── Sidebar ───────────────────────────────────────────────────
        sb = tk.Frame(self, bg=COLORS["bg_card"], width=240)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        tk.Frame(sb, bg=COLORS["accent"], height=4).pack(fill="x")

        lr = tk.Frame(sb, bg=COLORS["bg_card"])
        lr.pack(pady=(30, 6))
        tk.Label(lr, text="Medi", font=FONTS["logo"],
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")
        tk.Label(lr, text="Logic", font=FONTS["logo"],
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(side="left")

        tk.Label(sb, text="Sistema de Diagnóstico\nMédico Inteligente",
                 font=FONTS["body_sm"], bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"], justify="center").pack(pady=(0, 20))
        tk.Frame(sb, bg=COLORS["border"], height=1).pack(fill="x", padx=24)
        tk.Label(sb, text="MÓDULO ACTIVO", font=("Helvetica", 9, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(pady=(16, 2))
        tk.Label(sb, text="Consulta de Paciente", font=FONTS["heading"],
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack()

        self._hist_lbl = tk.Label(sb, text="Historial: 0 diagnósticos",
                                   font=FONTS["body_sm"], bg=COLORS["bg_card"],
                                   fg=COLORS["text_muted"])
        self._hist_lbl.pack(pady=(16, 0))

        tk.Frame(sb, bg=COLORS["bg_card"]).pack(expand=True)
        _btn(sb, "⚙ Panel Admin",
             lambda: self.controller.show_frame(
                 __import__("ui.login_view").login_view.LoginView),
             secondary=True).pack(pady=(0, 10), padx=20, fill="x")
        _btn(sb, "Inicio",
             lambda: self.controller.show_frame(
                 __import__("ui.home_view").home_view.HomeView),
             secondary=True).pack(pady=(0, 24), padx=20, fill="x")

        # ── Área principal scrollable ─────────────────────────────────
        mo = tk.Frame(self, bg=COLORS["bg_dark"])
        mo.pack(side="left", fill="both", expand=True)

        canvas = tk.Canvas(mo, bg=COLORS["bg_dark"], highlightthickness=0, bd=0)
        self._canvas_ref = canvas
        vsb = tk.Scrollbar(mo, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        self._inner = tk.Frame(canvas, bg=COLORS["bg_dark"])
        self._inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._inner, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self._build_form()

    # ══════════════════════════════════════════════════════════════════
    def _build_form(self):
        p = self._inner
        PX = 50

        # Header
        hdr = tk.Frame(p, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=PX, pady=(40, 0))
        tk.Label(hdr, text="Nueva Consulta", font=FONTS["title"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"]).pack(anchor="w")
        tk.Label(hdr, text="Complete el formulario para obtener un diagnóstico personalizado",
                 font=FONTS["body_sm"], bg=COLORS["bg_dark"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 0))
        tk.Frame(hdr, bg=COLORS["accent"], height=2, width=60).pack(anchor="w", pady=(10, 0))

        # ── 01 Datos del paciente ─────────────────────────────────────
        self._sec(p, "01", "Datos del Paciente", PX)
        c1 = self._card(p, PX)
        tk.Label(c1, text="NOMBRE COMPLETO", font=("Helvetica", 9, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 6))
        self._nombre_entry = self._entry(c1)
        self._nombre_entry.pack(fill="x", ipady=10)

        # ── 02 Síntomas con checkboxes dinámicos ──────────────────────
        self._sec(p, "02", "Síntomas  —  selecciona y asigna severidad", PX)
        self._sintomas_frame = tk.Frame(p, bg=COLORS["bg_dark"])
        self._sintomas_frame.pack(fill="x", padx=PX)
        self._cargar_sintomas()

        # ── 03 Condiciones crónicas dinámicas ─────────────────────────
        self._sec(p, "03", "Condiciones Crónicas Preexistentes", PX)
        self._cronicas_frame = tk.Frame(p, bg=COLORS["bg_dark"])
        self._cronicas_frame.pack(fill="x", padx=PX)
        self._cargar_cronicas()

        # ── 04 Alergias ───────────────────────────────────────────────
        self._sec(p, "04", "Alergias a Medicamentos", PX)
        c4 = self._card(p, PX)
        tk.Label(c4, text="Medicamentos a los que eres alérgico (separados por coma):",
                 font=FONTS["body_sm"], bg=COLORS["bg_card"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 8))
        self._alergias_entry = self._entry(c4)
        self._alergias_entry.pack(fill="x", ipady=10)
        tk.Label(c4, text="Ejemplo: aspirina, ibuprofeno, penicilina",
                 font=FONTS["body_sm"], bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(4, 0))

        # ── Botones ───────────────────────────────────────────────────
        bf = tk.Frame(p, bg=COLORS["bg_dark"])
        bf.pack(fill="x", padx=PX, pady=(24, 50))
        _btn(bf, "▶  Iniciar Diagnóstico", self.diagnosticar).pack(side="left")
        tk.Frame(bf, bg=COLORS["bg_dark"], width=12).pack(side="left")
        _btn(bf, "↺  Limpiar", self.limpiar_formulario,
             secondary=True).pack(side="left")
        tk.Frame(bf, bg=COLORS["bg_dark"], width=12).pack(side="left")
        _btn(bf, "⟳  Recargar síntomas", self.recargar_sintomas,
             secondary=True).pack(side="left")

    # ══════════════════════════════════════════════════════════════════
    # CARGA DINÁMICA DESDE PROLOG
    # ══════════════════════════════════════════════════════════════════

    def _cargar_sintomas(self):
        """Carga checkboxes desde sintoma(_, S) del .pl en memoria."""
        for w in self._sintomas_frame.winfo_children():
            w.destroy()
        self._sintoma_vars.clear()
        self._severidad_vars.clear()

        try:
            sintomas = self.service.obtener_todos_sintomas()
        except Exception:
            sintomas = []

        if not sintomas:
            card = self._card(self._sintomas_frame, 0)
            tk.Label(card,
                     text="⚠  No hay síntomas cargados. Carga el archivo RPA primero.",
                     font=FONTS["body_sm"], bg=COLORS["bg_card"],
                     fg=COLORS["warning"]).pack(anchor="w")
            return

        card = tk.Frame(self._sintomas_frame, bg=COLORS["bg_card"], padx=28, pady=16)
        card.pack(fill="x", pady=(0, 4))

        tk.Label(card, text=f"SÍNTOMAS DISPONIBLES ({len(sintomas)})",
                 font=("Helvetica", 9, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 12))

        col_sev = {
            "leve":     COLORS["accent"],
            "moderado": COLORS["warning"],
            "severo":   COLORS["danger"],
        }

        # Mostrar en columnas de 2
        grid = tk.Frame(card, bg=COLORS["bg_card"])
        grid.pack(fill="x")

        for i, s in enumerate(sintomas):
            vb = tk.BooleanVar()
            vs = tk.StringVar(value="moderado")
            self._sintoma_vars[s]    = vb
            self._severidad_vars[s]  = vs

            row_f = tk.Frame(grid, bg=COLORS["bg_card"])
            col = i % 2
            fila = i // 2
            row_f.grid(row=fila, column=col, sticky="w", padx=(0, 20), pady=2)

            tk.Checkbutton(
                row_f,
                text=s.replace("_", " ").capitalize(),
                variable=vb,
                bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                selectcolor=COLORS["bg_input"],
                activebackground=COLORS["bg_card"],
                activeforeground=COLORS["accent"],
                font=FONTS["body_sm"], anchor="w",
                cursor="hand2", width=26,
            ).pack(side="left")

            sf = tk.Frame(row_f, bg=COLORS["bg_card"])
            sf.pack(side="left")
            for nivel in ["leve", "moderado", "severo"]:
                tk.Radiobutton(
                    sf, text=nivel, variable=vs, value=nivel,
                    bg=COLORS["bg_card"], fg=col_sev[nivel],
                    selectcolor=COLORS["bg_input"],
                    activebackground=COLORS["bg_card"],
                    font=("Helvetica", 8), cursor="hand2",
                ).pack(side="left", padx=2)

    def _cargar_cronicas(self):
        """Carga checkboxes desde clasificacion(E, cronico) del .pl."""
        for w in self._cronicas_frame.winfo_children():
            w.destroy()
        self._cronicas_vars.clear()

        try:
            cronicas = self.service.obtener_cronicas_disponibles()
        except Exception:
            cronicas = []

        card = tk.Frame(self._cronicas_frame, bg=COLORS["bg_card"], padx=28, pady=16)
        card.pack(fill="x", pady=(0, 4))

        tk.Label(card, text="Selecciona las enfermedades crónicas que ya padeces:",
                 font=FONTS["body_sm"], bg=COLORS["bg_card"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 12))

        if not cronicas:
            tk.Label(card,
                     text="No hay enfermedades crónicas registradas aún.",
                     font=FONTS["body_sm"], bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"]).pack(anchor="w")
            return

        grid = tk.Frame(card, bg=COLORS["bg_card"])
        grid.pack(fill="x")

        for i, c in enumerate(cronicas):
            var = tk.BooleanVar()
            self._cronicas_vars[c] = var
            nombre = c.replace("_", " ").title()
            tk.Checkbutton(
                grid,
                text=nombre,
                variable=var,
                bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                selectcolor=COLORS["bg_input"],
                activebackground=COLORS["bg_card"],
                activeforeground=COLORS["accent"],
                font=FONTS["body_sm"], anchor="w", cursor="hand2",
            ).grid(row=i // 3, column=i % 3, sticky="w", padx=10, pady=3)

    def recargar_sintomas(self):
        """Recarga síntomas y crónicas desde Prolog (útil tras cargar RPA)."""
        self._cargar_sintomas()
        self._cargar_cronicas()

    # ══════════════════════════════════════════════════════════════════
    # HELPERS UI
    # ══════════════════════════════════════════════════════════════════

    def _sec(self, parent, num, titulo, px):
        f = tk.Frame(parent, bg=COLORS["bg_dark"])
        f.pack(fill="x", padx=px, pady=(26, 6))
        tk.Label(f, text=num, font=("Georgia", 10, "bold"),
                 bg=COLORS["accent"], fg=COLORS["bg_dark"],
                 padx=8, pady=2).pack(side="left")
        tk.Label(f, text=f"  {titulo}", font=FONTS["heading"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"]).pack(side="left")

    def _card(self, parent, px):
        c = tk.Frame(parent, bg=COLORS["bg_card"], padx=28, pady=18)
        c.pack(fill="x", padx=px if isinstance(px, int) and px > 0 else 0,
               pady=(0, 4))
        return c

    def _entry(self, parent):
        return tk.Entry(
            parent,
            bg=COLORS["bg_input"], fg=COLORS["text_primary"],
            insertbackground=COLORS["accent"], relief="flat",
            font=FONTS["body"], highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"]
        )

    # ══════════════════════════════════════════════════════════════════
    # LÓGICA
    # ══════════════════════════════════════════════════════════════════

    def diagnosticar(self):
        nombre = self._nombre_entry.get().strip()
        if not nombre:
            messagebox.showwarning("Datos incompletos",
                                   "Ingresa el nombre del paciente.")
            return

        pares = [(s, self._severidad_vars[s].get())
                 for s, v in self._sintoma_vars.items() if v.get()]

        if not pares:
            messagebox.showwarning("Sin síntomas",
                                   "Selecciona al menos un síntoma.")
            return

        cronicas = [c for c, v in self._cronicas_vars.items() if v.get()]
        alergias = [
            a.strip().lower().replace(" ", "_")
            for a in self._alergias_entry.get().split(",") if a.strip()
        ]

        try:
            paquete = self.service.diagnosticar(nombre, pares, alergias, cronicas)
        except Exception as ex:
            messagebox.showerror("Error en diagnóstico", str(ex))
            return

        self._hist_lbl.config(
            text=f"Historial: {self.service.historial_count()} diagnóstico(s)")

        vista = self.controller.frames[DiagnosisView]
        vista.mostrar_resultados(paquete)
        self.controller.show_frame(DiagnosisView)

    def limpiar_formulario(self):
        self._nombre_entry.delete(0, "end")
        self._alergias_entry.delete(0, "end")
        for v in self._sintoma_vars.values():
            v.set(False)
        for v in self._severidad_vars.values():
            v.set("moderado")
        for v in self._cronicas_vars.values():
            v.set(False)