import tkinter as tk
from tkinter import ttk
from database import init_db
from services import VehiculoService, PropietarioService
from crud_view import GenericCRUDFrame

class App(tk.Tk):
    """Aplicación principal con interfaz basada en pestañas y vistas genéricas."""
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión - CRUD Genérico")
        self.geometry("900x520")
        self.minsize(800, 480)

        # Aplicar estilo ttk moderno
        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self._configure_styles()
        self._build_tabs()

    def _configure_styles(self):
        """Ajusta detalles visuales de los componentes ttk."""
        self.style.configure("TNotebook.Tab", padding=[15, 6], font=("Segoe UI", 10, "bold"))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        self.style.configure("TLabel", font=("Segoe UI", 9))
        self.style.configure("TButton", font=("Segoe UI", 9))

    def _build_tabs(self):
        """Instancia los CRUDs para las diferentes entidades usando la clase genérica."""
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Configuración de Entidad: Vehículos
        vehiculos_fields = [
            {"key": "patente", "label": "Patente"},
            {"key": "marca", "label": "Marca"},
            {"key": "modelo", "label": "Modelo"},
            {"key": "anio", "label": "Año"}
        ]
        vehiculo_service = VehiculoService()
        tab_vehiculos = GenericCRUDFrame(
            parent=notebook,
            title="Vehículos",
            fields_config=vehiculos_fields,
            service=vehiculo_service
        )
        notebook.add(tab_vehiculos, text=" 🚗 Gestión de Vehículos ")

        # 2. Configuración de Entidad: Propietarios
        propietarios_fields = [
            {"key": "dni", "label": "DNI"},
            {"key": "nombre", "label": "Nombre Completo"},
            {"key": "telefono", "label": "Teléfono"},
            {"key": "email", "label": "Correo Electrónico"}
        ]
        propietario_service = PropietarioService()
        tab_propietarios = GenericCRUDFrame(
            parent=notebook,
            title="Propietarios",
            fields_config=propietarios_fields,
            service=propietario_service
        )
        notebook.add(tab_propietarios, text=" 👤 Gestión de Propietarios ")

def main():
    # Inicializar tablas en la base de datos
    init_db()
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
