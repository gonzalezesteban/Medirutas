import tkinter as tk
from tkinter import messagebox, ttk
from modules.usuario_manager import UsuarioManager
import json

class PermisosWindow:
    def __init__(self, company_code, user_id, conn):
        self.company_code = company_code
        self.user_id = user_id
        self.conn = conn
        self.usuario_manager = UsuarioManager()

        self.root = tk.Toplevel()
        self.root.title("Permisos")
        self.root.geometry("600x500")

        tk.Label(self.root, text="Gestión de Permisos", font=("Arial", 16)).pack(pady=10)

        # Verificar si es admin líder
        c = self.conn.cursor()
        c.execute("""
            SELECT r.is_admin FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.id = ? AND r.code = '0000'
        """, (user_id,))
        is_lider = c.fetchone()
        if not is_lider or not is_lider["is_admin"]:
            tk.Label(self.root, text="Solo el Administrador Líder puede gestionar permisos", 
                    fg="red", font=("Arial", 10)).pack(pady=10)
            tk.Button(self.root, text="Cerrar", command=self.root.destroy).pack(pady=10)
            return

        # Filtro de usuarios
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Buscar usuario:").pack(side="left", padx=5)
        self.user_filter_var = tk.StringVar()
        self.user_filter_entry = tk.Entry(filter_frame, textvariable=self.user_filter_var, width=30)
        self.user_filter_entry.pack(side="left", padx=5)
        tk.Button(filter_frame, text="Buscar", command=self.cargar_usuarios).pack(side="left", padx=5)

        # Lista de usuarios
        tk.Label(self.root, text="Usuarios:", font=("Arial", 12, "bold")).pack(pady=(10,5))
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=20)

        self.user_listbox = tk.Listbox(list_frame, width=60, height=10)
        self.user_listbox.pack(fill="both", expand=True)
        self.user_listbox.bind('<<ListboxSelect>>', self.on_user_select)

        # Permisos disponibles
        self.permisos_frame = tk.Frame(self.root)
        self.permisos_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.selected_user_id = None
        self.cargar_usuarios()

    def cargar_usuarios(self):
        self.user_listbox.delete(0, tk.END)
        usuarios = self.usuario_manager.get_usuarios(self.company_code)
        self.usuarios_dict = {}

        filter_text = self.user_filter_var.get().strip().lower()
        for uid, nombre, rol, is_admin in usuarios:
            if not filter_text or filter_text in nombre.lower() or filter_text in rol.lower():
                self.user_listbox.insert(tk.END, f"{nombre} ({rol})")
                self.usuarios_dict[self.user_listbox.size() - 1] = uid

    def on_user_select(self, event):
        selection = self.user_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        self.selected_user_id = self.usuarios_dict.get(idx)

        # Limpiar frame de permisos
        for widget in self.permisos_frame.winfo_children():
            widget.destroy()

        if not self.selected_user_id:
            return

        # Obtener permisos del usuario
        c = self.conn.cursor()
        c.execute("SELECT permissions_json FROM users WHERE id = ?", (self.selected_user_id,))
        user = c.fetchone()
        current_permissions = []
        if user and user["permissions_json"]:
            try:
                current_permissions = json.loads(user["permissions_json"])
            except:
                pass

        tk.Label(self.permisos_frame, text="Permisos de Administrador:", font=("Arial", 12, "bold")).pack(anchor="w")

        permisos_disponibles = [
            "Crear rutas",
            "Cuentas de cobro",
            "Documentos",
            "Lista de usuarios",
            "Reportar problema",
            "Crear servicios",
            "Crear códigos",
            "Permisos"
        ]

        self.permission_vars = {}
        for perm in permisos_disponibles:
            var = tk.BooleanVar(value=perm in current_permissions)
            self.permission_vars[perm] = var
            tk.Checkbutton(self.permisos_frame, text=perm, variable=var).pack(anchor="w", padx=20)

        tk.Button(self.permisos_frame, text="Guardar Permisos", command=self.guardar_permisos, 
                 width=20).pack(pady=10)

    def guardar_permisos(self):
        if not self.selected_user_id:
            messagebox.showerror("Error", "Seleccione un usuario")
            return

        permisos_seleccionados = [perm for perm, var in self.permission_vars.items() if var.get()]
        permisos_json = json.dumps(permisos_seleccionados)

        # Actualizar permisos en la base de datos
        # Primero necesitamos agregar la columna permissions_json si no existe
        c = self.conn.cursor()
        try:
            c.execute("ALTER TABLE users ADD COLUMN permissions_json TEXT")
            self.conn.commit()
        except:
            pass  # La columna ya existe

        c.execute("UPDATE users SET permissions_json = ? WHERE id = ?", 
                 (permisos_json, self.selected_user_id))
        self.conn.commit()

        messagebox.showinfo("Éxito", "Permisos guardados correctamente")
