import tkinter as tk

class HomeConductorWindow:
    def __init__(self, cod_empresa):
        self.cod_empresa = cod_empresa

        self.root = tk.Tk()
        self.root.title("Panel Conductor")
        self.root.geometry("400x300")

        tk.Label(self.root, text=f"Conductor - Empresa {cod_empresa}", font=("Arial", 14)).pack(pady=20)

        tk.Label(self.root, text="Bienvenido conductor.", font=("Arial", 12)).pack(pady=10)

        tk.Button(self.root, text="Cerrar Sesión", command=self.root.destroy).pack(pady=20)

        self.root.mainloop()
