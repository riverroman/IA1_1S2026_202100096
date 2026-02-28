import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from services.diagnostic_service import DiagnosticService
from services.rpa_service import RPAService

BG_DARK      = "#0D1B2A"   
BG_CARD      = "#132035"   
BG_ENTRY     = "#1A2A3F"   
ACCENT_TEAL  = "#00C9A7"   
ACCENT_BLUE  = "#3A7BD5" 
TEXT_PRIMARY = "#E8F4F8"  
TEXT_MUTED   = "#7A9BB5"   
BORDER_COLOR = "#1E3A5F"   
DANGER       = "#FF6B6B"   
WARNING      = "#FFD166" 

class StyledEntry(tk.Frame):
    def __init__(self, master, placeholder="", width=30, **kw):
        super().__init__(master, bg=BORDER_COLOR, padx=1, pady=1)
        self.entry = tk.Entry(
            self,
            bg=BG_ENTRY,
            fg=TEXT_PRIMARY,
            insertbackground=ACCENT_TEAL,
            relief="flat",
            font=("Courier New", 11),
            width=width,
            highlightthickness=0,
            **kw,
        )
        self.entry.pack()
        self._placeholder = placeholder
        self._set_placeholder()
        self.entry.bind("<FocusIn>",  self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<FocusIn>",  lambda e: self.config(bg=ACCENT_TEAL), add="+")
        self.entry.bind("<FocusOut>", lambda e: self.config(bg=BORDER_COLOR), add="+")

    def _set_placeholder(self):
        self.entry.insert(0, self._placeholder)
        self.entry.config(fg=TEXT_MUTED)

    def _on_focus_in(self, _):
        if self.entry.get() == self._placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=TEXT_PRIMARY)

    def _on_focus_out(self, _):
        if not self.entry.get():
            self._set_placeholder()

    def get(self):
        val = self.entry.get()
        return "" if val == self._placeholder else val


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MediLogic")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)

        self.diagnostic_service = DiagnosticService()
        self.rpa_service = RPAService()

        self._build_ui()

    # ── Construcción de la UI ──────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_patient_card()
        self._build_result_area()
        self._build_footer()

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG_DARK, pady=18)
        header.pack(fill="x", padx=30)

        # Logo / marca
        logo_frame = tk.Frame(header, bg=BG_DARK)
        logo_frame.pack(side="left")

        tk.Label(
            logo_frame,
            text="✚",
            font=("Arial", 22, "bold"),
            fg=ACCENT_TEAL,
            bg=BG_DARK,
        ).pack(side="left", padx=(0, 8))

        tk.Label(
            logo_frame,
            text="MediLogic",
            font=("Georgia", 22, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_DARK,
        ).pack(side="left")

        tk.Label(
            logo_frame,
            text="  Sistema de Diagnóstico",
            font=("Courier New", 10),
            fg=TEXT_MUTED,
            bg=BG_DARK,
        ).pack(side="left", padx=(4, 0))

        # Línea separadora
        sep = tk.Frame(self.root, bg=BORDER_COLOR, height=1)
        sep.pack(fill="x", padx=30)

    def _build_patient_card(self):
        card = tk.Frame(self.root, bg=BG_CARD, bd=0, relief="flat")
        card.pack(fill="x", padx=30, pady=(20, 10))

        # Encabezado de tarjeta
        card_header = tk.Frame(card, bg=ACCENT_TEAL)
        card_header.pack(fill="x")
        tk.Label(
            card_header,
            text="  MÓDULO PACIENTE",
            font=("Courier New", 9, "bold"),
            fg=BG_DARK,
            bg=ACCENT_TEAL,
            pady=6,
            anchor="w",
        ).pack(fill="x", padx=10)

        # Cuerpo de tarjeta
        body = tk.Frame(card, bg=BG_CARD, padx=20, pady=16)
        body.pack(fill="x")

        # Fila 1 – Nombre
        self._label(body, "Nombre del paciente").grid(
            row=0, column=0, sticky="w", padx=(0, 16), pady=6)
        self.nombre_entry = StyledEntry(body, placeholder="Ej. Juan García", width=32)
        self.nombre_entry.grid(row=0, column=1, sticky="w", pady=6)

        # Fila 2 – Síntomas
        self._label(body, "Síntomas (separados por coma)").grid(
            row=1, column=0, sticky="w", padx=(0, 16), pady=6)
        self.sintomas_entry = StyledEntry(body, placeholder="fiebre, tos, fatiga", width=32)
        self.sintomas_entry.grid(row=1, column=1, sticky="w", pady=6)

        # Botón diagnosticar
        btn_frame = tk.Frame(card, bg=BG_CARD, pady=12)
        btn_frame.pack(fill="x", padx=20)
        self._accent_button(
            btn_frame,
            text="EJECUTAR DIAGNÓSTICO  →",
            command=self.realizar_diagnostico,
        ).pack(side="left")

    def _build_result_area(self):
        result_card = tk.Frame(self.root, bg=BG_CARD)
        result_card.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        card_header = tk.Frame(result_card, bg=ACCENT_BLUE)
        card_header.pack(fill="x")
        tk.Label(
            card_header,
            text="  RESULTADOS",
            font=("Courier New", 9, "bold"),
            fg=TEXT_PRIMARY,
            bg=ACCENT_BLUE,
            pady=6,
            anchor="w",
        ).pack(fill="x", padx=10)

        # Área de texto con scrollbar
        text_frame = tk.Frame(result_card, bg=BG_CARD, padx=12, pady=12)
        text_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, bg=BG_CARD, troughcolor=BG_DARK,
                                  activebackground=ACCENT_TEAL, relief="flat", bd=0)
        scrollbar.pack(side="right", fill="y")

        self.resultado = tk.Text(
            text_frame,
            height=12,
            bg=BG_ENTRY,
            fg=TEXT_PRIMARY,
            font=("Courier New", 11),
            relief="flat",
            insertbackground=ACCENT_TEAL,
            selectbackground=ACCENT_BLUE,
            wrap="word",
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=8,
        )
        self.resultado.pack(fill="both", expand=True)
        scrollbar.config(command=self.resultado.yview)

        # Tags para colorear salida
        self.resultado.tag_config("key",    foreground=TEXT_MUTED,   font=("Courier New", 10, "bold"))
        self.resultado.tag_config("value",  foreground=TEXT_PRIMARY, font=("Courier New", 11))
        self.resultado.tag_config("teal",   foreground=ACCENT_TEAL,  font=("Courier New", 12, "bold"))
        self.resultado.tag_config("warn",   foreground=WARNING)
        self.resultado.tag_config("danger", foreground=DANGER)
        self.resultado.tag_config("muted",  foreground=TEXT_MUTED)
        self.resultado.tag_config("sep",    foreground=BORDER_COLOR)

        # Mensaje inicial
        self.resultado.insert(tk.END, "  Ingrese los datos del paciente y ejecute el diagnóstico…\n", "muted")
        self.resultado.config(state="disabled")

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=BG_DARK, pady=10)
        footer.pack(fill="x", padx=30)

        sep = tk.Frame(self.root, bg=BORDER_COLOR, height=1)
        sep.pack(fill="x", padx=30)

        footer2 = tk.Frame(self.root, bg=BG_DARK, pady=10)
        footer2.pack(fill="x", padx=30)

        self._ghost_button(
            footer2,
            text="⬆  Cargar archivo RPA",
            command=self.cargar_archivo,
        ).pack(side="left")

        tk.Label(
            footer2,
            text="MediLogic v1.0  •  Diagnóstico Asistido",
            font=("Courier New", 8),
            fg=TEXT_MUTED,
            bg=BG_DARK,
        ).pack(side="right")

    # ── Helpers de widgets ─────────────────────────────────────────────────────

    def _label(self, parent, text):
        return tk.Label(
            parent,
            text=text,
            font=("Courier New", 10),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )

    def _accent_button(self, parent, text, command):
        btn = tk.Label(
            parent,
            text=text,
            font=("Courier New", 10, "bold"),
            fg=BG_DARK,
            bg=ACCENT_TEAL,
            padx=18,
            pady=8,
            cursor="hand2",
        )
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>",    lambda e: btn.config(bg="#00E5BF"))
        btn.bind("<Leave>",    lambda e: btn.config(bg=ACCENT_TEAL))
        return btn

    def _ghost_button(self, parent, text, command):
        btn = tk.Label(
            parent,
            text=text,
            font=("Courier New", 10),
            fg=ACCENT_BLUE,
            bg=BG_DARK,
            padx=10,
            pady=4,
            cursor="hand2",
        )
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>",    lambda e: btn.config(fg=ACCENT_TEAL))
        btn.bind("<Leave>",    lambda e: btn.config(fg=ACCENT_BLUE))
        return btn

    # ── Lógica de negocio ──────────────────────────────────────────────────────

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if ruta:
            self.rpa_service.procesar_archivo(ruta)
            messagebox.showinfo("Éxito", "Archivo procesado correctamente")

    def realizar_diagnostico(self):
        nombre = self.nombre_entry.get().strip()
        sintomas_input = self.sintomas_entry.get()

        sintomas = [
            s.strip().lower().replace(" ", "_")
            for s in sintomas_input.split(",")
            if s.strip()
        ]

        resultado = self.diagnostic_service.obtener_diagnostico(sintomas)

        self.resultado.config(state="normal")
        self.resultado.delete("1.0", tk.END)

        if resultado:
            for i, r in enumerate(resultado, 1):
                urgencia = r["U"]
                urgencia_tag = "danger" if urgencia == "Alta" else ("warn" if urgencia == "Media" else "teal")

                self.resultado.insert(tk.END, f"  ── Resultado {i} ", "sep")
                self.resultado.insert(tk.END, "─" * 42 + "\n", "sep")
                self.resultado.insert(tk.END, "  Paciente   : ", "key")
                self.resultado.insert(tk.END, f"{nombre}\n", "value")
                self.resultado.insert(tk.END, "  Enfermedad : ", "key")
                self.resultado.insert(tk.END, f"{r['E']}\n", "teal")
                self.resultado.insert(tk.END, "  Afinidad   : ", "key")
                self.resultado.insert(tk.END, f"{r['P']}%\n", "value")
                self.resultado.insert(tk.END, "  Urgencia   : ", "key")
                self.resultado.insert(tk.END, f"{urgencia}\n\n", urgencia_tag)
        else:
            self.resultado.insert(tk.END, "\n  ✗  No se encontró diagnóstico para los síntomas indicados.\n", "muted")

        self.resultado.config(state="disabled")

    def run(self):
        self.root.mainloop()