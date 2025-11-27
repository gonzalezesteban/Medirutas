# utils/file_utils.py
import os
import shutil

def ensure_dir(path):
    """
    Crea una carpeta si no existe.
    """
    if not os.path.exists(path):
        os.makedirs(path)

def copy_file(src, dst):
    """
    Copia un archivo desde src hacia dst, creando carpetas si es necesario.
    """
    ensure_dir(os.path.dirname(dst))
    shutil.copyfile(src, dst)
    return dst

def save_text(path, content):
    """
    Guarda texto en un archivo.
    """
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def read_text(path):
    """
    Lee contenido en texto si existe.
    """
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
