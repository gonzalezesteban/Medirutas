# modules/usuario_manager.py
from database import get_db_conn

class UsuarioManager:
    def __init__(self):
        self.conn = get_db_conn()

    def _company_id(self, company_code):
        c = self.conn.cursor()
        c.execute("SELECT id FROM companies WHERE code = ?", (company_code,))
        r = c.fetchone()
        return r["id"] if r else None

    def get_usuarios(self, company_code, role_filter=None):
        """
        Retorna lista de usuarios (id, name, role_name) para la empresa.
        Si role_filter es proporcionado, filtra por rol.
        """
        comp_id = self._company_id(company_code)
        if not comp_id:
            return []
        c = self.conn.cursor()
        if role_filter:
            c.execute("""
                SELECT u.id, u.name, r.name as role_name, r.is_admin
                FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE u.company_id = ? AND r.name LIKE ?
                ORDER BY u.name
            """, (comp_id, f"%{role_filter}%"))
        else:
            c.execute("""
                SELECT u.id, u.name, r.name as role_name, r.is_admin
                FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE u.company_id = ?
                ORDER BY u.name
            """, (comp_id,))
        return [(r["id"], r["name"], r["role_name"], bool(r["is_admin"])) for r in c.fetchall()]

    def get_usuario(self, user_id):
        """
        Retorna información del usuario.
        """
        c = self.conn.cursor()
        c.execute("""
            SELECT u.id, u.name, u.company_id, u.role_id, r.name as role_name, r.is_admin
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.id = ?
        """, (user_id,))
        r = c.fetchone()
        if r:
            return {"id": r["id"], "name": r["name"], "company_id": r["company_id"], 
                   "role_id": r["role_id"], "role_name": r["role_name"], "is_admin": bool(r["is_admin"])}
        return None
