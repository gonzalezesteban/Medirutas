import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from modules.formulario_manager import FormularioManager
import os
import shutil

class FormFinWindow:
    def __init__(self, company_code, user_id, conn, callback=None):
        self.company_code = company_code
        self.user_id = user_id
        self.conn = conn
        self.formulario_manager = FormularioManager()
        self.callback = callback
        self.foto_fin = None
        self.fotos_peajes = []

        self.root = tk.Toplevel()
        self.root.title("Formulario Final")
        self.root.geometry("550x700")

        tk.Label(self.root, text="Formulario Final", font=("Arial", 16)).pack(pady=10)

        # Hora de finalización
        tk.Label(self.root, text="Hora de finalización (HH:MM):", font=("Arial", 12)).pack(pady=5)
        self.entry_hora = tk.Entry(self.root, width=20, font=("Arial", 12))
        self.entry_hora.insert(0, datetime.now().strftime("%H:%M"))
        self.entry_hora.pack(pady=5)

        # Valores de peajes
        tk.Label(self.root, text="Valores de peajes (separados por coma):", font=("Arial", 12)).pack(pady=5)
        self.entry_peajes = tk.Entry(self.root, width=50)
        self.entry_peajes.pack(pady=5)
        tk.Label(self.root, text="Ejemplo: 5000, 3000, 2000", fg="gray", font=("Arial", 9)).pack()

        # Fotos de peajes (opcional)
        tk.Label(self.root, text="Fotos de peajes (opcional):", font=("Arial", 12)).pack(pady=5)
        self.peajes_label = tk.Label(self.root, text="No hay fotos seleccionadas", fg="gray")
        self.peajes_label.pack(pady=5)
        tk.Button(self.root, text="Subir Fotos de Peajes", command=self.subir_peajes, width=25).pack(pady=5)

        # Foto final
        tk.Label(self.root, text="Foto de finalización:", font=("Arial", 12)).pack(pady=5)
        self.foto_fin_label = tk.Label(self.root, text="No hay foto seleccionada", fg="gray")
        self.foto_fin_label.pack(pady=5)
        tk.Button(self.root, text="Subir Foto Final", command=self.subir_final, width=25).pack(pady=5)

        # Firma
        tk.Label(self.root, text="Firma del médico y/o conductor:", font=("Arial", 12)).pack(pady=5)
        self.entry_firma = tk.Entry(self.root, width=50)
        self.entry_firma.pack(pady=5)

        # Botones
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Finalizar", command=self.guardar, width=20, height=2).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", command=self.root.destroy, width=20, height=2).pack(side="left", padx=5)

    def subir_peajes(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar Fotos de Peajes",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp"), ("Todos los archivos", "*.*")]
        )
        if files:
            self.fotos_peajes = list(files)
            self.peajes_label.config(text=f"{len(files)} foto(s) seleccionada(s)", fg="green")

    def subir_final(self):
        file = filedialog.askopenfilename(
            title="Seleccionar Foto Final",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp"), ("Todos los archivos", "*.*")]
        )
        if file:
            self.foto_fin = file
            self.foto_fin_label.config(text=os.path.basename(file), fg="green")

    def guardar(self):
        hora = self.entry_hora.get().strip()
        firma = self.entry_firma.get().strip()
        peajes_text = self.entry_peajes.get().strip()

        if not hora:
            messagebox.showerror("Error", "Ingrese la hora de finalización")
            return

        if not self.foto_fin:
            messagebox.showerror("Error", "Suba la foto de finalización")
            return

        if not firma:
            messagebox.showerror("Error", "Ingrese la firma")
            return

        # Procesar peajes
        lista_peajes = []
        if peajes_text:
            try:
                lista_peajes = [float(x.strip()) for x in peajes_text.split(",") if x.strip()]
            except ValueError:
                messagebox.showerror("Error", "Los valores de peajes deben ser números separados por comas")
                return

        # Copiar fotos a carpeta uploads
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)

        # Copiar foto final
        filename_fin = f"final_{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(self.foto_fin)}"
        dest_path_fin = os.path.join(uploads_dir, filename_fin)
        try:
            shutil.copy(self.foto_fin, dest_path_fin)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar la foto final: {str(e)}")
            return

        # Copiar fotos de peajes
        dest_paths_peajes = []
        for idx, foto_peaje in enumerate(self.fotos_peajes):
            filename_peaje = f"peaje_{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}_{os.path.basename(foto_peaje)}"
            dest_path_peaje = os.path.join(uploads_dir, filename_peaje)
            try:
                shutil.copy(foto_peaje, dest_path_peaje)
                dest_paths_peajes.append(dest_path_peaje)
            except Exception as e:
                print(f"Error al copiar foto de peaje: {str(e)}")

        # Guardar formulario
        if self.formulario_manager.crear_form_fin(self.company_code, self.user_id, hora, dest_path_fin, 
                                                  lista_peajes, dest_paths_peajes, firma):
            messagebox.showinfo("Éxito", "Formulario final enviado correctamente")
            self.root.destroy()
            if self.callback:
                self.callback()
        else:
            messagebox.showerror("Error", "No se pudo guardar el formulario")
