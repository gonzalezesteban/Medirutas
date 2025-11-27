import tkinter as tk
from tkinter import messagebox
from window_menu_panel import MenuPanelWindow

class HomeAdminWindow:
    def __init__(self, cod_empresa):
        self.cod_empresa = cod_empresa

        self.root = tk.Tk()
        self.root.title("Panel Administrador")
        self.root.geometry("450x350")

        tk.Label(self.root, text=f"Administrador - Empresa {cod_empresa}", font=("Arial", 14)).pack(pady=15)

        tk.Button(self.root, text="Panel de Gestión", width=25, command=self.open_panel).pack(pady=10)
        tk.Button(self.root, text="Cerrar Sesión", width=25, command=self.root.destroy).pack(pady=10)

        self.root.mainloop()

    def open_panel(self):
        MenuPanelWindow(self.cod_empresa)
