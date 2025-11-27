import tkinter as tk
from tkinter import messagebox, ttk
from modules.cobro_manager import CobroManager

class DetalleCuentaCobroConductorWindow:
    def __init__(self, company_code, user_id, month_year, conn):
        self.company_code = company_code
        self.user_id = user_id
        self.month_year = month_year
        self.conn = conn
        self.cobro_manager = CobroManager()

        self.root = tk.Toplevel()
        self.root.title("Detalle Cuenta de Cobro")
        self.root.geometry("700x600")

        tk.Label(self.root, text=f"Cuenta de Cobro - {month_year}", font=("Arial", 16)).pack(pady=10)

        # Detalles
        tk.Label(self.root, text="Detalles por Tipo de Servicio:", font=("Arial", 12, "bold")).pack(pady=(10,5))

        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(list_frame, columns=("servicio", "cantidad", "horas", "peajes", "total"), 
                                show="headings", yscrollcommand=scrollbar.set)
        self.tree.heading("servicio", text="Tipo de Servicio")
        self.tree.heading("cantidad", text="Cantidad")
        self.tree.heading("horas", text="Horas Trabajadas")
        self.tree.heading("peajes", text="Peajes")
        self.tree.heading("total", text="Total")
        self.tree.column("servicio", width=200)
        self.tree.column("cantidad", width=100)
        self.tree.column("horas", width=120)
        self.tree.column("peajes", width=100)
        self.tree.column("total", width=120)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        # Cargar detalles
        detalles = self.cobro_manager.get_detalle_cobro(company_code, user_id, month_year)

        total_servicios = 0
        total_horas = 0.0
        total_peajes = 0.0
        total_pagar = 0.0

        if detalles:
            for servicio, cantidad, horas, peajes in detalles:
                # Obtener costo por hora del servicio
                c = self.conn.cursor()
                c.execute("""
                    SELECT cost_per_hour FROM services 
                    WHERE company_id = (SELECT id FROM companies WHERE code = ?) AND name = ?
                """, (company_code, servicio))
                srow = c.fetchone()
                cost_per_hour = srow["cost_per_hour"] if srow else 0.0

                total_servicio = (horas * cost_per_hour) + peajes
                total_servicios += cantidad
                total_horas += horas
                total_peajes += peajes
                total_pagar += total_servicio

                self.tree.insert("", "end", values=(
                    servicio,
                    cantidad,
                    f"{horas:.2f}",
                    f"${peajes:.2f}",
                    f"${total_servicio:.2f}"
                ))

        # Fila de totales
        self.tree.insert("", "end", values=(
            "TOTAL",
            total_servicios,
            f"{total_horas:.2f}",
            f"${total_peajes:.2f}",
            f"${total_pagar:.2f}"
        ), tags=("total",))

        self.tree.tag_configure("total", background="#e0e0e0", font=("Arial", 10, "bold"))

        # Total a pagar
        total_frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=2)
        total_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(total_frame, text=f"Total a Pagar: ${total_pagar:.2f}", 
                font=("Arial", 14, "bold"), fg="green").pack(pady=10)

        tk.Button(self.root, text="Finalizar", command=self.root.destroy, width=20).pack(pady=15)
