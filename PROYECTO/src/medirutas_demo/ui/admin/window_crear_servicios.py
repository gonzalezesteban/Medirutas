import tkinter as tk
from tkinter import messagebox
from modules.servicio_manager import ServicioManager

class CrearServiciosWindow:
    def __init__(self, company_code, conn):
        self.company_code = company_code
        self.conn = conn
        self.servicio_manager = ServicioManager()
        self.servicios = []

        self.root = tk.Toplevel()
        self.root.title("Crear Servicios")
        self.root.geometry("600x500")

        tk.Label(self.root, text="Crear Servicios", font=("Arial", 16)).pack(pady=10)

        # Frame para crear nuevo servicio
        create_frame = tk.Frame(self.root)
        create_frame.pack(pady=10)

        tk.Label(create_frame, text="Nombre del servicio:").grid(row=0, column=0, sticky="e", padx=5)
        self.entry_nombre = tk.Entry(create_frame, width=30)
        self.entry_nombre.grid(row=0, column=1, padx=5)

        tk.Label(create_frame, text="Costo por hora ($):").grid(row=1, column=0, sticky="e", padx=5)
        self.entry_costo = tk.Entry(create_frame, width=30)
        self.entry_costo.grid(row=1, column=1, padx=5)

        btn_frame = tk.Frame(create_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="➕ Agregar", command=self.agregar_servicio, width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑️ Eliminar", command=self.eliminar_servicio, width=15).pack(side="left", padx=5)

        # Lista de servicios
        tk.Label(self.root, text="Servicios:", font=("Arial", 12, "bold")).pack(pady=(10,5))
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=20)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(list_frame, width=60, height=15, yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        tk.Button(self.root, text="Finalizar", command=self.finalizar, width=20).pack(pady=15)

        self.cargar_servicios()

    def cargar_servicios(self):
        self.listbox.delete(0, tk.END)
        servicios = self.servicio_manager.get_servicios(self.company_code)
        self.servicios = []
        for s in servicios:
            nombre, costo = s
            self.listbox.insert(tk.END, f"{nombre} - ${costo}/hora")
            self.servicios.append((nombre, costo))

    def agregar_servicio(self):
        nombre = self.entry_nombre.get().strip()
        costo = self.entry_costo.get().strip()

        if not (nombre and costo):
            messagebox.showerror("Error", "Complete todos los campos")
            return

        try:
            costo_float = float(costo)
        except ValueError:
            messagebox.showerror("Error", "El costo debe ser un número")
            return

        if self.servicio_manager.crear_servicio(self.company_code, nombre, costo_float):
            messagebox.showinfo("Éxito", "Servicio creado correctamente")
            self.entry_nombre.delete(0, tk.END)
            self.entry_costo.delete(0, tk.END)
            self.cargar_servicios()
        else:
            messagebox.showerror("Error", "El servicio ya existe o no se pudo crear")

    def eliminar_servicio(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un servicio para eliminar")
            return

        idx = selected[0]
        nombre, costo = self.servicios[idx]
        
        # Obtener el ID del servicio
        c = self.conn.cursor()
        c.execute("SELECT id FROM services WHERE company_id = (SELECT id FROM companies WHERE code = ?) AND name = ?",
                 (self.company_code, nombre))
        srow = c.fetchone()
        if srow:
            if self.servicio_manager.eliminar_servicio(self.company_code, srow["id"]):
                messagebox.showinfo("Éxito", "Servicio eliminado")
                self.cargar_servicios()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el servicio")

    def finalizar(self):
        self.root.destroy()
