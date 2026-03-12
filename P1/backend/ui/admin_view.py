import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from ui.theme import COLORS, FONTS

def _btn(parent, text, command, secondary=False, danger=False, small=False):
    if danger:
        bg, fg, hbg = COLORS["danger"], "#fff", "#c0392b"
    elif secondary:
        bg, fg, hbg = COLORS["bg_input"], COLORS["text_secondary"], COLORS["border"]
    else:
        bg, fg, hbg = COLORS["accent"], COLORS["bg_dark"], COLORS["accent_hover"]
    pad_x = 12 if small else 20
    pad_y = 6  if small else 9
    b = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                  font=FONTS["button"], relief="flat", bd=0,
                  padx=pad_x, pady=pad_y, cursor="hand2",
                  activebackground=hbg, activeforeground=fg)
    b.bind("<Enter>", lambda e: b.config(bg=hbg))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def _entry(parent, width=None, show=None):
    kw = {}
    if width: kw["width"] = width
    if show:  kw["show"]  = show
    return tk.Entry(
        parent, bg=COLORS["bg_input"], fg=COLORS["text_primary"],
        insertbackground=COLORS["accent"], relief="flat",
        font=FONTS["body"], highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["accent"], **kw)


def _label(parent, text, muted=False, heading=False):
    fg = COLORS["text_muted"] if muted else COLORS["text_primary"]
    fnt = FONTS["heading"] if heading else FONTS["body_sm"]
    return tk.Label(parent, text=text, bg=COLORS["bg_card"], fg=fg, font=fnt)


