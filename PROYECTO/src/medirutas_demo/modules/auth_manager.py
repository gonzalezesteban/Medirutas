from database import get_db

class AuthManager:
    def __init__(self):
        self.db = get_db()

    def login(self, correo, password):
        query = """
            SELECT id, nombre, correo, rol_id, empresa_id
            FROM usuarios
            WHERE correo = ? AND password = ?
        """
        result = self.db.query(query, (correo, password))
        return result[0] if result else None

    def register_user(self, nombre, correo, password, empresa_id, rol_id):
        query = """
            INSERT INTO usuarios (nombre, correo, password, empresa_id, rol_id)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.db.execute(query, (nombre, correo, password, empresa_id, rol_id))
