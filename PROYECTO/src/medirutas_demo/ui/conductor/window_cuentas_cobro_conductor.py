import tkinter as tk
from tkinter import messagebox, ttk
from modules.cobro_manager import CobroManager
from datetime import date
from ui.conductor.window_detalle_cuenta_cobro_conductor import DetalleCuentaCobroConductorWindow

class CuentasCobroConductorWindow:
    def __init__(self, company_code, user_id, conn):
        self.company_code = company_code
        self.user_id = user_id
        self.conn = conn
        self.cobro_manager = CobroManager()

        self.root = tk.Toplevel()
        self.root.title("Todas tus Cuentas de Cobro")
        self.root.geometry("600x500")

        tk.Label(self.root, text="Todas tus Cuentas de Cobro", font=("Arial", 16)).pack(pady=10)

        # Lista de cuentas
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(list_frame, columns=("mes", "total"), show="headings",
                                yscrollcommand=scrollbar.set)
        self.tree.heading("mes", text="Mes/Año")
        self.tree.heading("total", text="Total a Pagar")
        self.tree.column("mes", width=200)
        self.tree.column("total", width=200)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        self.tree.bind('<<TreeviewSelect>>', self.on_cuenta_select)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Ver Detalle", command=self.ver_detalle, width=20).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Actualizar", command=self.cargar_cuentas, width=20).pack(side="left", padx=5)

        self.selected_month_year = None
        self.cargar_cuentas()

    def cargar_cuentas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        cuentas = self.cobro_manager.get_cuentas_cobro_usuario(self.company_code, self.user_id)

        if not cuentas:
            self.tree.insert("", "end", values=("No hay cuentas de cobro", ""))
            return

        for month_year, total in cuentas:
            self.tree.insert("", "end", values=(month_year, f"${total:.2f}"),
                           tags=(month_year,))

    def on_cuenta_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        self.selected_month_year = item['tags'][0] if item['tags'] else None

    def ver_detalle(self):
        if not self.selected_month_year:
            messagebox.showerror("Error", "Seleccione una cuenta de cobro")
            return

        DetalleCuentaCobroConductorWindow(self.company_code, self.user_id, self.selected_month_year, self.conn)
