import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date
from modules.ruta_manager import RutaManager
from modules.servicio_manager import ServicioManager
import sqlite3

class CrearRutaWindow:
    def __init__(self, company_code, user_id, conn):
        self.company_code = company_code
        self.user_id = user_id
        self.conn = conn
        self.ruta_manager = RutaManager()
        self.servicio_manager = ServicioManager()

        self.root = tk.Toplevel()
        self.root.title("Crear Ruta")
        self.root.geometry("600x600")

        tk.Label(self.root, text="Crear Ruta", font=("Arial", 16)).pack(pady=10)

        # Tipo de servicio
        tk.Label(self.root, text="Tipo de servicio:").pack()
        self.service_var = tk.StringVar()
        service_combo = ttk.Combobox(self.root, textvariable=self.service_var, state="readonly", width=40)
        service_combo.pack()
        servicios = self.servicio_manager.get_servicios(company_code)
        service_combo['values'] = [s[0] for s in servicios]
        if servicios:
            service_combo.current(0)
        self.service_combo = service_combo

        # Día
        tk.Label(self.root, text="Día (YYYY-MM-DD):").pack()
        self.entry_dia = tk.Entry(self.root)
        self.entry_dia.insert(0, date.today().isoformat())
        self.entry_dia.pack()

        # Hora de inicio
        tk.Label(self.root, text="Hora de inicio (HH:MM):").pack()
        self.entry_hora = tk.Entry(self.root)
        self.entry_hora.insert(0, datetime.now().strftime("%H:%M"))
        self.entry_hora.pack()

        # Lugar de inicio
        tk.Label(self.root, text="Lugar de inicio:").pack()
        self.entry_inicio = tk.Entry(self.root, width=50)
        self.entry_inicio.pack()

        # Conductor
        tk.Label(self.root, text="Conductor:").pack()
        self.driver_var = tk.StringVar()
        driver_combo = ttk.Combobox(self.root, textvariable=self.driver_var, state="readonly", width=40)
        driver_combo.pack()
        c = self.conn.cursor()
        c.execute("""
            SELECT u.id, u.name FROM users u
            JOIN roles r ON u.role_id = r.id
            JOIN companies co ON u.company_id = co.id
            WHERE co.code = ? AND r.is_admin = 0
        """, (company_code,))
        drivers = [(r["id"], r["name"]) for r in c.fetchall()]
        driver_combo['values'] = [f"{name} (ID: {id})" for id, name in drivers]
        if drivers:
            driver_combo.current(0)
        self.driver_combo = driver_combo

        # Direcciones (paradas)
        tk.Label(self.root, text="Direcciones (una por línea):").pack()
        self.text_direcciones = tk.Text(self.root, width=50, height=8)
        self.text_direcciones.pack()

        tk.Button(self.root, text="Crear Ruta", command=self.save_ruta, width=20, height=2).pack(pady=15)

    def save_ruta(self):
        service_name = self.service_var.get()
        dia = self.entry_dia.get().strip()
        hora = self.entry_hora.get().strip()
        inicio = self.entry_inicio.get().strip()
        driver_text = self.driver_var.get()
        direcciones_text = self.text_direcciones.get("1.0", tk.END).strip()

        if not (service_name and dia and hora and inicio and driver_text and direcciones_text):
            messagebox.showerror("Error", "Complete todos los campos")
            return

        # Obtener service_id
        servicios = self.servicio_manager.get_servicios(self.company_code)
        service_id = None
        for s in servicios:
            if s[0] == service_name:
                c = self.conn.cursor()
                c.execute("SELECT id FROM services WHERE company_id = (SELECT id FROM companies WHERE code = ?) AND name = ?", 
                         (self.company_code, service_name))
                srow = c.fetchone()
                service_id = srow["id"] if srow else None
                break

        # Obtener driver_user_id
        driver_id = int(driver_text.split("(ID: ")[1].replace(")", ""))

        # Crear ruta
        route_id = self.ruta_manager.crear_ruta(
            self.company_code, "", inicio, "", 0, 
            driver_user_id=driver_id, service_id=service_id, day=dia, start_time=hora
        )

        if not route_id:
            messagebox.showerror("Error", "No se pudo crear la ruta")
            return

        # Agregar paradas
        direcciones = [d.strip() for d in direcciones_text.split("\n") if d.strip()]
        c = self.conn.cursor()
        for idx, direccion in enumerate(direcciones):
            c.execute("INSERT INTO stops (route_id, address, lat, lng, order_index) VALUES (?, ?, ?, ?, ?)",
                     (route_id, direccion, "", "", idx + 1))
        self.conn.commit()

        messagebox.showinfo("Éxito", "Ruta creada correctamente")
        self.root.destroy()
