import tkinter as tk
from tkinter import messagebox
from modules.rol_manager import RolManager
import sqlite3

class CrearCodigosWindow:
    def __init__(self, company_code, user_id, conn):
        self.company_code = company_code
        self.user_id = user_id
        self.conn = conn
        self.rol_manager = RolManager()

        self.root = tk.Toplevel()
        self.root.title("Crear Códigos de Rol")
        self.root.geometry("500x500")

        tk.Label(self.root, text="Crear Códigos de Rol", font=("Arial", 16)).pack(pady=10)

        # Verificar si es admin líder
        c = self.conn.cursor()
        c.execute("""
            SELECT r.is_admin FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.id = ? AND r.code = '0000'
        """, (user_id,))
        is_lider = c.fetchone()
        if not is_lider or not is_lider["is_admin"]:
            tk.Label(self.root, text="Solo el Administrador Líder puede crear códigos", 
                    fg="red", font=("Arial", 10)).pack(pady=10)
            tk.Button(self.root, text="Cerrar", command=self.root.destroy).pack(pady=10)
            return

        # Frame para crear código
        create_frame = tk.Frame(self.root)
        create_frame.pack(pady=10)

        tk.Label(create_frame, text="Cargo:").grid(row=0, column=0, sticky="e", padx=5)
        self.cargo_var = tk.StringVar(value="Conductor")
        cargo_combo = tk.OptionMenu(create_frame, self.cargo_var, "Administrador", "Conductor")
        cargo_combo.grid(row=0, column=1, padx=5, sticky="w")

        tk.Label(create_frame, text="Código:").grid(row=1, column=0, sticky="e", padx=5)
        self.entry_codigo = tk.Entry(create_frame, width=30)
        self.entry_codigo.grid(row=1, column=1, padx=5)

        tk.Button(create_frame, text="Crear Código", command=self.crear_codigo, width=20).grid(row=2, column=0, columnspan=2, pady=10)

        # Lista de códigos existentes
        tk.Label(self.root, text="Códigos existentes:", font=("Arial", 12, "bold")).pack(pady=(10,5))
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=20)

        self.listbox = tk.Listbox(list_frame, width=60, height=12)
        self.listbox.pack(fill="both", expand=True)

        tk.Button(self.root, text="Finalizar", command=self.finalizar, width=20).pack(pady=15)

        self.cargar_codigos()

    def crear_codigo(self):
        cargo = self.cargo_var.get()
        codigo = self.entry_codigo.get().strip()

        if not codigo:
            messagebox.showerror("Error", "Ingrese un código")
            return

        # Obtener company_id
        c = self.conn.cursor()
        c.execute("SELECT id FROM companies WHERE code = ?", (self.company_code,))
        comp = c.fetchone()
        if not comp:
            messagebox.showerror("Error", "Empresa no encontrada")
            return
        comp_id = comp["id"]

        # Verificar si el código ya existe
        c.execute("SELECT id FROM roles WHERE company_id = ? AND code = ?", (comp_id, codigo))
        if c.fetchone():
            messagebox.showerror("Error", "El código ya existe")
            return

        # Crear rol
        is_admin = 1 if cargo == "Administrador" else 0
        nombre_rol = f"{cargo} - {codigo}"
        try:
            c.execute("INSERT INTO roles (company_id, name, code, is_admin) VALUES (?, ?, ?, ?)",
                     (comp_id, nombre_rol, codigo, is_admin))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Código creado correctamente")
            self.entry_codigo.delete(0, tk.END)
            self.cargar_codigos()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El código ya existe")

    def cargar_codigos(self):
        self.listbox.delete(0, tk.END)
        c = self.conn.cursor()
        c.execute("SELECT name, code, is_admin FROM roles WHERE company_id = (SELECT id FROM companies WHERE code = ?) ORDER BY code",
                 (self.company_code,))
        for r in c.fetchall():
            tipo = "Administrador" if r["is_admin"] else "Conductor"
            self.listbox.insert(tk.END, f"{tipo} - Código: {r['code']} ({r['name']})")

    def finalizar(self):
        self.root.destroy()
