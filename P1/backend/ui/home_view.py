import tkinter as tk
from ui.theme import COLORS, FONTS

def styled_button_large(parent, text, subtitle, command, accent_color=None):
    """Botón grande tipo card con título y subtítulo."""
    color = accent_color or COLORS["accent"]
    hover_bg = "#1A3050"

    frame = tk.Frame(
        parent,
        bg=COLORS["bg_card"],
        cursor="hand2",
        padx=30,
        pady=24,
    )

    top_bar = tk.Frame(frame, bg=color, height=3)
    top_bar.pack(fill="x", pady=(0, 16))

    tk.Label(
        frame,
        text=text,
        font=("Georgia", 14, "bold"),
        bg=COLORS["bg_card"],
        fg=COLORS["text_primary"],
        anchor="w",
    ).pack(fill="x")

    tk.Label(
        frame,
        text=subtitle,
        font=FONTS["body_sm"],
        bg=COLORS["bg_card"],
        fg=COLORS["text_secondary"],
        anchor="w",
        wraplength=280,
        justify="left",
    ).pack(fill="x", pady=(6, 0))

    arrow = tk.Label(
        frame,
        text="→",
        font=("Georgia", 18),
        bg=COLORS["bg_card"],
        fg=color,
    )
    arrow.pack(anchor="e", pady=(10, 0))

    # Hover effects en todos los hijos
    def on_enter(e):
        frame.config(bg=hover_bg)
        for w in frame.winfo_children():
            try:
                if isinstance(w, tk.Frame):
                    continue
                w.config(bg=hover_bg)
            except Exception:
                pass

    def on_leave(e):
        frame.config(bg=COLORS["bg_card"])
        for w in frame.winfo_children():
            try:
                if isinstance(w, tk.Frame):
                    continue
                w.config(bg=COLORS["bg_card"])
            except Exception:
                pass

    frame.bind("<Button-1>", lambda e: command())
    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)

    for child in frame.winfo_children():
        child.bind("<Button-1>", lambda e: command())
        child.bind("<Enter>", on_enter)
        child.bind("<Leave>", on_leave)

    return frame


class HomeView(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.controller = controller
        self.build_ui()

    def build_ui(self):

        # ── Layout principal: izquierda (hero) + derecha (acciones) ──
        left = tk.Frame(self, bg=COLORS["bg_dark"])
        left.pack(side="left", fill="both", expand=True, padx=(70, 40), pady=60)

        right = tk.Frame(self, bg=COLORS["bg_card"], width=380)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        # ── Panel derecho ─────────────────────────────────────────────
        tk.Frame(right, bg=COLORS["accent"], height=4).pack(fill="x")

        right_inner = tk.Frame(right, bg=COLORS["bg_card"])
        right_inner.pack(fill="both", expand=True, padx=30, pady=40)

        tk.Label(
            right_inner,
            text="Acceder al sistema",
            font=("Georgia", 13, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            right_inner,
            text="Selecciona el módulo al que\ndeseas ingresar",
            font=FONTS["body_sm"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            justify="left",
        ).pack(anchor="w", pady=(0, 30))

        # Card — Módulo Paciente
        btn_paciente = styled_button_large(
            right_inner,
            text="Módulo Paciente",
            subtitle="Ingresa tus síntomas y obtén un diagnóstico preliminar de forma rápida y privada.",
            command=lambda: self.controller.show_frame(
                __import__("ui.patient_view").patient_view.PatientView
            ),
            accent_color=COLORS["accent"],
        )
        btn_paciente.pack(fill="x", pady=(0, 16))

        # Card — Módulo Admin
        btn_admin = styled_button_large(
            right_inner,
            text="Panel Administrativo",
            subtitle="Acceso restringido para personal médico autorizado. Requiere credenciales.",
            command=lambda: self.controller.show_frame(
                __import__("ui.login_view").login_view.LoginView
            ),
            accent_color=COLORS["warning"],
        )
        btn_admin.pack(fill="x")

        # Aviso legal
        tk.Frame(right_inner, bg=COLORS["border"], height=1).pack(fill="x", pady=(30, 16))

        tk.Label(
            right_inner,
            text="⚠  Esta herramienta es de apoyo diagnóstico\npreliminar y no sustituye la consulta médica.",
            font=("Helvetica", 9),
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            justify="left",
        ).pack(anchor="w")

        # ── Panel izquierdo / Hero ────────────────────────────────────

        # Logo
        logo_row = tk.Frame(left, bg=COLORS["bg_dark"])
        logo_row.pack(anchor="w", pady=(0, 8))

        tk.Label(
            logo_row, text="Medi",
            font=("Georgia", 42, "bold"),
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
        ).pack(side="left")
        tk.Label(
            logo_row, text="Logic",
            font=("Georgia", 42, "bold"),
            bg=COLORS["bg_dark"],
            fg=COLORS["accent"],
        ).pack(side="left")

        # Tagline
        tk.Label(
            left,
            text="Sistema de Apoyo Diagnóstico Médico",
            font=("Georgia", 14, "italic"),
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
        ).pack(anchor="w", pady=(0, 30))

        # Línea decorativa
        tk.Frame(left, bg=COLORS["accent"], height=2, width=80).pack(anchor="w", pady=(0, 36))

        # Descripción principal
        tk.Label(
            left,
            text="Diagnóstico preliminar\nbasado en inteligencia artificial.",
            font=("Georgia", 22, "bold"),
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
            justify="left",
        ).pack(anchor="w", pady=(0, 20))

        description = (
            "MediLogic analiza los síntomas reportados por el paciente y genera "
            "un listado de posibles diagnósticos con su nivel de afinidad y urgencia, "
            "utilizando un motor de inferencia médica basado en reglas clínicas.\n\n"
            "Esta herramienta está diseñada como apoyo para la toma de decisiones "
            "preliminares y no reemplaza la evaluación de un profesional de la salud."
        )

        tk.Label(
            left,
            text=description,
            font=FONTS["body"],
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
            justify="left",
            wraplength=520,
        ).pack(anchor="w", pady=(0, 40))

        # Features / pills
        features_frame = tk.Frame(left, bg=COLORS["bg_dark"])
        features_frame.pack(anchor="w")

        features = [
            ("", "Diagnóstico inmediato"),
            ("", "Sin registro requerido"),
            ("", "Gestión RPA integrada"),
        ]

        for icon, label in features:
            pill = tk.Frame(features_frame, bg=COLORS["bg_card"], padx=14, pady=8)
            pill.pack(side="left", padx=(0, 12))

            tk.Label(pill, text=f"{icon}  {label}",
                     font=FONTS["body_sm"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["text_secondary"]).pack()

        # Versión
        tk.Label(
            left,
            text="v1.0  —  IA1 · 1S2026",
            font=("Helvetica", 9),
            bg=COLORS["bg_dark"],
            fg=COLORS["text_muted"],
        ).pack(anchor="w", pady=(40, 0))