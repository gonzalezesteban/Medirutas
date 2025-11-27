# utils/image_utils.py
from PIL import Image, ImageTk

def load_image(path, width=None, height=None):
    """
    Carga una imagen y opcionalmente la redimensiona.
    Retorna PhotoImage listo para usar en tkinter.
    """
    try:
        img = Image.open(path)
        if width and height:
            img = img.resize((width, height))
        return ImageTk.PhotoImage(img)
    except Exception:
        return None
