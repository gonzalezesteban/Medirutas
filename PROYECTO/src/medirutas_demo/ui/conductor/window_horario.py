import tkinter as tk
from tkinter import messagebox, ttk
from modules.ruta_manager import RutaManager
from datetime import date

class HorarioConductorWindow:
    def __init__(self, company_code, user_id, conn):
        self.company_code = company_code
        self.user_id = user_id
        self.conn = conn
        self.ruta_manager = RutaManager()

        self.root = tk.Toplevel()
        self.root.title("Horario del Conductor")
        self.root.geometry("800x600")

        tk.Label(self.root, text="Horario Programado", font=("Arial", 16)).pack(pady=10)

        # Lista de rutas
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(list_frame, columns=("fecha", "hora", "inicio", "direcciones"), 
                                show="headings", yscrollcommand=scrollbar.set)
        self.tree.heading("fecha", text="Día/Mes")
        self.tree.heading("hora", text="Hora Inicio")
        self.tree.heading("inicio", text="Ubicación Inicio")
        self.tree.heading("direcciones", text="Direcciones")
        self.tree.column("fecha", width=120)
        self.tree.column("hora", width=100)
        self.tree.column("inicio", width=200)
        self.tree.column("direcciones", width=350)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Actualizar", command=self.cargar_rutas, width=20).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Salir", command=self.root.destroy, width=20).pack(side="left", padx=5)

        self.cargar_rutas()

    def cargar_rutas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        rutas = self.ruta_manager.get_rutas_conductor(self.company_code, self.user_id)

        if not rutas:
            self.tree.insert("", "end", values=("", "No hay rutas programadas", "", ""))
            return

        for fecha, hora, inicio, direcciones in rutas:
            # Formatear fecha para mostrar día/mes
            try:
                fecha_obj = date.fromisoformat(fecha)
                fecha_str = fecha_obj.strftime("%d/%m")
            except:
                fecha_str = fecha

            self.tree.insert("", "end", values=(fecha_str, hora, inicio, direcciones))
