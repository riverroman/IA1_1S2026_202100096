import tkinter as tk
from tkinter import filedialog, messagebox
from services.rpa_service import RPAService
from ui.theme import COLORS, FONTS

def styled_button(parent, text, command, secondary=False, full_width=False):
    bg = COLORS["bg_input"] if secondary else COLORS["accent"]
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

    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


class AdminView(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.controller = controller
        self.rpa = RPAService()
        self.build_ui()

    def build_ui(self):

        # ── Barra lateral ─────────────────────────────────────────────
        sidebar = tk.Frame(self, bg=COLORS["bg_card"], width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Frame(sidebar, bg=COLORS["warning"], height=4).pack(fill="x")

        logo_frame = tk.Frame(sidebar, bg=COLORS["bg_card"])
        logo_frame.pack(pady=(40, 10))

        tk.Label(logo_frame, text="Medi", font=FONTS["logo"],
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")
        tk.Label(logo_frame, text="Logic", font=FONTS["logo"],
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(side="left")

        tk.Label(
            sidebar,
            text="Sistema de Diagnóstico\nMédico Inteligente",
            font=("Helvetica", 10),
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            justify="center",
        ).pack(pady=(0, 40))

        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=30)

        tk.Label(sidebar, text="MÓDULO ACTIVO", font=("Helvetica", 9, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["warning"]).pack(pady=(20, 4))

        tk.Label(sidebar, text="Administración RPA", font=FONTS["heading"],
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack()

        tk.Frame(sidebar, bg=COLORS["bg_card"]).pack(expand=True)

        styled_button(
            sidebar,
            text="← Volver al Inicio",
            command=lambda: self.controller.show_frame(
                __import__("ui.patient_view").patient_view.PatientView
            ),
            secondary=True,
        ).pack(pady=(0, 30), padx=30, fill="x")

        # ── Área principal ────────────────────────────────────────────
        main = tk.Frame(self, bg=COLORS["bg_dark"])
        main.pack(side="left", fill="both", expand=True, padx=60, pady=50)

        # Encabezado
        tk.Label(main, text="Panel de Administración", font=FONTS["title"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"]).pack(anchor="w")

        tk.Label(main, text="Gestión de archivos RPA y configuración del sistema",
                 font=FONTS["body_sm"], bg=COLORS["bg_dark"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 0))

        tk.Frame(main, bg=COLORS["warning"], height=2, width=60).pack(anchor="w", pady=(8, 30))

        # ── Card RPA ──────────────────────────────────────────────────
        card = tk.Frame(main, bg=COLORS["bg_card"], padx=40, pady=36)
        card.pack(fill="x")

        tk.Label(card, text="PROCESAMIENTO RPA", font=("Helvetica", 9, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 12))

        tk.Label(
            card,
            text="Cargue un archivo de texto (.txt) para procesar mediante\nel motor de automatización RPA del sistema.",
            font=FONTS["body_sm"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_secondary"],
            justify="left",
        ).pack(anchor="w", pady=(0, 20))

        # Estado del archivo
        self.status_frame = tk.Frame(card, bg=COLORS["bg_input"], padx=16, pady=12)
        self.status_frame.pack(fill="x", pady=(0, 20))

        self.status_icon = tk.Label(self.status_frame, text="○", font=("Helvetica", 14),
                                     bg=COLORS["bg_input"], fg=COLORS["text_muted"])
        self.status_icon.pack(side="left", padx=(0, 10))

        self.status_label = tk.Label(self.status_frame, text="Ningún archivo seleccionado",
                                      font=FONTS["body_sm"], bg=COLORS["bg_input"],
                                      fg=COLORS["text_muted"])
        self.status_label.pack(side="left")

        styled_button(card, text="📂  Cargar Archivo RPA", command=self.cargar_archivo).pack(anchor="w")

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar Archivo RPA",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )

        if ruta:
            nombre = ruta.split("/")[-1]
            self.status_icon.config(text="●", fg=COLORS["accent"])
            self.status_label.config(text=f"{nombre}", fg=COLORS["text_primary"])

            try:
                self.rpa.procesar_archivo(ruta)
                messagebox.showinfo("Éxito", f"Archivo procesado correctamente:\n{nombre}")
            except Exception as ex:
                self.status_icon.config(text="✕", fg=COLORS["danger"])
                self.status_label.config(text=f"Error al procesar: {nombre}", fg=COLORS["danger"])
                messagebox.showerror("Error RPA", str(ex))