import tkinter as tk
from tkinter import ttk, messagebox

class GenericCRUDFrame(ttk.Frame):
    """
    Clase genérica para vistas CRUD en Tkinter.
    Construye la interfaz de forma dinámica a partir de la configuración
    de campos y opera sobre cualquier servicio que cumpla la interfaz CRUD.
    """
    def __init__(self, parent, title, fields_config, service):
        """
        :param parent: Widget contenedor padre.
        :param title: Título descriptivo de la entidad (ej: 'Vehículos').
        :param fields_config: Lista de diccionarios [{'key': 'campo', 'label': 'Etiqueta'}].
        :param service: Instancia de servicio con métodos get_all, create, update, delete.
        """
        super().__init__(parent, padding=10)
        self.title = title
        self.fields_config = fields_config
        self.service = service

        # Gestión del estado
        self.entries = {}
        self.selected_id = None

        self._build_ui()
        self.load_data()

    def _build_ui(self):
        """Construye todos los componentes visuales de manera modular y dinámica."""
        # Configurar expansión de grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # 1. Panel Izquierdo: Formulario y Acciones
        left_container = ttk.Frame(self)
        left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_container.columnconfigure(0, weight=1)

        form_frame = ttk.LabelFrame(left_container, text=f"Formulario de {self.title}", padding=10)
        form_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)

        # GENERACIÓN DINÁMICA DE CAMPOS (Bucle obligatorio)
        for row_idx, field in enumerate(self.fields_config):
            key = field["key"]
            label_text = field["label"]

            label = ttk.Label(form_frame, text=f"{label_text}:")
            label.grid(row=row_idx, column=0, padx=5, pady=6, sticky="w")

            entry = ttk.Entry(form_frame)
            entry.grid(row=row_idx, column=1, padx=5, pady=6, sticky="ew")

            # Almacenamiento eficiente de referencias a los Entry en un diccionario
            self.entries[key] = entry

        # Panel de Botones de Acción
        actions_frame = ttk.LabelFrame(left_container, text="Acciones", padding=10)
        actions_frame.grid(row=1, column=0, sticky="ew")
        for col_idx in range(4):
            actions_frame.columnconfigure(col_idx, weight=1)

        btn_create = ttk.Button(actions_frame, text="Crear", command=self.on_create)
        btn_create.grid(row=0, column=0, padx=3, pady=5, sticky="ew")

        btn_update = ttk.Button(actions_frame, text="Actualizar", command=self.on_update)
        btn_update.grid(row=0, column=1, padx=3, pady=5, sticky="ew")

        btn_delete = ttk.Button(actions_frame, text="Eliminar", command=self.on_delete)
        btn_delete.grid(row=0, column=2, padx=3, pady=5, sticky="ew")

        btn_clear = ttk.Button(actions_frame, text="Limpiar", command=self.clear_form)
        btn_clear.grid(row=0, column=3, padx=3, pady=5, sticky="ew")

        # 2. Panel Derecho: Tabla Treeview con Scrollbar
        table_frame = ttk.LabelFrame(self, text=f"Listado de {self.title}", padding=10)
        table_frame.grid(row=0, column=1, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Definición dinámica de columnas (ID + campos configurados)
        columns = ["id"] + [f["key"] for f in self.fields_config]
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        # Configuración de encabezados y anchos
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=50, anchor="center")

        for field in self.fields_config:
            self.tree.heading(field["key"], text=field["label"])
            self.tree.column(field["key"], width=120, anchor="w")

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Evento de selección en la tabla
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    # -------------------------------------------------------------
    # Métodos de Gestión de Datos y Estado del Formulario
    # -------------------------------------------------------------
    def get_form_data(self):
        """Lee y retorna los datos del formulario como diccionario."""
        return {key: entry.get().strip() for key, entry in self.entries.items()}

    def validate_fields(self):
        """Valida que ningún campo esté vacío. Retorna (bool, dict_datos)."""
        data = self.get_form_data()
        for field in self.fields_config:
            key = field["key"]
            label = field["label"]
            if not data.get(key):
                messagebox.showwarning(
                    "Validación de Campo",
                    f"El campo '{label}' no puede estar vacío."
                )
                self.entries[key].focus()
                return False, None
        return True, data

    def clear_form(self):
        """Limpia los campos Entry y restablece la selección."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.selected_id = None
        # Deseleccionar en la tabla si hay elemento seleccionado
        selected = self.tree.selection()
        if selected:
            self.tree.selection_remove(selected)

    def load_data(self):
        """Recarga los registros en la tabla Treeview desde el servicio."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            records = self.service.get_all()
            for record in records:
                row_values = [record.get("id")] + [record.get(f["key"]) for f in self.fields_config]
                self.tree.insert("", tk.END, values=row_values)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los registros: {e}")

    # -------------------------------------------------------------
    # Manejadores de Eventos CRUD y Validaciones
    # -------------------------------------------------------------
    def on_tree_select(self, event):
        """Carga los datos de la fila seleccionada en los campos del formulario."""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item = self.tree.item(selected_items[0])
        values = item["values"]
        if not values:
            return

        self.selected_id = values[0]

        # Poblar los Entry de forma iterativa
        for idx, field in enumerate(self.fields_config, start=1):
            key = field["key"]
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, str(values[idx]))

    def on_create(self):
        """Flujo para crear un nuevo registro."""
        is_valid, data = self.validate_fields()
        if not is_valid:
            return

        try:
            new_id = self.service.create(data)
            messagebox.showinfo("Éxito", f"Registro de {self.title} creado exitosamente con ID {new_id}.")
            self.load_data()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error al Crear", f"No se pudo guardar el registro: {e}")

    def on_update(self):
        """Flujo para actualizar un registro existente."""
        if not self.selected_id:
            messagebox.showwarning(
                "Manejo de Error de Selección",
                "Debe seleccionar un registro de la tabla antes de presionar 'Actualizar'."
            )
            return

        is_valid, data = self.validate_fields()
        if not is_valid:
            return

        try:
            updated = self.service.update(self.selected_id, data)
            if updated:
                messagebox.showinfo("Éxito", f"Registro con ID {self.selected_id} actualizado correctamente.")
                self.load_data()
                self.clear_form()
            else:
                messagebox.showwarning("Advertencia", "No se encontró el registro para actualizar.")
        except Exception as e:
            messagebox.showerror("Error al Actualizar", f"No se pudo actualizar el registro: {e}")

    def on_delete(self):
        """Flujo para eliminar un registro."""
        if not self.selected_id:
            messagebox.showwarning(
                "Manejo de Error de Selección",
                "Debe seleccionar un registro de la tabla antes de presionar 'Eliminar'."
            )
            return

        confirm = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el registro ID {self.selected_id} de {self.title}?"
        )
        if not confirm:
            return

        try:
            deleted = self.service.delete(self.selected_id)
            if deleted:
                messagebox.showinfo("Éxito", f"Registro con ID {self.selected_id} eliminado correctamente.")
                self.load_data()
                self.clear_form()
            else:
                messagebox.showwarning("Advertencia", "No se encontró el registro para eliminar.")
        except Exception as e:
            messagebox.showerror("Error al Eliminar", f"No se pudo eliminar el registro: {e}")
