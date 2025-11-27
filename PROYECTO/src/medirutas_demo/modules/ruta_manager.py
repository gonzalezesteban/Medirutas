# modules/ruta_manager.py
from database import get_db_conn
from datetime import date, datetime
import sqlite3

class RutaManager:
    def __init__(self):
        self.conn = get_db_conn()

    def _company_id(self, company_code):
        c = self.conn.cursor()
        c.execute("SELECT id FROM companies WHERE code = ?", (company_code,))
        r = c.fetchone()
        return r["id"] if r else None

    def crear_ruta(self, company_code, nombre, punto_inicio, punto_final, duracion_minutos, driver_user_id=None, service_id=None, day=None, start_time=None):
        """
        Inserta una ruta mínima:
        - routes.start_location = punto_inicio
        - crea 2 stops: inicio y final (final con order_index 1)
        Retorna id de la ruta creada o None si falla.
        """
        comp_id = self._company_id(company_code)
        if not comp_id:
            return None
        c = self.conn.cursor()
        if not day:
            day = date.today().isoformat()
        if not start_time:
            start_time = datetime.now().strftime("%H:%M")
        c.execute(
            "INSERT INTO routes (company_id, service_id, date, start_time, start_location, driver_user_id, created_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (comp_id, service_id, day, start_time, punto_inicio, driver_user_id, None)
        )
        self.conn.commit()
        route_id = c.lastrowid
        # create stops: inicio then final
        c.execute("INSERT INTO stops (route_id, address, lat, lng, order_index) VALUES (?, ?, ?, ?, ?)",
                  (route_id, punto_inicio, "", "", 0))
        c.execute("INSERT INTO stops (route_id, address, lat, lng, order_index) VALUES (?, ?, ?, ?, ?)",
                  (route_id, punto_final, "", "", 1))
        self.conn.commit()
        return route_id

    def get_rutas_conductor(self, company_code, user_id):
        """
        Retorna lista de rutas (date, start_time, start_location, concatenated addresses) para un conductor.
        Cada elemento: (date, start_time, start_location, direcciones_str)
        """
        comp_id = self._company_id(company_code)
        if not comp_id:
            return []
        c = self.conn.cursor()
        c.execute("""
            SELECT r.date, r.start_time, r.start_location, r.id
            FROM routes r
            WHERE r.company_id = ? AND r.driver_user_id = ?
            ORDER BY r.date
        """, (comp_id, user_id))
        rows = c.fetchall()
        result = []
        for r in rows:
            rid = r["id"]
            c.execute("SELECT address FROM stops WHERE route_id = ? ORDER BY order_index", (rid,))
            stops = [s["address"] for s in c.fetchall()]
            direcciones = " | ".join(stops)
            result.append((r["date"], r["start_time"], r["start_location"], direcciones))
        return result

    def asignar_conductor_a_ruta(self, route_id, driver_user_id):
        c = self.conn.cursor()
        c.execute("UPDATE routes SET driver_user_id = ? WHERE id = ?", (driver_user_id, route_id))
        self.conn.commit()
        return True

    def obtener_ruta(self, route_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM routes WHERE id = ?", (route_id,))
        return c.fetchone()
