from database import get_connection

class BaseService:
    """Clase base para servicios CRUD."""
    def __init__(self, table_name, fields):
        self.table_name = table_name
        self.fields = fields  # Lista de nombres de columnas (sin incluir 'id')

    def get_all(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name}")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_by_id(self, item_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def create(self, data):
        columns = ", ".join(self.fields)
        placeholders = ", ".join(["?"] * len(self.fields))
        values = [data.get(field) for field in self.fields]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})",
            values
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id

    def update(self, item_id, data):
        set_clause = ", ".join([f"{field} = ?" for field in self.fields])
        values = [data.get(field) for field in self.fields]
        values.append(item_id)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?",
            values
        )
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def delete(self, item_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (item_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0


class VehiculoService(BaseService):
    def __init__(self):
        super().__init__(
            table_name="vehiculos",
            fields=["patente", "marca", "modelo", "anio"]
        )


class PropietarioService(BaseService):
    def __init__(self):
        super().__init__(
            table_name="propietarios",
            fields=["dni", "nombre", "telefono", "email"]
        )
