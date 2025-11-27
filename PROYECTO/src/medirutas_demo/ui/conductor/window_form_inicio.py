import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from modules.formulario_manager import FormularioManager
import os
import shutil

class FormInicioWindow:
    def __init__(self, company_code, user_id, conn, callback=None):
        self.company_code = company_code
        self.user_id = user_id
        self.conn = conn
        self.formulario_manager = FormularioManager()
        self.callback = callback
        self.foto_path = None

        self.root = tk.Toplevel()
        self.root.title("Formulario de Inicio")
        self.root.geometry("500x500")

        tk.Label(self.root, text="Formulario de Inicio", font=("Arial", 16)).pack(pady=10)

        # Hora de inicio
        tk.Label(self.root, text="Hora de inicio (HH:MM):", font=("Arial", 12)).pack(pady=5)
        self.entry_hora = tk.Entry(self.root, width=20, font=("Arial", 12))
        self.entry_hora.insert(0, datetime.now().strftime("%H:%M"))
        self.entry_hora.pack(pady=5)

        # Foto del lugar
        tk.Label(self.root, text="Foto del lugar al llegar:", font=("Arial", 12)).pack(pady=5)
        self.foto_label = tk.Label(self.root, text="No hay foto seleccionada", fg="gray")
        self.foto_label.pack(pady=5)
        tk.Button(self.root, text="Subir Foto", command=self.subir_foto, width=20).pack(pady=5)

        # Firma del médico
        tk.Label(self.root, text="Firma del médico:", font=("Arial", 12)).pack(pady=5)
        self.entry_firma = tk.Entry(self.root, width=50)
        self.entry_firma.pack(pady=5)

        # Botones
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Finalizar", command=self.guardar, width=20, height=2).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", command=self.root.destroy, width=20, height=2).pack(side="left", padx=5)

    def subir_foto(self):
        file = filedialog.askopenfilename(
            title="Seleccionar Foto",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp"), ("Todos los archivos", "*.*")]
        )
        if file:
            self.foto_path = file
            self.foto_label.config(text=os.path.basename(file), fg="green")

    def guardar(self):
        hora = self.entry_hora.get().strip()
        firma = self.entry_firma.get().strip()

        if not hora:
            messagebox.showerror("Error", "Ingrese la hora de inicio")
            return

        if not self.foto_path:
            messagebox.showerror("Error", "Suba una foto del lugar")
            return

        if not firma:
            messagebox.showerror("Error", "Ingrese la firma del médico")
            return

        # Copiar foto a carpeta uploads
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        filename = f"inicio_{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(self.foto_path)}"
        dest_path = os.path.join(uploads_dir, filename)
        try:
            shutil.copy(self.foto_path, dest_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar la foto: {str(e)}")
            return

        # Guardar formulario
        if self.formulario_manager.crear_form_inicio(self.company_code, self.user_id, hora, dest_path, firma):
            messagebox.showinfo("Éxito", "Formulario de inicio guardado correctamente")
            self.root.destroy()
            if self.callback:
                self.callback()
        else:
            messagebox.showerror("Error", "No se pudo guardar el formulario")
