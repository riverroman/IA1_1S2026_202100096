import tkinter as tk
from services.diagnostic_service import DiagnosticService
from ui.diagnosis_view import DiagnosisView
from ui.theme import COLORS, FONTS, PAD

def styled_entry(parent, **kwargs):
    """Campo de entrada con estilo refinado."""
    e = tk.Entry(
        parent,
        bg=COLORS["bg_input"],
        fg=COLORS["text_primary"],
        insertbackground=COLORS["accent"],
        relief="flat",
        font=FONTS["body"],
        bd=0,
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["accent"],
        **kwargs
    )
    return e

def styled_button(parent, text, command, secondary=False):
    """Botón con estilo refinado y efecto hover."""
    bg = COLORS["bg_card"] if secondary else COLORS["accent"]
    fg = COLORS["text_secondary"] if secondary else COLORS["bg_dark"]
    hover_bg = COLORS["border"] if secondary else COLORS["accent_hover"]

    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        font=FONTS["button"],
        relief="flat",
        bd=0,
        padx=24,
        pady=10,
        cursor="hand2",
        activebackground=hover_bg,
        activeforeground=fg,
    )

    def on_enter(e):
        btn.config(bg=hover_bg)

    def on_leave(e):
        btn.config(bg=bg)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


class PatientView(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.controller = controller
        self.service = DiagnosticService()
        self.build_ui()

    def build_ui(self):

        # ── Barra lateral izquierda con logo ──────────────────────────
        sidebar = tk.Frame(self, bg=COLORS["bg_card"], width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Frame(sidebar, bg=COLORS["accent"], height=4).pack(fill="x")

        logo_frame = tk.Frame(sidebar, bg=COLORS["bg_card"])
        logo_frame.pack(pady=(40, 10))

        tk.Label(
            logo_frame,
            text="Medi",
            font=FONTS["logo"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_primary"],
        ).pack(side="left")
        tk.Label(
            logo_frame,
            text="Logic",
            font=FONTS["logo"],
            bg=COLORS["bg_card"],
            fg=COLORS["accent"],
        ).pack(side="left")

        tk.Label(
            sidebar,
            text="Sistema de Diagnóstico\nMédico Inteligente",
            font=FONTS["body_sm"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            justify="center",
        ).pack(pady=(0, 40))

        # Separador decorativo
        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=30, pady=10)

        tk.Label(
            sidebar,
            text="MÓDULO ACTIVO",
            font=("Helvetica", 9, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["accent"],
        ).pack(pady=(20, 4))

        tk.Label(
            sidebar,
            text="Consulta de Paciente",
            font=FONTS["heading"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_primary"],
        ).pack()

        # Spacer
        tk.Frame(sidebar, bg=COLORS["bg_card"]).pack(expand=True)

        styled_button(
            sidebar,
            text="⚙  Panel Admin",
            command=lambda: self.controller.show_frame(
                __import__("ui.login_view").login_view.LoginView
            ),
            secondary=True,
        ).pack(pady=(0, 30), padx=30, fill="x")

        # ── Área principal ─────────────────────────────────────────────
        main = tk.Frame(self, bg=COLORS["bg_dark"])
        main.pack(side="left", fill="both", expand=True, padx=60, pady=50)

        # Encabezado
        header = tk.Frame(main, bg=COLORS["bg_dark"])
        header.pack(fill="x", pady=(0, 30))

        tk.Label(
            header,
            text="Nueva Consulta",
            font=FONTS["title"],
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Ingrese los datos del paciente para obtener un diagnóstico",
            font=FONTS["body_sm"],
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
        ).pack(anchor="w", pady=(4, 0))

        # Línea decorativa bajo header
        tk.Frame(main, bg=COLORS["accent"], height=2, width=60).pack(anchor="w", pady=(8, 30))

        # ── Formulario ────────────────────────────────────────────────
        card = tk.Frame(main, bg=COLORS["bg_card"], padx=40, pady=36)
        card.pack(fill="x")

        # Nombre
        tk.Label(
            card,
            text="NOMBRE DEL PACIENTE",
            font=("Helvetica", 9, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 6))

        self.nombre = styled_entry(card)
        self.nombre.pack(fill="x", ipady=10)

        tk.Frame(card, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 24))

        # Síntomas
        tk.Label(
            card,
            text="SÍNTOMAS  —  separados por coma",
            font=("Helvetica", 9, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 6))

        self.sintomas = styled_entry(card)
        self.sintomas.pack(fill="x", ipady=10)

        tk.Label(
            card,
            text="Ejemplo: fiebre, tos, dolor de cabeza",
            font=FONTS["body_sm"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

        # Botón diagnosticar
        btn_frame = tk.Frame(card, bg=COLORS["bg_card"])
        btn_frame.pack(fill="x", pady=(30, 0))

        styled_button(
            btn_frame,
            text="▶  Iniciar Diagnóstico",
            command=self.diagnosticar,
        ).pack(side="left")

    def diagnosticar(self):
        sintomas = [
            s.strip().lower().replace(" ", "_")
            for s in self.sintomas.get().split(",")
        ]
        resultado = self.service.obtener_diagnostico(sintomas)
        vista = self.controller.frames[DiagnosisView]
        vista.mostrar_resultados(resultado, self.nombre.get())
        self.controller.show_frame(DiagnosisView)