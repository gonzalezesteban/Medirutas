import tkinter as tk
from tkinter import messagebox
from database import Database

class RegisterWindow:
    def __init__(self):
        self.db = Database()

        self.root = tk.Toplevel()
        self.root.title("Registrar Empresa")
        self.root.geometry("400x380")

        tk.Label(self.root, text="Registrar Empresa", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Nombre Empresa:").pack()
        self.entry_nombre = tk.Entry(self.root)
        self.entry_nombre.pack()

        tk.Label(self.root, text="Código Empresa:").pack()
        self.entry_codigo = tk.Entry(self.root)
        self.entry_codigo.pack()

        tk.Label(self.root, text="Usuario Admin:").pack()
        self.entry_user = tk.Entry(self.root)
        self.entry_user.pack()

        tk.Label(self.root, text="Contraseña Admin:").pack()
        self.entry_pwd = tk.Entry(self.root, show="*")
        self.entry_pwd.pack()

        tk.Button(self.root, text="Registrar", command=self.register).pack(pady=20)

    def register(self):
        nombre = self.entry_nombre.get()
        codigo = self.entry_codigo.get()
        user = self.entry_user.get()
        pwd = self.entry_pwd.get()

        if not (nombre and codigo and user and pwd):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        if self.db.register_empresa(nombre, codigo, user, pwd):
            messagebox.showinfo("Éxito", "Empresa registrada correctamente.")
            self.root.destroy()
        else:
            messagebox.showerror("Error", "El código de empresa ya existe.")
