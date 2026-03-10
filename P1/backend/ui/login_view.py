import tkinter as tk
from tkinter import messagebox
from ui.admin_view import AdminView
from ui.theme import COLORS, FONTS, PAD


def styled_entry(parent, **kwargs):
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
        **kwargs,
    )
    return e


def styled_button(parent, text, command, secondary=False):
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

    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


class LoginView(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.controller = controller
        self.build_ui()

    def build_ui(self):

        # Centra el card verticalmente
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        wrapper = tk.Frame(self, bg=COLORS["bg_dark"])
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        # ── Logo ──────────────────────────────────────────────────────
        logo_row = tk.Frame(wrapper, bg=COLORS["bg_dark"])
        logo_row.pack(pady=(0, 6))

        tk.Label(logo_row, text="Medi", font=FONTS["logo"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"]).pack(side="left")
        tk.Label(logo_row, text="Logic", font=FONTS["logo"],
                 bg=COLORS["bg_dark"], fg=COLORS["accent"]).pack(side="left")

        tk.Label(
            wrapper,
            text="Acceso Restringido — Panel de Administración",
            font=FONTS["body_sm"],
            bg=COLORS["bg_dark"],
            fg=COLORS["text_muted"],
        ).pack(pady=(0, 30))

        # ── Card ──────────────────────────────────────────────────────
        card = tk.Frame(wrapper, bg=COLORS["bg_card"], padx=50, pady=44)
        card.pack(ipadx=0)

        # Línea accent en la parte superior
        tk.Frame(card, bg=COLORS["accent"], height=3).pack(fill="x", pady=(0, 30))

        tk.Label(
            card,
            text="Iniciar Sesión",
            font=FONTS["subtitle"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 24))

        # Campo usuario
        tk.Label(card, text="USUARIO", font=("Helvetica", 9, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 6))

        self.user = styled_entry(card, width=36)
        self.user.pack(fill="x", ipady=10)

        tk.Frame(card, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 20))

        # Campo contraseña
        tk.Label(card, text="CONTRASEÑA", font=("Helvetica", 9, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 6))

        self.password = styled_entry(card, show="●", width=36)
        self.password.pack(fill="x", ipady=10)

        tk.Frame(card, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 30))

        # Botones
        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x")

        styled_button(btn_row, text="Ingresar", command=self.login).pack(
            side="left", fill="x", expand=True
        )

        tk.Frame(btn_row, bg=COLORS["bg_card"], width=12).pack(side="left")

        styled_button(
            btn_row,
            text="Cancelar",
            command=lambda: self.controller.show_frame(
                __import__("ui.patient_view").patient_view.PatientView
            ),
            secondary=True,
        ).pack(side="left", fill="x", expand=True)

        # Bind Enter key
        self.password.bind("<Return>", lambda e: self.login())
        self.user.bind("<Return>", lambda e: self.password.focus())

    def login(self):
        if self.user.get() == "admin" and self.password.get() == "admin123":
            self.controller.show_frame(AdminView)
        else:
            messagebox.showerror("Acceso Denegado", "Credenciales incorrectas.\nVerifique usuario y contraseña.")