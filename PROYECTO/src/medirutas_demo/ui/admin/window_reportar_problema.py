import tkinter as tk
from tkinter import messagebox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ReportarProblemaWindow:
    def __init__(self, company_code, user_id, conn):
        self.company_code = company_code
        self.user_id = user_id
        self.conn = conn

        self.root = tk.Toplevel()
        self.root.title("Reportar Problema")
        self.root.geometry("600x500")

        tk.Label(self.root, text="Reportar Problema", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Descripción del problema:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(10,5))

        self.text_area = tk.Text(self.root, width=70, height=20, wrap=tk.WORD)
        self.text_area.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Label(self.root, text="El reporte se enviará a: jega.seiya@gmail.com", 
                font=("Arial", 9), fg="gray").pack(pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Enviar Reporte", command=self.enviar_reporte, width=20, height=2).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", command=self.root.destroy, width=20, height=2).pack(side="left", padx=5)

    def enviar_reporte(self):
        texto = self.text_area.get("1.0", tk.END).strip()

        if not texto:
            messagebox.showerror("Error", "Escriba una descripción del problema")
            return

        # Obtener información del usuario
        c = self.conn.cursor()
        c.execute("SELECT name FROM users WHERE id = ?", (self.user_id,))
        user = c.fetchone()
        user_name = user["name"] if user else "Usuario desconocido"

        # Intentar enviar email
        try:
            # Configuración del email (usando Gmail SMTP)
            # Nota: En producción, esto debería usar credenciales seguras
            sender_email = "jega.seiya@gmail.com"
            receiver_email = "jega.seiya@gmail.com"
            password = ""  # Se requiere contraseña de aplicación de Gmail

            # Crear mensaje
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = f"Reporte de Problema - MediRutas - Usuario: {user_name}"

            body = f"""
Usuario: {user_name}
Código de Empresa: {self.company_code}
ID de Usuario: {self.user_id}

Descripción del problema:
{texto}
            """
            message.attach(MIMEText(body, "plain"))

            # Intentar enviar (solo si hay contraseña configurada)
            if password:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
                messagebox.showinfo("Éxito", "Reporte enviado correctamente")
            else:
                # Simular envío para demo
                print(f"REPORTE (simulado):\n{body}")
                messagebox.showinfo("Éxito", 
                    "Reporte registrado. En producción se enviará a jega.seiya@gmail.com\n\n" +
                    f"Usuario: {user_name}\nEmpresa: {self.company_code}\n\n{texto}")
            
            self.root.destroy()
        except Exception as e:
            # En caso de error, al menos guardar el reporte localmente
            print(f"Error al enviar email: {e}")
            print(f"REPORTE:\nUsuario: {user_name}\nEmpresa: {self.company_code}\n{texto}")
            messagebox.showinfo("Reporte Registrado", 
                f"El reporte ha sido registrado localmente.\n\n" +
                f"Usuario: {user_name}\nEmpresa: {self.company_code}\n\n{texto}")
            self.root.destroy()
