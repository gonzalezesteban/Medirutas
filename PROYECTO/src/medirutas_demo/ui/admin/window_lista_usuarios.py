import tkinter as tk
from tkinter import messagebox, ttk
from modules.usuario_manager import UsuarioManager

class ListaUsuariosWindow:
    def __init__(self, company_code, conn):
        self.company_code = company_code
        self.conn = conn
        self.usuario_manager = UsuarioManager()

        self.root = tk.Toplevel()
        self.root.title("Lista de Usuarios")
        self.root.geometry("700x500")

        tk.Label(self.root, text="Lista de Usuarios", font=("Arial", 16)).pack(pady=10)

        # Filtro por rol
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Filtrar por rol:").pack(side="left", padx=5)
        self.role_filter_var = tk.StringVar()
        self.role_filter_entry = tk.Entry(filter_frame, textvariable=self.role_filter_var, width=30)
        self.role_filter_entry.pack(side="left", padx=5)
        tk.Button(filter_frame, text="Filtrar", command=self.cargar_usuarios).pack(side="left", padx=5)
        tk.Button(filter_frame, text="Limpiar", command=self.limpiar_filtro).pack(side="left", padx=5)

        # Lista de usuarios
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(list_frame, columns=("id", "nombre", "rol"), show="headings", 
                                yscrollcommand=scrollbar.set)
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("rol", text="Rol")
        self.tree.column("id", width=50)
        self.tree.column("nombre", width=200)
        self.tree.column("rol", width=300)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        tk.Button(self.root, text="Actualizar", command=self.cargar_usuarios).pack(pady=10)

        self.cargar_usuarios()

    def limpiar_filtro(self):
        self.role_filter_var.set("")
        self.cargar_usuarios()

    def cargar_usuarios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        role_filter = self.role_filter_var.get().strip() if self.role_filter_var.get().strip() else None
        usuarios = self.usuario_manager.get_usuarios(self.company_code, role_filter)

        if not usuarios:
            self.tree.insert("", "end", values=("", "No hay usuarios", ""))
            return

        for uid, nombre, rol, is_admin in usuarios:
            tipo = "Admin" if is_admin else "Conductor"
            self.tree.insert("", "end", values=(uid, nombre, f"{rol} ({tipo})"))
