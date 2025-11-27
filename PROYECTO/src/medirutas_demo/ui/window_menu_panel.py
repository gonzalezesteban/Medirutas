import tkinter as tk
from tkinter import messagebox
from database import Database

class MenuPanelWindow:
    def __init__(self, cod_empresa):
        self.cod_empresa = cod_empresa
        self.db = Database()

        self.root = tk.Toplevel()
        self.root.title("Panel de Administración")
        self.root.geometry("500x400")

        tk.Label(self.root, text="Gestión de Conductores", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Usuario del Conductor:").pack()
        self.entry_user = tk.Entry(self.root)
        self.entry_user.pack()

        tk.Label(self.root, text="Contraseña:").pack()
        self.entry_pwd = tk.Entry(self.root, show="*")
        self.entry_pwd.pack()

        tk.Button(self.root, text="Registrar Conductor", command=self.register_driver).pack(pady=15)

        tk.Button(self.root, text="Ver Conductores Registrados", command=self.show_drivers).pack(pady=10)

    def register_driver(self):
        user = self.entry_user.get()
        pwd = self.entry_pwd.get()

        if not (user and pwd):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        if self.db.register_conductor(self.cod_empresa, user, pwd):
            messagebox.showinfo("Éxito", "Conductor registrado.")
        else:
            messagebox.showerror("Error", "El conductor ya existe en esta empresa.")

    def show_drivers(self):
        conductores = self.db.get_conductores(self.cod_empresa)

        if not conductores:
            messagebox.showinfo("Conductores", "No hay conductores registrados.")
            return

        listado = "\n".join([f"- {c}" for c in conductores])
        messagebox.showinfo("Conductores", listado)
