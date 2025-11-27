# modules/servicio_manager.py
from database import get_db_conn
import sqlite3

class ServicioManager:
    def __init__(self):
        self.conn = get_db_conn()

    def _company_id(self, company_code):
        c = self.conn.cursor()
        c.execute("SELECT id FROM companies WHERE code = ?", (company_code,))
        r = c.fetchone()
        return r["id"] if r else None

    def crear_servicio(self, company_code, nombre, costo_por_hora):
        """
        Crea un servicio para la empresa. Retorna True si se creó, False si ya existe.
        """
        comp_id = self._company_id(company_code)
        if not comp_id:
            return False
        c = self.conn.cursor()
        # Evitar duplicados por nombre dentro de la compañía
        c.execute("SELECT id FROM services WHERE company_id = ? AND name = ?", (comp_id, nombre))
        if c.fetchone():
            return False
        c.execute("INSERT INTO services (company_id, name, cost_per_hour) VALUES (?, ?, ?)",
                  (comp_id, nombre, float(costo_por_hora)))
        self.conn.commit()
        return True

    def get_servicios(self, company_code):
        """
        Retorna lista de tuplas (name, cost_per_hour) para la empresa.
        """
        comp_id = self._company_id(company_code)
        if not comp_id:
            return []
        c = self.conn.cursor()
        c.execute("SELECT name, cost_per_hour FROM services WHERE company_id = ?", (comp_id,))
        return [(r["name"], r["cost_per_hour"]) for r in c.fetchall()]

    def actualizar_servicio(self, company_code, servicio_id, nuevo_nombre, nuevo_costo):
        comp_id = self._company_id(company_code)
        if not comp_id:
            return False
        c = self.conn.cursor()
        c.execute("UPDATE services SET name = ?, cost_per_hour = ? WHERE id = ? AND company_id = ?",
                  (nuevo_nombre, float(nuevo_costo), servicio_id, comp_id))
        self.conn.commit()
        return True

    def eliminar_servicio(self, company_code, servicio_id):
        comp_id = self._company_id(company_code)
        if not comp_id:
            return False
        c = self.conn.cursor()
        c.execute("DELETE FROM services WHERE id = ? AND company_id = ?", (servicio_id, comp_id))
        self.conn.commit()
        return True
