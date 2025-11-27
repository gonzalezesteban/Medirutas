import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import os
import json
from PIL import Image, ImageTk

class DocumentosWindow:
    def __init__(self, company_code, conn):
        self.company_code = company_code
        self.conn = conn

        self.root = tk.Toplevel()
        self.root.title("Documentos")
        self.root.geometry("800x600")

        tk.Label(self.root, text="Documentos de Rutas", font=("Arial", 16)).pack(pady=10)

        # Filtro de conductores
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Filtrar por conductor:").pack(side="left", padx=5)
        self.driver_filter_var = tk.StringVar()
        self.driver_filter_entry = tk.Entry(filter_frame, textvariable=self.driver_filter_var, width=30)
        self.driver_filter_entry.pack(side="left", padx=5)
        tk.Button(filter_frame, text="Filtrar", command=self.cargar_rutas).pack(side="left", padx=5)

        # Filtro de fecha
        tk.Label(filter_frame, text="Fecha (YYYY-MM-DD):").pack(side="left", padx=5)
        self.date_filter_var = tk.StringVar()
        self.date_filter_entry = tk.Entry(filter_frame, textvariable=self.date_filter_var, width=15)
        self.date_filter_entry.pack(side="left", padx=5)
        tk.Button(filter_frame, text="Limpiar", command=self.limpiar_filtros).pack(side="left", padx=5)

        # Lista de rutas
        tk.Label(self.root, text="Rutas completadas:", font=("Arial", 12, "bold")).pack(pady=(10,5))
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=20)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(list_frame, columns=("fecha", "conductor", "ruta_id"), show="headings",
                                yscrollcommand=scrollbar.set)
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("conductor", text="Conductor")
        self.tree.heading("ruta_id", text="Ruta ID")
        self.tree.column("fecha", width=120)
        self.tree.column("conductor", width=200)
        self.tree.column("ruta_id", width=100)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        self.tree.bind('<<TreeviewSelect>>', self.on_route_select)

        # Frame para mostrar documentos
        self.doc_frame = tk.Frame(self.root)
        self.doc_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.cargar_rutas()

    def limpiar_filtros(self):
        self.driver_filter_var.set("")
        self.date_filter_var.set("")
        self.cargar_rutas()

    def cargar_rutas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        driver_filter = self.driver_filter_var.get().strip()
        date_filter = self.date_filter_var.get().strip()

        c = self.conn.cursor()
        c.execute("SELECT id FROM companies WHERE code = ?", (self.company_code,))
        comp = c.fetchone()
        if not comp:
            return
        comp_id = comp["id"]

        # Obtener rutas con documentos
        query = """
            SELECT DISTINCT r.id, r.date, u.name as driver_name
            FROM routes r
            JOIN documents d ON r.id = d.route_id
            JOIN users u ON r.driver_user_id = u.id
            WHERE r.company_id = ?
        """
        params = [comp_id]

        if driver_filter:
            query += " AND u.name LIKE ?"
            params.append(f"%{driver_filter}%")

        if date_filter:
            query += " AND r.date = ?"
            params.append(date_filter)

        query += " ORDER BY r.date DESC, r.id DESC"

        c.execute(query, params)
        routes = c.fetchall()

        for route in routes:
            self.tree.insert("", "end", values=(route["date"], route["driver_name"], route["id"]),
                           tags=(route["id"],))

    def on_route_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        route_id = item['tags'][0] if item['tags'] else None

        if not route_id:
            return

        # Limpiar frame de documentos
        for widget in self.doc_frame.winfo_children():
            widget.destroy()

        # Obtener documentos de la ruta
        c = self.conn.cursor()
        c.execute("""
            SELECT d.type, d.filepath, d.timestamp, d.extra_json, u.name as user_name
            FROM documents d
            LEFT JOIN users u ON d.user_id = u.id
            WHERE d.route_id = ?
            ORDER BY d.timestamp
        """, (route_id,))
        docs = c.fetchall()

        tk.Label(self.doc_frame, text=f"Documentos de la Ruta #{route_id}", 
                font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

        for doc in docs:
            doc_type = doc["type"]
            filepath = doc["filepath"]
            timestamp = doc["timestamp"]
            extra_json = doc["extra_json"]
            user_name = doc["user_name"] or "Desconocido"

            doc_frame = tk.Frame(self.doc_frame, relief=tk.RAISED, borderwidth=1)
            doc_frame.pack(fill="x", pady=5, padx=10)

            tk.Label(doc_frame, text=f"Tipo: {doc_type} | Usuario: {user_name} | Fecha: {timestamp[:19]}",
                    font=("Arial", 10)).pack(anchor="w", padx=5, pady=2)

            if extra_json:
                try:
                    extra = json.loads(extra_json)
                    if doc_type == "inicio":
                        hora = extra.get("hora", "N/A")
                        tk.Label(doc_frame, text=f"Hora de inicio: {hora}", font=("Arial", 9)).pack(anchor="w", padx=5)
                    elif doc_type == "final":
                        hora = extra.get("hora", "N/A")
                        peajes = extra.get("peajes", [])
                        tk.Label(doc_frame, text=f"Hora de finalización: {hora}", font=("Arial", 9)).pack(anchor="w", padx=5)
                        if peajes:
                            tk.Label(doc_frame, text=f"Peajes: {', '.join(map(str, peajes))}", 
                                    font=("Arial", 9)).pack(anchor="w", padx=5)
                except:
                    pass

            if filepath and os.path.exists(filepath):
                btn_frame = tk.Frame(doc_frame)
                btn_frame.pack(anchor="w", padx=5, pady=2)
                tk.Button(btn_frame, text="Abrir Foto", 
                         command=lambda f=filepath: self.abrir_archivo(f)).pack(side="left", padx=2)
            else:
                tk.Label(doc_frame, text="Archivo no disponible", fg="gray", font=("Arial", 9)).pack(anchor="w", padx=5)

    def abrir_archivo(self, filepath):
        try:
            if os.path.exists(filepath):
                os.startfile(filepath)
            else:
                messagebox.showerror("Error", "El archivo no existe")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {str(e)}")
