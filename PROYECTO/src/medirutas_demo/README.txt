# MediRutas Demo
## Objetivo
Mostrar el funcionamiento general del flujo completo:
* Creación de cuentas.
* Inicio de sesión.
* Administración (usuarios, roles, empresas, servicios, códigos, rutas, cuentas de cobro).
* Operación del conductor (formularios de inicio/fin, horarios, cuentas de cobro).
Estructura del Proyecto
medirutas_demo/
│
-── main.py
-── database.py
-── config.py
-── README.md
-── requirements.txt
│
-── assets/
│   -── logo.png
│   -── map_placeholder.png
│   -── photo_placeholder.png
│   -── icons/
│       -── menu_icon.png
│       -── back_icon.png
│       -── user_icon.png
│
├── ui/
│   -── __init__.py
│   -── window_login.py
│   -── window_register.py
│   -── window_home_admin.py
│   -── window_home_conductor.py
│   -── window_menu_panel.py
│   │
│   -── admin/
│   │   -── __init__.py
│   │   -── window_crear_ruta.py
│   │   -── window_cuentas_cobro.py
│   │   -── window_detalle_cuenta_cobro.py
│   │   -── window_documentos.py
│   │   -── window_lista_usuarios.py
│   │   -── window_reportar_problema.py
│   │   -── window_crear_servicios.py
│   │   -── window_crear_codigos.py
│   │   -── window_permisos.py
│   │
│   └── conductor/
│       -── __init__.py
│       -── window_form_inicio.py
│       -── window_form_fin.py
│       -── window_cuentas_cobro_conductor.py
│       -── window_detalle_cuenta_cobro_conductor.py
│       -── window_horario.py
│
-── modules/
│   -── __init__.py
│   -── auth_manager.py
│   -── empresa_manager.py
│   -── rol_manager.py
│   -── usuario_manager.py
│   -── servicio_manager.py
│   -── ruta_manager.py
│   -── formulario_manager.py
│   -── cobro_manager.py
│
-── utils/
    -── __init__.py
    -── file_utils.py
    -── image_utils.py
    -── ui_components.py

## Para Ejecución ##
1.
* Python 3.10+

2.
* Instalar las dependencias
pip install -r requirements.txt

3.
Inicializar la base de datos
Al ejecutar por primera vez, **database.py** creará las tablas necesarias.

4.
Ejecutar:
python main.py

---
Dependencias Principales
* tkinter (incluido con Python)
* pillow
* sqlite3 (incluido con Python)