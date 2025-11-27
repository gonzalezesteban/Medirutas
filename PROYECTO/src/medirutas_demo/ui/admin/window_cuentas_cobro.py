import tkinter as tk
from tkinter import messagebox, ttk
from modules.cobro_manager import CobroManager
from datetime import datetime, date
from ui.admin.window_detalle_cuenta_cobro import DetalleCuentaCobroWindow

class CuentasCobroWindow:
    def __init__(self, company_code, conn):
        self.company_code = company_code
        self.conn = conn
        self.cobro_manager = CobroManager()

        self.root = tk.Toplevel()
        self.root.title("Cuentas de Cobro")
        self.root.geometry("700x600")

        tk.Label(self.root, text="Cuentas de Cobro", font=("Arial", 16)).pack(pady=10)

        # Filtro de conductores
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Filtrar por conductor:").pack(side="left", padx=5)
        self.driver_filter_var = tk.StringVar()
        self.driver_filter_entry = tk.Entry(filter_frame, textvariable=self.driver_filter_var, width=30)
        self.driver_filter_entry.pack(side="left", padx=5)
        tk.Button(filter_frame, text="Filtrar", command=self.cargar_cuentas).pack(side="left", padx=5)
        tk.Button(filter_frame, text="Generar Mes Actual", command=self.generar_mes_actual).pack(side="left", padx=5)

        # Lista de cuentas de cobro
        tk.Label(self.root, text="Histórico de Cuentas de Cobro (últimos 12 meses):", 
                font=("Arial", 12, "bold")).pack(pady=(10,5))

        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=20)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(list_frame, columns=("mes", "conductor", "total"), show="headings",
                                yscrollcommand=scrollbar.set)
        self.tree.heading("mes", text="Mes/Año")
        self.tree.heading("conductor", text="Conductor")
        self.tree.heading("total", text="Total a Pagar")
        self.tree.column("mes", width=150)
        self.tree.column("conductor", width=200)
        self.tree.column("total", width=150)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        self.tree.bind('<<TreeviewSelect>>', self.on_cuenta_select)

        # Cuenta actual del mes
        current_frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=2)
        current_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(current_frame, text="Cuenta de Cobro Actual (Mes Actual):", 
                font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

        self.current_label = tk.Label(current_frame, text="Cargando...", font=("Arial", 10))
        self.current_label.pack(anchor="w", padx=20, pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Ver Detalle", command=self.ver_detalle, width=20).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Actualizar", command=self.cargar_cuentas, width=20).pack(side="left", padx=5)

        self.selected_billing_id = None
        self.cargar_cuentas()

    def generar_mes_actual(self):
        month_year = date.today().strftime("%Y-%m")
        if self.cobro_manager.generate_billing_for_month(self.company_code, month_year):
            messagebox.showinfo("Éxito", "Cuentas de cobro generadas para el mes actual")
            self.cargar_cuentas()
        else:
            messagebox.showerror("Error", "No se pudieron generar las cuentas de cobro")

    def cargar_cuentas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        driver_filter = self.driver_filter_var.get().strip()

        c = self.conn.cursor()
        c.execute("SELECT id FROM companies WHERE code = ?", (self.company_code,))
        comp = c.fetchone()
        if not comp:
            return
        comp_id = comp["id"]

        # Obtener cuentas de cobro
        query = """
            SELECT br.id, br.month_year, br.total_amount, u.name as driver_name
            FROM billing_records br
            LEFT JOIN users u ON br.driver_user_id = u.id
            WHERE br.company_id = ?
        """
        params = [comp_id]

        if driver_filter:
            query += " AND u.name LIKE ?"
            params.append(f"%{driver_filter}%")

        query += " ORDER BY br.month_year DESC LIMIT 12"

        c.execute(query, params)
        cuentas = c.fetchall()

        for cuenta in cuentas:
            mes_anio = cuenta["month_year"]
            conductor = cuenta["driver_name"] or "Todos"
            total = f"${cuenta['total_amount']:.2f}"
            self.tree.insert("", "end", values=(mes_anio, conductor, total),
                           tags=(cuenta["id"],))

        # Cargar cuenta actual
        month_year = date.today().strftime("%Y-%m")
        c.execute("""
            SELECT SUM(total_amount) as total
            FROM billing_records
            WHERE company_id = ? AND month_year = ?
        """, (comp_id, month_year))
        current = c.fetchone()
        if current and current["total"]:
            self.current_label.config(text=f"Total del mes actual ({month_year}): ${current['total']:.2f}")
        else:
            self.current_label.config(text=f"No hay cuenta de cobro para el mes actual ({month_year})")

    def on_cuenta_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        self.selected_billing_id = item['tags'][0] if item['tags'] else None

    def ver_detalle(self):
        if not self.selected_billing_id:
            messagebox.showerror("Error", "Seleccione una cuenta de cobro")
            return

        DetalleCuentaCobroWindow(self.company_code, self.selected_billing_id, self.conn)
