# utils/ui_components.py
import tkinter as tk

class ScrollableFrame(tk.Frame):
    """
    Un frame con scrollbar vertical.
    Perfecto para listas o paneles deslizables (lo que pediste en el punto 4E).
    """
    def __init__(self, parent, width=400, height=400):
        super().__init__(parent)

        canvas = tk.Canvas(self, width=width, height=height)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)

        self.scrollable_frame = tk.Frame(canvas)

        # Se crea un window interno donde vive el contenido
        window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configurar desplazamiento
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        self.scrollable_frame.bind("<Configure>", configure_scroll)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class LabeledEntry(tk.Frame):
    """
    Un pequeño componente reutilizable:
    Label + Entry en una sola fila.
    """
    def __init__(self, parent, text="", entry_width=20, **kwargs):
        super().__init__(parent)
        tk.Label(self, text=text).pack(side="left")
        self.entry = tk.Entry(self, width=entry_width, **kwargs)
        self.entry.pack(side="left")

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