class AdminView(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.controller     = controller
        from services.prolog_service import PrologService
        self.prolog         = PrologService()
        self._tab_actual    = tk.StringVar(value="enfermedades")
        self._modo_edicion  = False
        self._enf_editando  = None
        self._rpa_corriendo = False
        self.build_ui()

    # ══════════════════════════════════════════════════════════════════
    def build_ui(self):
        sb = tk.Frame(self, bg=COLORS["bg_card"], width=220)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        tk.Frame(sb, bg=COLORS["accent"], height=4).pack(fill="x")

        lr = tk.Frame(sb, bg=COLORS["bg_card"])
        lr.pack(pady=(28, 4))
        tk.Label(lr, text="Medi", font=FONTS["logo"],
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")
        tk.Label(lr, text="Logic", font=FONTS["logo"],
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(side="left")
        tk.Label(sb, text="Panel Administrativo", font=FONTS["body_sm"],
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(pady=(0, 20))
        tk.Frame(sb, bg=COLORS["border"], height=1).pack(fill="x", padx=20)

        tabs = [
            ("Enfermedades", "enfermedades"),
            ("Medicamentos", "medicamentos"),
            ("Archivo .pl",  "archivo"),
            ("Robot RPA",    "rpa"),
        ]
        self._tab_btns = {}
        for label, key in tabs:
            b = tk.Button(
                sb, text=label, command=lambda k=key: self._cambiar_tab(k),
                bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                font=FONTS["body_sm"], relief="flat", bd=0,
                padx=20, pady=12, anchor="w", cursor="hand2",
                activebackground=COLORS["bg_input"],
                activeforeground=COLORS["text_primary"],
            )
            b.pack(fill="x", pady=1)
            self._tab_btns[key] = b

        tk.Frame(sb, bg=COLORS["bg_card"]).pack(expand=True)
        _btn(sb, "← Volver al Inicio",
             lambda: self.controller.show_frame(
                 __import__("ui.home_view").home_view.HomeView),
             secondary=True).pack(pady=(0, 10), padx=16, fill="x")
        _btn(sb, "Cerrar Sesión",
             lambda: self.controller.show_frame(
                 __import__("ui.login_view").login_view.LoginView),
             secondary=True).pack(pady=(0, 24), padx=16, fill="x")

        self._content = tk.Frame(self, bg=COLORS["bg_dark"])
        self._content.pack(side="left", fill="both", expand=True)

        self._tabs = {}
        self._tabs["enfermedades"] = self._build_tab_enfermedades()
        self._tabs["medicamentos"] = self._build_tab_medicamentos()
        self._tabs["archivo"]      = self._build_tab_archivo()
        self._tabs["rpa"]          = self._build_tab_rpa()

        self._cambiar_tab("enfermedades")

    def _cambiar_tab(self, key):
        self._tab_actual.set(key)
        for k, frame in self._tabs.items():
            frame.pack_forget()
        self._tabs[key].pack(fill="both", expand=True)
        for k, btn in self._tab_btns.items():
            activo = k == key
            btn.config(
                bg=COLORS["bg_input"] if activo else COLORS["bg_card"],
                fg=COLORS["accent"]   if activo else COLORS["text_secondary"],
            )
        if key == "enfermedades":
            self._refrescar_lista_enfermedades()
        elif key == "medicamentos":
            self._refrescar_lista_medicamentos()
            self._refrescar_combo_enf_med()
        elif key == "rpa":
            self._refrescar_config_email_display()

    # ══════════════════════════════════════════════════════════════════
    # PESTAÑA 1 — ENFERMEDADES
    # ══════════════════════════════════════════════════════════════════
    def _build_tab_enfermedades(self):
        frame = tk.Frame(self._content, bg=COLORS["bg_dark"])

        canvas = tk.Canvas(frame, bg=COLORS["bg_dark"], highlightthickness=0)
        vsb = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        inner = tk.Frame(canvas, bg=COLORS["bg_dark"])
        inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        PX = 40
        hdr = tk.Frame(inner, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=PX, pady=(36, 0))
        tk.Label(hdr, text="Gestión de Enfermedades", font=FONTS["title"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"]).pack(anchor="w")
        tk.Label(hdr, text="Crear, editar y eliminar enfermedades en la base de conocimiento",
                 font=FONTS["body_sm"], bg=COLORS["bg_dark"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 0))
        tk.Frame(hdr, bg=COLORS["accent"], height=2, width=60).pack(anchor="w", pady=(10, 0))

        form = tk.Frame(inner, bg=COLORS["bg_card"], padx=32, pady=24)
        form.pack(fill="x", padx=PX, pady=(20, 0))

        self._form_titulo_lbl = tk.Label(
            form, text="NUEVA ENFERMEDAD",
            font=("Helvetica", 9, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["accent"])
        self._form_titulo_lbl.pack(anchor="w", pady=(0, 14))

        r1 = tk.Frame(form, bg=COLORS["bg_card"])
        r1.pack(fill="x", pady=(0, 10))
        c1 = tk.Frame(r1, bg=COLORS["bg_card"])
        c1.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tk.Label(c1, text="Nombre (sin espacios, usar _)",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 4))
        self._enf_nombre = _entry(c1)
        self._enf_nombre.pack(fill="x", ipady=8)

        c2 = tk.Frame(r1, bg=COLORS["bg_card"])
        c2.pack(side="left", fill="x", expand=True)
        tk.Label(c2, text="Descripción",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 4))
        self._enf_desc = _entry(c2)
        self._enf_desc.pack(fill="x", ipady=8)

        r2 = tk.Frame(form, bg=COLORS["bg_card"])
        r2.pack(fill="x", pady=(0, 10))
        c3 = tk.Frame(r2, bg=COLORS["bg_card"])
        c3.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tk.Label(c3, text="Síntomas (separados por coma)",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 4))
        self._enf_sintomas = _entry(c3)
        self._enf_sintomas.pack(fill="x", ipady=8)
        tk.Label(c3, text="Ej: fiebre, tos, dolor_muscular",
                 font=FONTS["body_sm"], bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(2, 0))

        c4 = tk.Frame(r2, bg=COLORS["bg_card"])
        c4.pack(side="left", fill="x", expand=True)
        tk.Label(c4, text="Medicamentos contraindicados (coma)",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 4))
        self._enf_contra = _entry(c4)
        self._enf_contra.pack(fill="x", ipady=8)

        r3 = tk.Frame(form, bg=COLORS["bg_card"])
        r3.pack(fill="x", pady=(0, 14))
        tk.Label(r3, text="Clasificaciones (coma)  —  ej: respiratorio, viral, cronico",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 4))
        self._enf_clasif = _entry(r3)
        self._enf_clasif.pack(fill="x", ipady=8)

        self._bf_form = tk.Frame(form, bg=COLORS["bg_card"])
        self._bf_form.pack(fill="x")
        self._btn_crear = _btn(self._bf_form, "✚  Crear Enfermedad", self._crear_enfermedad)
        self._btn_crear.pack(side="left")
        tk.Frame(self._bf_form, bg=COLORS["bg_card"], width=10).pack(side="left")
        self._btn_actualizar = _btn(self._bf_form, "✎  Actualizar Enfermedad",
                                    self._actualizar_enfermedad)
        tk.Frame(self._bf_form, bg=COLORS["bg_card"], width=10).pack(side="left")
        _btn(self._bf_form, "↺  Nuevo / Limpiar",
             self._limpiar_form_enf, secondary=True).pack(side="left")

        tk.Label(inner, text="ENFERMEDADES REGISTRADAS",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_dark"],
                 fg=COLORS["text_muted"]).pack(anchor="w", padx=PX, pady=(28, 6))

        lista_frame = tk.Frame(inner, bg=COLORS["bg_card"])
        lista_frame.pack(fill="x", padx=PX, pady=(0, 40))

        cols = ("enfermedad", "descripcion", "sintomas", "clasificacion")
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Med.Treeview",
                        background=COLORS["bg_card"],
                        foreground=COLORS["text_primary"],
                        fieldbackground=COLORS["bg_card"],
                        rowheight=28, font=FONTS["body_sm"])
        style.configure("Med.Treeview.Heading",
                        background=COLORS["bg_input"],
                        foreground=COLORS["text_muted"],
                        font=("Helvetica", 9, "bold"))
        style.map("Med.Treeview",
                  background=[("selected", COLORS["accent"])],
                  foreground=[("selected", COLORS["bg_dark"])])

        self._tree_enf = ttk.Treeview(lista_frame, columns=cols,
                                       show="headings", style="Med.Treeview", height=10)
        for col, w, label in [
            ("enfermedad",    160, "Enfermedad"),
            ("descripcion",   280, "Descripción"),
            ("sintomas",      260, "Síntomas"),
            ("clasificacion", 160, "Clasificación"),
        ]:
            self._tree_enf.heading(col, text=label)
            self._tree_enf.column(col, width=w, minwidth=80)

        vsb2 = ttk.Scrollbar(lista_frame, orient="vertical", command=self._tree_enf.yview)
        self._tree_enf.configure(yscrollcommand=vsb2.set)
        self._tree_enf.pack(side="left", fill="x", expand=True)
        vsb2.pack(side="right", fill="y")

        acc = tk.Frame(inner, bg=COLORS["bg_dark"])
        acc.pack(fill="x", padx=PX, pady=(6, 0))
        _btn(acc, "✎  Cargar al formulario para editar",
             self._cargar_enf_seleccionada, secondary=True, small=True).pack(side="left")
        tk.Frame(acc, bg=COLORS["bg_dark"], width=8).pack(side="left")
        _btn(acc, "🗑  Eliminar seleccionado",
             self._eliminar_enf_seleccionada, danger=True, small=True).pack(side="left")

        return frame

    def _refrescar_lista_enfermedades(self):
        for row in self._tree_enf.get_children():
            self._tree_enf.delete(row)
        try:
            for e in self.prolog.obtener_todas_enfermedades():
                sint  = ", ".join(self.prolog.obtener_sintomas_enfermedad(e))
                clasf = ", ".join(str(c) for c in self.prolog.obtener_clasificaciones(e))
                desc  = self.prolog.obtener_descripcion(e)
                self._tree_enf.insert("", "end", values=(e, desc, sint, clasf))
        except Exception as ex:
            print(f"[admin] error refrescar enfermedades: {ex}")

    def _crear_enfermedad(self):
        nombre = self._enf_nombre.get().strip().lower().replace(" ", "_")
        desc   = self._enf_desc.get().strip()
        if not nombre:
            messagebox.showwarning("Campo vacío", "El nombre de la enfermedad es requerido.")
            return
        sint   = [s.strip().lower().replace(" ", "_") for s in self._enf_sintomas.get().split(",") if s.strip()]
        contra = [c.strip().lower().replace(" ", "_") for c in self._enf_contra.get().split(",") if c.strip()]
        clasif = [cl.strip().lower().replace(" ", "_") for cl in self._enf_clasif.get().split(",") if cl.strip()]
        try:
            self.prolog.agregar_enfermedad(nombre, desc, sint, contra, clasif)
            self._persistir_pl()
            self._refrescar_lista_enfermedades()
            self._limpiar_form_enf()
            messagebox.showinfo("Éxito", f"Enfermedad '{nombre}' creada correctamente.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _cargar_enf_seleccionada(self):
        sel = self._tree_enf.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona una enfermedad de la lista.")
            return
        vals = self._tree_enf.item(sel[0], "values")
        enf  = vals[0]
        sint   = ", ".join(self.prolog.obtener_sintomas_enfermedad(enf))
        contra = ", ".join(str(c) for c in self.prolog.obtener_contraindicados(enf))
        clasif = ", ".join(str(c) for c in self.prolog.obtener_clasificaciones(enf))
        for e in [self._enf_nombre, self._enf_desc, self._enf_sintomas,
                  self._enf_contra, self._enf_clasif]:
            e.delete(0, "end")
        self._enf_nombre.insert(0, enf)
        self._enf_desc.insert(0, vals[1])
        self._enf_sintomas.insert(0, sint)
        self._enf_contra.insert(0, contra)
        self._enf_clasif.insert(0, clasif)
        self._modo_edicion = True
        self._enf_editando = enf
        self._form_titulo_lbl.config(text=f"EDITANDO: {enf.upper()}", fg="#f39c12")
        self._btn_crear.pack_forget()
        self._btn_actualizar.pack(side="left")

    def _actualizar_enfermedad(self):
        if not self._enf_editando:
            return
        nombre_nuevo = self._enf_nombre.get().strip().lower().replace(" ", "_")
        desc   = self._enf_desc.get().strip()
        sint   = [s.strip().lower().replace(" ", "_") for s in self._enf_sintomas.get().split(",") if s.strip()]
        contra = [c.strip().lower().replace(" ", "_") for c in self._enf_contra.get().split(",") if c.strip()]
        clasif = [cl.strip().lower().replace(" ", "_") for cl in self._enf_clasif.get().split(",") if cl.strip()]
        if not nombre_nuevo:
            messagebox.showwarning("Campo vacío", "El nombre no puede estar vacío.")
            return
        try:
            self.prolog.eliminar_enfermedad(self._enf_editando)
            self.prolog.agregar_enfermedad(nombre_nuevo, desc, sint, contra, clasif)
            self._persistir_pl()
            self._refrescar_lista_enfermedades()
            self._limpiar_form_enf()
            messagebox.showinfo("Actualizada", f"Enfermedad '{nombre_nuevo}' actualizada correctamente.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _eliminar_enf_seleccionada(self):
        sel = self._tree_enf.selection()
        if not sel:
            return
        enf = self._tree_enf.item(sel[0], "values")[0]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar la enfermedad '{enf}' y todos sus hechos?"):
            return
        try:
            self.prolog.eliminar_enfermedad(enf)
            self._persistir_pl()
            self._refrescar_lista_enfermedades()
            messagebox.showinfo("Eliminada", f"'{enf}' eliminada correctamente.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _limpiar_form_enf(self):
        for e in [self._enf_nombre, self._enf_desc, self._enf_sintomas,
                  self._enf_contra, self._enf_clasif]:
            e.delete(0, "end")
        self._modo_edicion = False
        self._enf_editando = None
        self._form_titulo_lbl.config(text="NUEVA ENFERMEDAD", fg=COLORS["accent"])
        self._btn_actualizar.pack_forget()
        self._btn_crear.pack(side="left")

    # ══════════════════════════════════════════════════════════════════
    # PESTAÑA 2 — MEDICAMENTOS
    # ══════════════════════════════════════════════════════════════════
    def _build_tab_medicamentos(self):
        frame = tk.Frame(self._content, bg=COLORS["bg_dark"])
        canvas = tk.Canvas(frame, bg=COLORS["bg_dark"], highlightthickness=0)
        vsb = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        inner = tk.Frame(canvas, bg=COLORS["bg_dark"])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        PX = 40

        hdr = tk.Frame(inner, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=PX, pady=(36, 0))
        tk.Label(hdr, text="Gestión de Medicamentos", font=FONTS["title"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"]).pack(anchor="w")
        tk.Label(hdr, text="Asocia medicamentos a enfermedades — se guardan como trata(Med, Enf) en el .pl",
                 font=FONTS["body_sm"], bg=COLORS["bg_dark"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 0))
        tk.Frame(hdr, bg=COLORS["accent"], height=2, width=60).pack(anchor="w", pady=(10, 0))

        form = tk.Frame(inner, bg=COLORS["bg_card"], padx=32, pady=24)
        form.pack(fill="x", padx=PX, pady=(20, 0))
        tk.Label(form, text="ASOCIAR MEDICAMENTO A ENFERMEDAD",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_card"],
                 fg=COLORS["accent"]).pack(anchor="w", pady=(0, 16))

        r1 = tk.Frame(form, bg=COLORS["bg_card"])
        r1.pack(fill="x", pady=(0, 12))
        c1 = tk.Frame(r1, bg=COLORS["bg_card"])
        c1.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tk.Label(c1, text="Nombre del medicamento",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 4))
        self._med_nombre = _entry(c1)
        self._med_nombre.pack(fill="x", ipady=8)
        tk.Label(c1, text="Ej: paracetamol, amoxicilina, metformina",
                 font=FONTS["body_sm"], bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(2, 0))

        c2 = tk.Frame(r1, bg=COLORS["bg_card"])
        c2.pack(side="left", fill="x", expand=True)
        tk.Label(c2, text="Enfermedad que trata",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 4))
        self._med_enf_var = tk.StringVar()
        self._med_enf_combo = ttk.Combobox(c2, textvariable=self._med_enf_var,
                                            font=FONTS["body_sm"], state="readonly")
        self._med_enf_combo.pack(fill="x", ipady=6)

        bf = tk.Frame(form, bg=COLORS["bg_card"])
        bf.pack(fill="x", pady=(16, 0))
        _btn(bf, "✚  Asociar Medicamento", self._crear_medicamento).pack(side="left")
        tk.Frame(bf, bg=COLORS["bg_card"], width=10).pack(side="left")
        _btn(bf, "⟳  Recargar enfermedades",
             self._refrescar_combo_enf_med, secondary=True, small=True).pack(side="left")

        tk.Frame(inner, bg=COLORS["border"], height=1).pack(fill="x", padx=PX, pady=(24, 0))
        tk.Label(inner, text="MEDICAMENTOS REGISTRADOS (trata/2)",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_dark"],
                 fg=COLORS["text_muted"]).pack(anchor="w", padx=PX, pady=(16, 6))

        lista_frame = tk.Frame(inner, bg=COLORS["bg_card"])
        lista_frame.pack(fill="x", padx=PX)
        cols = ("medicamento", "enfermedad")
        self._tree_med = ttk.Treeview(lista_frame, columns=cols,
                                       show="headings", style="Med.Treeview", height=10)
        self._tree_med.heading("medicamento", text="Medicamento")
        self._tree_med.heading("enfermedad",  text="Trata Enfermedad")
        self._tree_med.column("medicamento", width=240)
        self._tree_med.column("enfermedad",  width=300)
        vsb3 = ttk.Scrollbar(lista_frame, orient="vertical", command=self._tree_med.yview)
        self._tree_med.configure(yscrollcommand=vsb3.set)
        self._tree_med.pack(side="left", fill="x", expand=True)
        vsb3.pack(side="right", fill="y")

        acc = tk.Frame(inner, bg=COLORS["bg_dark"])
        acc.pack(fill="x", padx=PX, pady=(8, 40))
        _btn(acc, "🗑  Eliminar asociación seleccionada",
             self._eliminar_med_seleccionado, danger=True, small=True).pack(side="left")
        return frame

    def _refrescar_combo_enf_med(self):
        try:
            enfs = self.prolog.obtener_todas_enfermedades()
            self._med_enf_combo["values"] = enfs
            if enfs: self._med_enf_combo.current(0)
        except Exception: pass

    def _refrescar_lista_medicamentos(self):
        for row in self._tree_med.get_children():
            self._tree_med.delete(row)
        try:
            for r in self.prolog.query("trata(M, E)"):
                self._tree_med.insert("", "end", values=(str(r["M"]), str(r["E"])))
        except Exception as ex:
            print(f"[admin] error refrescar meds: {ex}")

    def _crear_medicamento(self):
        med = self._med_nombre.get().strip().lower().replace(" ", "_")
        enf = self._med_enf_var.get().strip()
        if not med or not enf:
            messagebox.showwarning("Campos vacíos", "Debes ingresar medicamento y seleccionar enfermedad.")
            return
        try:
            self.prolog.agregar_trata(med, enf)
            self._persistir_pl()
            self._refrescar_lista_medicamentos()
            self._med_nombre.delete(0, "end")
            messagebox.showinfo("Éxito", f"'{med}' asociado a '{enf}'.\ntrata({med}, {enf}) guardado en .pl")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _eliminar_med_seleccionado(self):
        sel = self._tree_med.selection()
        if not sel: return
        vals = self._tree_med.item(sel[0], "values")
        med, enf = vals[0], vals[1]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar trata({med}, {enf})?"):
            return
        try:
            self.prolog.eliminar_trata(med, enf)
            self._persistir_pl()
            self._refrescar_lista_medicamentos()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    # ══════════════════════════════════════════════════════════════════
    # PESTAÑA 3 — ARCHIVO .pl
    # ══════════════════════════════════════════════════════════════════
    def _build_tab_archivo(self):
        frame = tk.Frame(self._content, bg=COLORS["bg_dark"])
        PX = 40
        hdr = tk.Frame(frame, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=PX, pady=(36, 0))
        tk.Label(hdr, text="Gestión del Archivo .pl", font=FONTS["title"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"]).pack(anchor="w")
        tk.Label(hdr, text="Visualiza, exporta o carga un archivo Prolog completo",
                 font=FONTS["body_sm"], bg=COLORS["bg_dark"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 0))
        tk.Frame(hdr, bg=COLORS["accent"], height=2, width=60).pack(anchor="w", pady=(10, 0))

        acc = tk.Frame(frame, bg=COLORS["bg_dark"])
        acc.pack(fill="x", padx=PX, pady=(20, 10))
        _btn(acc, "Ver .pl actual",   self._ver_pl_actual).pack(side="left")
        tk.Frame(acc, bg=COLORS["bg_dark"], width=10).pack(side="left")
        _btn(acc, "Exportar .pl",     self._exportar_pl,  secondary=True).pack(side="left")
        tk.Frame(acc, bg=COLORS["bg_dark"], width=10).pack(side="left")
        _btn(acc, "Cargar nuevo .pl", self._cargar_pl,    secondary=True).pack(side="left")

        viewer_frame = tk.Frame(frame, bg=COLORS["bg_card"])
        viewer_frame.pack(fill="both", expand=True, padx=PX, pady=(0, 40))
        self._pl_text = tk.Text(viewer_frame, bg=COLORS["bg_input"], fg=COLORS["text_primary"],
            font=("Courier", 10), relief="flat", padx=16, pady=16,
            insertbackground=COLORS["accent"], state="disabled", wrap="none")
        hsb = tk.Scrollbar(viewer_frame, orient="horizontal", command=self._pl_text.xview)
        vsb = tk.Scrollbar(viewer_frame, orient="vertical",   command=self._pl_text.yview)
        self._pl_text.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._pl_text.pack(fill="both", expand=True)
        return frame

    def _ver_pl_actual(self):
        from config import PROLOG_FILE
        try:
            with open(PROLOG_FILE, "r", encoding="utf-8") as f:
                contenido = f.read()
            self._pl_text.config(state="normal")
            self._pl_text.delete("1.0", "end")
            self._pl_text.insert("1.0", contenido)
            self._pl_text.config(state="disabled")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _exportar_pl(self):
        from config import PROLOG_FILE
        destino = filedialog.asksaveasfilename(defaultextension=".pl",
            filetypes=[("Prolog files", "*.pl"), ("All files", "*.*")],
            initialfile="knowledge_base_export.pl", title="Exportar archivo .pl")
        if not destino: return
        try:
            with open(PROLOG_FILE, "r", encoding="utf-8") as f: contenido = f.read()
            with open(destino, "w", encoding="utf-8") as f: f.write(contenido)
            messagebox.showinfo("Exportado", f"Archivo guardado en:\n{destino}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _cargar_pl(self):
        origen = filedialog.askopenfilename(
            filetypes=[("Prolog files", "*.pl"), ("All files", "*.*")],
            title="Cargar archivo .pl")
        if not origen: return
        if not messagebox.askyesno("Confirmar",
                "¿Reemplazar el .pl actual?\nEl motor Prolog se recargará automáticamente."): return
        from config import PROLOG_FILE
        import shutil
        try:
            shutil.copy2(origen, PROLOG_FILE)
            self.prolog.reload()
            messagebox.showinfo("Cargado", "Archivo .pl reemplazado y motor Prolog recargado.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    # ══════════════════════════════════════════════════════════════════
    # PESTAÑA 4 — ROBOT RPA
    # ══════════════════════════════════════════════════════════════════
    def _build_tab_rpa(self):
        frame = tk.Frame(self._content, bg=COLORS["bg_dark"])

        canvas = tk.Canvas(frame, bg=COLORS["bg_dark"], highlightthickness=0)
        vsb = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        inner = tk.Frame(canvas, bg=COLORS["bg_dark"])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        PX = 40

        # ── Header ────────────────────────────────────────────────────
        hdr = tk.Frame(inner, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=PX, pady=(36, 0))
        tk.Label(hdr, text="Robot RPA — Carga Automática", font=FONTS["title"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"]).pack(anchor="w")
        tk.Label(hdr, text="Configura y ejecuta el robot para cargar enfermedades desde un archivo TXT",
                 font=FONTS["body_sm"], bg=COLORS["bg_dark"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 0))
        tk.Frame(hdr, bg=COLORS["accent"], height=2, width=60).pack(anchor="w", pady=(10, 0))

        # ── Sección 1: Archivo TXT ────────────────────────────────────
        tk.Label(inner, text="① ARCHIVO DE ENTRADA",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_dark"],
                 fg=COLORS["text_muted"]).pack(anchor="w", padx=PX, pady=(24, 6))

        card_txt = tk.Frame(inner, bg=COLORS["bg_card"], padx=32, pady=20)
        card_txt.pack(fill="x", padx=PX)

        tk.Label(card_txt, text="Ruta del archivo TXT (ArchivoRPA.txt)",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 6))

        fila_txt = tk.Frame(card_txt, bg=COLORS["bg_card"])
        fila_txt.pack(fill="x")
        self._rpa_txt_entry = _entry(fila_txt)
        self._rpa_txt_entry.pack(side="left", fill="x", expand=True, ipady=8)
        ruta_default = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "ArchivoRPA.txt")
        self._rpa_txt_entry.insert(0, os.path.normpath(ruta_default))
        tk.Frame(fila_txt, bg=COLORS["bg_card"], width=8).pack(side="left")
        _btn(fila_txt, "Explorar", self._rpa_explorar_txt,
             secondary=True, small=True).pack(side="left")

        tk.Label(card_txt,
                 text="Formato esperado: NOMBRE;DESCRIPCION;[sint1,sint2];[contra1];[clasif1,clasif2]",
                 font=FONTS["body_sm"], bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(6, 0))

        # ── Sección 2: Configuración Email (solo lectura desde config.py) ──
        tk.Label(inner, text="② CONFIGURACIÓN DE EMAIL",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_dark"],
                 fg=COLORS["text_muted"]).pack(anchor="w", padx=PX, pady=(24, 6))

        card_email = tk.Frame(inner, bg=COLORS["bg_card"], padx=32, pady=20)
        card_email.pack(fill="x", padx=PX)

        # Cabecera con badge "config.py"
        email_hdr = tk.Frame(card_email, bg=COLORS["bg_card"])
        email_hdr.pack(fill="x", pady=(0, 12))
        tk.Label(email_hdr, text="Leída automáticamente desde ",
                 font=FONTS["body_sm"], bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(side="left")
        tk.Label(email_hdr, text="config.py",
                 font=("Courier", 9, "bold"), bg=COLORS["bg_input"],
                 fg=COLORS["accent"], padx=6, pady=2).pack(side="left")

        # Grid de valores actuales (solo lectura)
        grid = tk.Frame(card_email, bg=COLORS["bg_input"], padx=16, pady=12)
        grid.pack(fill="x")

        self._email_info_labels = {}
        campos = [
            ("smtp_host",    "SMTP Host"),
            ("smtp_port",    "Puerto"),
            ("usuario",      "Remitente"),
            ("destinatario", "Destinatario"),
        ]
        for i, (key, label) in enumerate(campos):
            tk.Label(grid, text=f"{label}:", font=("Helvetica", 9, "bold"),
                     bg=COLORS["bg_input"], fg=COLORS["text_muted"],
                     width=14, anchor="w").grid(row=i, column=0, sticky="w", pady=3)
            lbl = tk.Label(grid, text="—", font=("Courier", 9),
                           bg=COLORS["bg_input"], fg=COLORS["text_primary"], anchor="w")
            lbl.grid(row=i, column=1, sticky="w", padx=(8, 0), pady=3)
            self._email_info_labels[key] = lbl

        # Botón para abrir config.py en editor
        tk.Frame(card_email, bg=COLORS["bg_card"], height=10).pack()
        _btn(card_email, "Editar config.py",
             self._abrir_config_py, secondary=True, small=True).pack(anchor="w")

        # ── Sección 3: Instrucciones + Ejecutar ──────────────────────
        tk.Label(inner, text="③ EJECUTAR ROBOT",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_dark"],
                 fg=COLORS["text_muted"]).pack(anchor="w", padx=PX, pady=(24, 6))

        card_run = tk.Frame(inner, bg=COLORS["bg_card"], padx=32, pady=20)
        card_run.pack(fill="x", padx=PX)

        inst_frame = tk.Frame(card_run, bg=COLORS["bg_input"], padx=16, pady=12)
        inst_frame.pack(fill="x", pady=(0, 16))
        tk.Label(inst_frame, text="INSTRUCCIONES DE USO",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_input"],
                 fg=COLORS["accent"]).pack(anchor="w", pady=(0, 8))
        pasos = [
            "1. Asegúrate de que la pestaña 'Enfermedades' esté visible en esta misma ventana",
            "2. Verifica la ruta del archivo TXT arriba",
            "3. Presiona '▶ Iniciar Robot RPA'",
            "4. Cuando se indique, mueve el mouse al campo 'Nombre' del formulario (4 seg)",
            "5. Luego mueve el mouse al botón '✚ Crear Enfermedad' (4 seg)",
            "6. El robot llenará cada enfermedad automáticamente",
            "7. Al finalizar se generará un informe y se enviará por email (config.py)",
        ]
        for p in pasos:
            tk.Label(inst_frame, text=p, font=FONTS["body_sm"],
                     bg=COLORS["bg_input"], fg=COLORS["text_secondary"],
                     anchor="w").pack(anchor="w", pady=1)

        btn_row = tk.Frame(card_run, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(0, 16))
        self._btn_iniciar_rpa = _btn(btn_row, "▶  Iniciar Robot RPA", self._iniciar_rpa)
        self._btn_iniciar_rpa.pack(side="left")
        tk.Frame(btn_row, bg=COLORS["bg_card"], width=12).pack(side="left")
        _btn(btn_row, "Limpiar Log", self._limpiar_log_rpa,
             secondary=True, small=True).pack(side="left")

        self._rpa_status_lbl = tk.Label(card_run, text="⬤  Robot inactivo",
                                         font=("Helvetica", 9, "bold"),
                                         bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        self._rpa_status_lbl.pack(anchor="w", pady=(0, 10))

        # ── Sección 4: Log en tiempo real ─────────────────────────────
        tk.Label(inner, text="④ LOG EN TIEMPO REAL",
                 font=("Helvetica", 9, "bold"), bg=COLORS["bg_dark"],
                 fg=COLORS["text_muted"]).pack(anchor="w", padx=PX, pady=(24, 6))

        log_frame = tk.Frame(inner, bg=COLORS["bg_card"])
        log_frame.pack(fill="x", padx=PX, pady=(0, 40))

        self._rpa_log = tk.Text(
            log_frame, bg="#0d1117", fg="#58d68d",
            font=("Courier", 9), relief="flat", padx=12, pady=12,
            height=14, state="disabled", wrap="word",
            insertbackground=COLORS["accent"])
        log_vsb = tk.Scrollbar(log_frame, orient="vertical", command=self._rpa_log.yview)
        self._rpa_log.configure(yscrollcommand=log_vsb.set)
        self._rpa_log.pack(side="left", fill="both", expand=True)
        log_vsb.pack(side="right", fill="y")

        return frame

    def _refrescar_config_email_display(self):
        """Lee EMAIL_CONFIG de config.py y actualiza los labels de visualización."""
        try:
            from config import EMAIL_CONFIG
            mapping = {
                "smtp_host":    EMAIL_CONFIG.get("smtp_host", "—"),
                "smtp_port":    str(EMAIL_CONFIG.get("smtp_port", "—")),
                "usuario":      EMAIL_CONFIG.get("usuario", "—"),
                "destinatario": EMAIL_CONFIG.get("destinatario", "—"),
            }
            for key, lbl in self._email_info_labels.items():
                valor = mapping.get(key, "—")
                # Ocultar contraseña — no la mostramos
                lbl.config(text=valor if valor else "—")
        except Exception as ex:
            print(f"[admin] error leyendo EMAIL_CONFIG: {ex}")

    def _abrir_config_py(self):
        """Abre config.py en el editor por defecto del sistema."""
        import subprocess, sys
        from config import __file__ as config_path
        ruta = os.path.abspath(config_path)
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", "-t", ruta])
            elif sys.platform == "win32":
                os.startfile(ruta)
            else:
                subprocess.Popen(["xdg-open", ruta])
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudo abrir config.py:\n{ex}")

    # ── Métodos RPA ───────────────────────────────────────────────────

    def _rpa_explorar_txt(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Seleccionar ArchivoRPA.txt")
        if ruta:
            self._rpa_txt_entry.delete(0, "end")
            self._rpa_txt_entry.insert(0, ruta)

    def _log_rpa(self, msg):
        def _append():
            self._rpa_log.config(state="normal")
            ts = __import__("datetime").datetime.now().strftime("%H:%M:%S")
            self._rpa_log.insert("end", f"[{ts}] {msg}\n")
            self._rpa_log.see("end")
            self._rpa_log.config(state="disabled")
        self.after(0, _append)

    def _limpiar_log_rpa(self):
        self._rpa_log.config(state="normal")
        self._rpa_log.delete("1.0", "end")
        self._rpa_log.config(state="disabled")

    def _iniciar_rpa(self):
        if self._rpa_corriendo:
            messagebox.showwarning("Robot activo", "El robot ya está en ejecución.")
            return

        ruta_txt = self._rpa_txt_entry.get().strip()
        if not ruta_txt or not os.path.exists(ruta_txt):
            messagebox.showerror("Archivo no encontrado",
                f"No se encontró el archivo:\n{ruta_txt}\n\nVerifica la ruta.")
            return

        self._rpa_corriendo = True
        self._btn_iniciar_rpa.config(state="disabled", text="⏳  Robot en ejecución...")
        self._rpa_status_lbl.config(
            text="⬤  Robot activo — NO muevas el mouse hasta que se indique",
            fg=COLORS["accent"])

        hilo = threading.Thread(
            target=self._hilo_rpa,
            args=(ruta_txt,),
            daemon=True)
        hilo.start()

    def _hilo_rpa(self, ruta_txt):
        import time
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from rpa.robot import ejecutar_rpa, generar_informe
            from services.rpa_service import RPAService
            # EMAIL_CONFIG viene directo de config.py — igual que robot.py standalone
            from config import EMAIL_CONFIG

            self._log_rpa("Iniciando Robot RPA...")
            self._log_rpa(f"Archivo : {ruta_txt}")
            self._log_rpa(f"Email   : {EMAIL_CONFIG.get('destinatario', '(no configurado)')}")
            self._log_rpa("")
            self._log_rpa("Mueve el mouse al campo 'Nombre' del formulario")
            self._log_rpa("Tienes 4 segundos...")

            time.sleep(4)
            import pyautogui
            pos_nombre = pyautogui.position()
            self._log_rpa(f"✓ Campo Nombre → {pos_nombre}")
            self._log_rpa("")
            self._log_rpa("Ahora mueve el mouse al botón '✚ Crear Enfermedad'")
            self._log_rpa("Tienes 4 segundos...")

            time.sleep(4)
            pos_btn = pyautogui.position()
            self._log_rpa(f"✓ Botón Crear → {pos_btn}")
            self._log_rpa("")
            self._log_rpa("Iniciando en 3 segundos — NO toques el mouse")
            self._log_rpa("(mueve a esquina superior-izquierda para abortar)")
            time.sleep(3)

            resultado = ejecutar_rpa(
                ruta_txt=ruta_txt,
                pos_nombre=(pos_nombre.x, pos_nombre.y),
                pos_btn_crear=(pos_btn.x, pos_btn.y),
                callback=self._log_rpa,
            )

            # Recargar .pl
            try:
                RPAService().prolog_service.reload()
                self._log_rpa("✓ Base de conocimiento (.pl) actualizada")
            except Exception as ex:
                self._log_rpa(f"⚠ Error al recargar .pl: {ex}")

            # Guardar informe
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            dir_rpa = os.path.join(os.path.dirname(__file__), "..", "rpa")
            ruta_informe = os.path.join(dir_rpa, f"informe_rpa_{ts}.txt")
            generar_informe(resultado, guardar_en=ruta_informe)
            self._log_rpa(f"✓ Informe → {ruta_informe}")

            # Enviar email con EMAIL_CONFIG de config.py (igual que robot.py)
            if EMAIL_CONFIG.get("usuario") and EMAIL_CONFIG.get("destinatario"):
                self._log_rpa(f"Enviando email a {EMAIL_CONFIG['destinatario']}...")
                try:
                    r = RPAService().enviar_email_bitacora(resultado, EMAIL_CONFIG)
                    if r.get("ok"):
                        self._log_rpa(f"✓ Email enviado correctamente")
                    else:
                        self._log_rpa(f"⚠ Email falló: {r.get('mensaje')}")
                except Exception as ex:
                    self._log_rpa(f"⚠ Email error: {ex}")
            else:
                self._log_rpa("ℹ Email omitido — configura usuario/destinatario en config.py")

            self._log_rpa("")
            self._log_rpa(f"═══ COMPLETADO — OK: {resultado.get('total_ok',0)} | "
                          f"Errores: {resultado.get('total_error',0)} ═══")

        except Exception as ex:
            self._log_rpa(f"✗ Error fatal: {ex}")
        finally:
            self._rpa_corriendo = False
            self.after(0, self._rpa_finalizado)

    def _rpa_finalizado(self):
        self._btn_iniciar_rpa.config(state="normal", text="▶  Iniciar Robot RPA")
        self._rpa_status_lbl.config(
            text="⬤  Robot inactivo — ejecución completada",
            fg=COLORS["text_muted"])

    # ══════════════════════════════════════════════════════════════════
    # PERSISTENCIA
    # ══════════════════════════════════════════════════════════════════
    def _persistir_pl(self):
        from config import PROLOG_FILE
        try:
            with open(PROLOG_FILE, "r", encoding="utf-8") as f:
                contenido_original = f.read()
            marcador  = "% ==================================\n% ENFERMEDADES Y HECHOS"
            marcador2 = "% ==================================\n% TRATAMIENTOS"
            if marcador in contenido_original:
                reglas_parte = contenido_original[:contenido_original.index(marcador)]
            elif marcador2 in contenido_original:
                reglas_parte = contenido_original[:contenido_original.index(marcador2)]
            else:
                reglas_parte = contenido_original

            lineas = [
                "\n% ==================================",
                "% ENFERMEDADES Y HECHOS — Generado automáticamente",
                "% ==================================\n",
            ]
            for e in self.prolog.obtener_todas_enfermedades():
                lineas.append(f"enfermedad({e}).")
                desc = self.prolog.obtener_descripcion(e)
                if desc:
                    lineas.append(f"descripcion({e},'{str(desc).replace(chr(39), chr(92)+chr(39))}').")
                for s in self.prolog.obtener_sintomas_enfermedad(e):
                    lineas.append(f"sintoma({e},{s}).")
                for c in self.prolog.obtener_contraindicados(e):
                    lineas.append(f"contraindicado({e},{c}).")
                for cl in self.prolog.obtener_clasificaciones(e):
                    lineas.append(f"clasificacion({e},{cl}).")
            lineas.append("")
            lineas.append("% TRATAMIENTOS — trata(Medicamento, Enfermedad)")
            for r in self.prolog.query("trata(M, E)"):
                lineas.append(f"trata({r['M']},{r['E']}).")

            with open(PROLOG_FILE, "w", encoding="utf-8") as f:
                f.write(reglas_parte + "\n".join(lineas) + "\n")
        except Exception as ex:
            print(f"[admin] error persistir .pl: {ex}")