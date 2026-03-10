import tkinter as tk
from ui.home_view import HomeView
from ui.patient_view import PatientView
from ui.login_view import LoginView
from ui.admin_view import AdminView
from ui.diagnosis_view import DiagnosisView
from ui.theme import COLORS

class MainWindow:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("MediLogic")
        self.root.geometry("1200x700")
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.resizable(True, True)

        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 600
        y = (self.root.winfo_screenheight() // 2) - 350
        self.root.geometry(f"1200x700+{x}+{y}")

        self.container = tk.Frame(self.root, bg=COLORS["bg_dark"])
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for View in (HomeView, PatientView, LoginView, AdminView, DiagnosisView):
            frame = View(self.container, self)
            self.frames[View] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomeView)

    def show_frame(self, view):
        frame = self.frames[view]
        frame.tkraise()

    def run(self):
        self.root.mainloop()