import tkinter as tk
from ui.theme import COLORS, FONTS

URGENCY_COLOR={"Alta":"#E05C6A","Media":"#F4A261","Baja":"#00C9A7"}
URGENCY_BG={"Alta":"#2A1520","Media":"#2A1D10","Baja":"#0D2420"}

def _btn(parent,text,command,secondary=False):
    bg=COLORS["bg_input"] if secondary else COLORS["accent"]
    fg=COLORS["text_secondary"] if secondary else COLORS["bg_dark"]
    hbg=COLORS["border"] if secondary else COLORS["accent_hover"]
    b=tk.Button(parent,text=text,command=command,bg=bg,fg=fg,font=FONTS["button"],relief="flat",bd=0,padx=20,pady=8,cursor="hand2",activebackground=hbg,activeforeground=fg)
    b.bind("<Enter>",lambda e:b.config(bg=hbg))
    b.bind("<Leave>",lambda e:b.config(bg=bg))
    return b

class DiagnosisView(tk.Frame):
    def __init__(self,parent,controller):
        super().__init__(parent,bg=COLORS["bg_dark"])
        self.controller=controller
        self._paquete=None
        self.build_ui()

    def build_ui(self):
        sb=tk.Frame(self,bg=COLORS["bg_card"],width=240)
        sb.pack(side="left",fill="y")
        sb.pack_propagate(False)
        tk.Frame(sb,bg=COLORS["accent"],height=4).pack(fill="x")
        lr=tk.Frame(sb,bg=COLORS["bg_card"])
        lr.pack(pady=(30,6))
        tk.Label(lr,text="Medi",font=FONTS["logo"],bg=COLORS["bg_card"],fg=COLORS["text_primary"]).pack(side="left")
        tk.Label(lr,text="Logic",font=FONTS["logo"],bg=COLORS["bg_card"],fg=COLORS["accent"]).pack(side="left")
        tk.Label(sb,text="Sistema de Diagnóstico\nMédico Inteligente",font=FONTS["body_sm"],bg=COLORS["bg_card"],fg=COLORS["text_muted"],justify="center").pack(pady=(0,20))
        tk.Frame(sb,bg=COLORS["border"],height=1).pack(fill="x",padx=24)
        tk.Label(sb,text="RESULTADO",font=("Helvetica",9,"bold"),bg=COLORS["bg_card"],fg=COLORS["accent"]).pack(pady=(16,2))
        self._pac_lbl=tk.Label(sb,text="—",font=FONTS["heading"],bg=COLORS["bg_card"],fg=COLORS["text_primary"],wraplength=190)
        self._pac_lbl.pack()
        self._fecha_lbl=tk.Label(sb,text="",font=FONTS["body_sm"],bg=COLORS["bg_card"],fg=COLORS["text_muted"])
        self._fecha_lbl.pack(pady=(4,0))
        self._total_lbl=tk.Label(sb,text="",font=FONTS["body_sm"],bg=COLORS["bg_card"],fg=COLORS["text_secondary"])
        self._total_lbl.pack(pady=(8,0))
        tk.Frame(sb,bg=COLORS["bg_card"]).pack(expand=True)
        _btn(sb,"Nueva Consulta",lambda:self.controller.show_frame(__import__("ui.patient_view").patient_view.PatientView),secondary=True).pack(pady=(0,8),padx=20,fill="x")
        _btn(sb,"Exportar PDF",self._exportar_pdf,secondary=True).pack(pady=(0,8),padx=20,fill="x")
        _btn(sb,"Ver Historial",self._ver_historial,secondary=True).pack(pady=(0,24),padx=20,fill="x")

        mo=tk.Frame(self,bg=COLORS["bg_dark"])
        mo.pack(side="left",fill="both",expand=True)
        self._canvas=tk.Canvas(mo,bg=COLORS["bg_dark"],highlightthickness=0,bd=0)
        vsb=tk.Scrollbar(mo,orient="vertical",command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vsb.set)
        self._rf=tk.Frame(self._canvas,bg=COLORS["bg_dark"])
        self._rf.bind("<Configure>",lambda e:self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.create_window((0,0),window=self._rf,anchor="nw")
        self._canvas.pack(side="left",fill="both",expand=True)
        vsb.pack(side="right",fill="y")
        self._canvas.bind_all("<MouseWheel>",lambda e:self._canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

    def mostrar_resultados(self,paquete):
        self._paquete=paquete
        self._pac_lbl.config(text=paquete["nombre"])
        self._fecha_lbl.config(text=paquete["fecha"])
        self._total_lbl.config(text=f'{paquete["total"]} resultado(s)')
        for w in self._rf.winfo_children(): w.destroy()
        PX=40

        hdr=tk.Frame(self._rf,bg=COLORS["bg_dark"])
        hdr.pack(fill="x",padx=PX,pady=(36,0))
        tk.Label(hdr,text="Informe de Diagnóstico",font=FONTS["title"],bg=COLORS["bg_dark"],fg=COLORS["text_primary"]).pack(anchor="w")
        tk.Label(hdr,text=f'Paciente: {paquete["nombre"]}  ·  {paquete["fecha"]}',font=FONTS["body_sm"],bg=COLORS["bg_dark"],fg=COLORS["text_secondary"]).pack(anchor="w",pady=(4,0))
        tk.Frame(hdr,bg=COLORS["accent"],height=2,width=60).pack(anchor="w",pady=(10,0))

        # Resumen síntomas
        cs=tk.Frame(self._rf,bg=COLORS["bg_card"],padx=28,pady=16)
        cs.pack(fill="x",padx=PX,pady=(16,6))
        tk.Label(cs,text="SÍNTOMAS REPORTADOS",font=("Helvetica",9,"bold"),bg=COLORS["bg_card"],fg=COLORS["text_muted"]).pack(anchor="w",pady=(0,10))
        prow=tk.Frame(cs,bg=COLORS["bg_card"])
        prow.pack(fill="x")
        col_sev={"leve":COLORS["accent"],"moderado":COLORS["warning"],"severo":COLORS["danger"]}
        for s,nivel in paquete["sintomas"]:
            pill=tk.Frame(prow,bg=COLORS["bg_input"],padx=10,pady=4)
            pill.pack(side="left",padx=(0,6),pady=2)
            tk.Label(pill,text=s.replace("_"," "),font=FONTS["body_sm"],bg=COLORS["bg_input"],fg=COLORS["text_primary"]).pack(side="left")
            tk.Label(pill,text=f" {nivel}",font=("Helvetica",9,"bold"),bg=COLORS["bg_input"],fg=col_sev.get(nivel,COLORS["text_muted"])).pack(side="left")
        if paquete["alergias"]:
            tk.Frame(cs,bg=COLORS["border"],height=1).pack(fill="x",pady=(12,8))
            tk.Label(cs,text=f'⚠  Alergias: {", ".join(paquete["alergias"])}',font=FONTS["body_sm"],bg=COLORS["bg_card"],fg=COLORS["warning"]).pack(anchor="w")
        if paquete["cronicas"]:
            tk.Label(cs,text=f'Condiciones crónicas: {", ".join(paquete["cronicas"])}',font=FONTS["body_sm"],bg=COLORS["bg_card"],fg=COLORS["text_secondary"]).pack(anchor="w",pady=(4,0))

        if not paquete["resultados"]:
            nc=tk.Frame(self._rf,bg=COLORS["bg_card"],padx=30,pady=30)
            nc.pack(fill="x",padx=PX,pady=12)
            tk.Label(nc,text="⚠",font=("Helvetica",28),bg=COLORS["bg_card"],fg=COLORS["warning"]).pack()
            tk.Label(nc,text="No se encontró diagnóstico",font=FONTS["heading"],bg=COLORS["bg_card"],fg=COLORS["text_primary"]).pack(pady=(8,4))
            tk.Label(nc,text="Los síntomas no coinciden con ningún patrón conocido (afinidad < 30%).",font=FONTS["body_sm"],bg=COLORS["bg_card"],fg=COLORS["text_secondary"]).pack()
            return

        for i,r in enumerate(paquete["resultados"]):
            self._card_res(r,i+1,PX)
        tk.Frame(self._rf,bg=COLORS["bg_dark"],height=40).pack()

    def _card_res(self,r,idx,px):
        urg=r["urgencia"]
        uc=URGENCY_COLOR.get(urg,COLORS["text_muted"])
        ubg=URGENCY_BG.get(urg,COLORS["bg_card"])
        pct=float(r["porcentaje"])

        outer=tk.Frame(self._rf,bg=COLORS["bg_card"])
        outer.pack(fill="x",padx=px,pady=(0,10))
        tk.Frame(outer,bg=uc,height=3).pack(fill="x")
        c=tk.Frame(outer,bg=COLORS["bg_card"],padx=28,pady=20)
        c.pack(fill="both",expand=True)

        tr=tk.Frame(c,bg=COLORS["bg_card"])
        tr.pack(fill="x")
        tk.Label(tr,text=f"#{idx}  {r['nombre_ui']}",font=FONTS["heading"],bg=COLORS["bg_card"],fg=COLORS["text_primary"]).pack(side="left")
        tk.Label(tr,text=f"  {urg}  ",font=("Helvetica",9,"bold"),bg=uc,fg=COLORS["bg_dark"],padx=8,pady=3).pack(side="right")

        if r.get("descripcion"):
            tk.Label(c,text=r["descripcion"],font=FONTS["body_sm"],bg=COLORS["bg_card"],fg=COLORS["text_secondary"]).pack(anchor="w",pady=(4,0))

        tk.Frame(c,bg=COLORS["border"],height=1).pack(fill="x",pady=(14,10))
        ar=tk.Frame(c,bg=COLORS["bg_card"])
        ar.pack(fill="x",pady=(0,6))
        tk.Label(ar,text="Afinidad:",font=FONTS["body_sm"],bg=COLORS["bg_card"],fg=COLORS["text_muted"]).pack(side="left")
        tk.Label(ar,text=f"  {pct}%",font=("Helvetica",12,"bold"),bg=COLORS["bg_card"],fg=uc).pack(side="left")

        bb=tk.Frame(c,bg=COLORS["bg_input"],height=8)
        bb.pack(fill="x",pady=(0,14))
        bb.update_idletasks()
        tk.Frame(bb,bg=uc,height=8).place(relwidth=min(max(pct/100,0),1),relheight=1)

        af=tk.Frame(c,bg=ubg,padx=14,pady=10)
        af.pack(fill="x",pady=(0,14))
        tk.Label(af,text=f"→  {r['accion']}",font=("Helvetica",11,"bold"),bg=ubg,fg=uc).pack(anchor="w")

        med=r.get("medicamento","ninguno")
        todos=r.get("todos_meds",[])
        mf=tk.Frame(c,bg=COLORS["bg_card"])
        mf.pack(fill="x",pady=(0,14))
        tk.Label(mf,text="Medicamento sugerido:",font=("Helvetica",10,"bold"),bg=COLORS["bg_card"],fg=COLORS["text_muted"]).pack(anchor="w")
        md=str(med).replace("_"," ").title() if med!="ninguno" else "⚠ Ninguno disponible (revisar alergias)"
        mc=COLORS["accent"] if med!="ninguno" else COLORS["danger"]
        tk.Label(mf,text=f"  {md}",font=("Helvetica",11,"bold"),bg=COLORS["bg_card"],fg=mc).pack(anchor="w",pady=(4,0))
        if todos and len(todos)>1:
            otros=[str(m).replace("_"," ").title() for m in todos if m!=med]
            if otros:
                tk.Label(mf,text=f"  Alternativas: {', '.join(otros)}",font=FONTS["body_sm"],bg=COLORS["bg_card"],fg=COLORS["text_secondary"]).pack(anchor="w",pady=(2,0))

        tk.Frame(c,bg=COLORS["border"],height=1).pack(fill="x",pady=(4,12))
        coins=[str(s).replace("_"," ") for s in r.get("coinciden",[])]
        ausen=[str(s).replace("_"," ") for s in r.get("ausentes",[])]
        tc=tk.Frame(c,bg=COLORS["bg_card"])
        tc.pack(fill="x")
        if coins:
            ca=tk.Frame(tc,bg=COLORS["bg_card"])
            ca.pack(side="left",fill="both",expand=True,padx=(0,10))
            tk.Label(ca,text="✓  Síntomas que coinciden:",font=("Helvetica",9,"bold"),bg=COLORS["bg_card"],fg=COLORS["accent"]).pack(anchor="w")
            tk.Label(ca,text="\n".join(f"  • {s}" for s in coins),font=FONTS["body_sm"],bg=COLORS["bg_card"],fg=COLORS["text_primary"],justify="left").pack(anchor="w",pady=(4,0))
        if ausen:
            cb2=tk.Frame(tc,bg=COLORS["bg_card"])
            cb2.pack(side="left",fill="both",expand=True)
            tk.Label(cb2,text="○  Síntomas no reportados:",font=("Helvetica",9,"bold"),bg=COLORS["bg_card"],fg=COLORS["text_muted"]).pack(anchor="w")
            tk.Label(cb2,text="\n".join(f"  • {s}" for s in ausen),font=FONTS["body_sm"],bg=COLORS["bg_card"],fg=COLORS["text_muted"],justify="left").pack(anchor="w",pady=(4,0))

        reglas=r.get("reglas",[])
        if reglas:
            tk.Frame(c,bg=COLORS["border"],height=1).pack(fill="x",pady=(12,10))
            tk.Label(c,text="⚙  Reglas Prolog activadas:",font=("Helvetica",9,"bold"),bg=COLORS["bg_card"],fg=COLORS["text_muted"]).pack(anchor="w")
            for reg in reglas:
                rf=tk.Frame(c,bg=COLORS["bg_input"],padx=12,pady=6)
                rf.pack(fill="x",pady=(4,0))
                tk.Label(rf,text=reg,font=("Courier",9),bg=COLORS["bg_input"],fg=COLORS["text_secondary"],anchor="w",wraplength=700,justify="left").pack(fill="x")

    def _exportar_pdf(self):
        if not self._paquete: return
        try:
            from services.pdf_service import PDFService
            PDFService().generar(self._paquete)
            from tkinter import messagebox
            messagebox.showinfo("PDF exportado","Informe guardado correctamente.")
        except Exception as ex:
            from tkinter import messagebox
            messagebox.showerror("Error al exportar PDF",str(ex))

    def _ver_historial(self):
        try:
            from ui.patient_view import PatientView
            historial=self.controller.frames[PatientView].service.obtener_historial()
        except Exception: return
        win=tk.Toplevel(self)
        win.title("Historial — Sesión Actual")
        win.configure(bg=COLORS["bg_dark"])
        win.geometry("700x480")
        tk.Label(win,text="Historial de la Sesión",font=FONTS["title"],bg=COLORS["bg_dark"],fg=COLORS["text_primary"]).pack(pady=(20,4),padx=30,anchor="w")
        tk.Label(win,text=f"{len(historial)} diagnóstico(s)",font=FONTS["body_sm"],bg=COLORS["bg_dark"],fg=COLORS["text_secondary"]).pack(padx=30,anchor="w")
        tk.Frame(win,bg=COLORS["accent"],height=2).pack(fill="x",padx=30,pady=10)
        ch=tk.Canvas(win,bg=COLORS["bg_dark"],highlightthickness=0)
        vh=tk.Scrollbar(win,orient="vertical",command=ch.yview)
        ch.configure(yscrollcommand=vh.set)
        ih=tk.Frame(ch,bg=COLORS["bg_dark"])
        ih.bind("<Configure>",lambda e:ch.configure(scrollregion=ch.bbox("all")))
        ch.create_window((0,0),window=ih,anchor="nw")
        ch.pack(side="left",fill="both",expand=True,padx=20)
        vh.pack(side="right",fill="y")
        if not historial:
            tk.Label(ih,text="No hay diagnósticos en esta sesión.",font=FONTS["body"],bg=COLORS["bg_dark"],fg=COLORS["text_muted"]).pack(pady=30)
        else:
            for p in historial:
                rh=tk.Frame(ih,bg=COLORS["bg_card"],padx=20,pady=12)
                rh.pack(fill="x",pady=(0,6))
                tk.Label(rh,text=f'{p["fecha"]}  —  {p["nombre"]}',font=FONTS["heading"],bg=COLORS["bg_card"],fg=COLORS["text_primary"]).pack(side="left")
                def _ver(paq=p):
                    self.mostrar_resultados(paq); win.destroy()
                _btn(rh,"Ver",_ver).pack(side="right")
                tk.Label(rh,text=f'{p["total"]} resultado(s)',font=FONTS["body_sm"],bg=COLORS["bg_card"],fg=COLORS["text_secondary"]).pack(side="right",padx=12)