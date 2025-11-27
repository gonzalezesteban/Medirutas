# modules/cobro_manager.py
from database import get_db_conn
from datetime import date, datetime
import json

class CobroManager:
    def __init__(self):
        self.conn = get_db_conn()

    def _company_id(self, company_code):
        c = self.conn.cursor()
        c.execute("SELECT id FROM companies WHERE code = ?", (company_code,))
        r = c.fetchone()
        return r["id"] if r else None

    def get_cuentas_cobro(self, company_code):
        """
        Retorna lista de billing_records (id, month_year, total_amount)
        """
        comp_id = self._company_id(company_code)
        if not comp_id:
            return []
        c = self.conn.cursor()
        c.execute("SELECT id, month_year, total_amount FROM billing_records WHERE company_id = ? ORDER BY month_year DESC", (comp_id,))
        return [(r["id"], r["month_year"], r["total_amount"]) for r in c.fetchall()]

    def get_detalle_cuenta_cobro(self, company_code, billing_id):
        """
        Retorna una representación legible del details_json.
        """
        comp_id = self._company_id(company_code)
        if not comp_id:
            return None
        c = self.conn.cursor()
        c.execute("SELECT details_json FROM billing_records WHERE company_id = ? AND id = ?", (comp_id, billing_id))
        r = c.fetchone()
        if not r:
            return None
        details = json.loads(r["details_json"] or "{}")
        # normalizar a lista de tuplas (ruta/servicio, valor, fecha) para compatibilidad con la UI previa
        result = []
        for svc, metrics in details.items():
            cantidad = metrics.get("cantidad_servicios", 0)
            horas = metrics.get("horas_trab", 0)
            peajes = metrics.get("peajes_total", 0)
            result.append((svc, cantidad, horas, peajes))
        return result

    def get_cuentas_cobro_usuario(self, company_code, user_id):
        comp_id = self._company_id(company_code)
        if not comp_id:
            return []
        c = self.conn.cursor()
        c.execute("SELECT month_year, total_amount FROM billing_records WHERE company_id = ? AND driver_user_id = ? ORDER BY month_year DESC", (comp_id, user_id))
        return [(r["month_year"], r["total_amount"]) for r in c.fetchall()]

    def get_detalle_cobro(self, company_code, user_id, month_year):
        """
        Retorna lista de (servicio, cantidad, horas, peajes) para el driver en el mes dado.
        """
        comp_id = self._company_id(company_code)
        if not comp_id:
            return []
        c = self.conn.cursor()
        c.execute("SELECT details_json FROM billing_records WHERE company_id = ? AND driver_user_id = ? AND month_year = ?", (comp_id, user_id, month_year))
        r = c.fetchone()
        if not r:
            return []
        details = json.loads(r["details_json"] or "{}")
        out = []
        for svc, metrics in details.items():
            out.append((svc, metrics.get("cantidad_servicios",0), metrics.get("horas_trab",0.0), metrics.get("peajes_total",0.0)))
        return out

    def generate_billing_for_month(self, company_code, month_year=None):
        """
        Genera registros de billing_records para todos los conductores en la compañía
        para el mes especificado (YYYY-MM). Si month_year None -> mes actual.
        Fórmula: Total = Σ( (horas_trabajadas * costo_hora) + peajes )
        """
        comp_id = self._company_id(company_code)
        if not comp_id:
            return False
        if month_year is None:
            month_year = date.today().strftime("%Y-%m")
        c = self.conn.cursor()
        # obtener conductores que tuvieron rutas en ese mes
        c.execute("SELECT DISTINCT driver_user_id FROM routes WHERE company_id = ? AND substr(date,1,7) = ?", (comp_id, month_year))
        drivers = [r["driver_user_id"] for r in c.fetchall() if r["driver_user_id"]]
        for d in drivers:
            # obtener rutas del mes para conductor
            c.execute("SELECT id, service_id FROM routes WHERE company_id = ? AND driver_user_id = ? AND substr(date,1,7) = ?", (comp_id, d, month_year))
            routes = c.fetchall()
            details = {}
            total_all = 0.0
            for rt in routes:
                rid = rt["id"]
                sid = rt["service_id"]
                # obtener info servicio
                c.execute("SELECT name, cost_per_hour FROM services WHERE id = ?", (sid,))
                srow = c.fetchone()
                svc_name = srow["name"] if srow else f"service_{sid}"
                cost_hour = srow["cost_per_hour"] if srow else 0.0
                # obtener documentos inicio/final para esta ruta y conductor
                c.execute("SELECT type, extra_json FROM documents WHERE route_id = ? AND user_id = ?", (rid, d))
                docs = c.fetchall()
                hora_inicio = None; hora_fin = None; peajes_sum = 0.0
                for doc in docs:
                    extra = json.loads(doc["extra_json"] or "{}")
                    if doc["type"] == "inicio":
                        hora_inicio = extra.get("hora")
                    elif doc["type"] == "final":
                        hora_fin = extra.get("hora")
                        peajes = extra.get("peajes", [])
                        # sumar peajes (acepta lista de strings/numeros)
                        try:
                            peajes_sum += sum([float(x) for x in peajes if str(x).strip()!=''])
                        except:
                            pass
                hours_worked = 0.0
                if hora_inicio and hora_fin:
                    try:
                        fmt = "%H:%M"
                        h1 = datetime.strptime(hora_inicio, fmt)
                        h2 = datetime.strptime(hora_fin, fmt)
                        diff = (h2 - h1).seconds / 3600.0
                        if diff < 0:
                            diff += 24.0
                        hours_worked = diff
                    except:
                        hours_worked = 0.0
                det = details.setdefault(svc_name, {"cantidad_servicios":0, "horas_trab":0.0, "peajes_total":0.0, "cost_per_hour": cost_hour})
                det["cantidad_servicios"] += 1
                det["horas_trab"] += hours_worked
                det["peajes_total"] += peajes_sum
                total_service = (hours_worked * cost_hour) + peajes_sum
                total_all += total_service
            # insertar billing record
            br_details_json = json.dumps(details, ensure_ascii=False)
            c.execute("INSERT INTO billing_records (company_id, driver_user_id, month_year, details_json, total_amount) VALUES (?, ?, ?, ?, ?)",
                      (comp_id, d, month_year, br_details_json, float(total_all)))
            self.conn.commit()
        return True
