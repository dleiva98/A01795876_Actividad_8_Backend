from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import pooling, Error

app = Flask(__name__)

# --- Configuración de base de datos ---
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "contrasena",
    "database": "testdb",
}

# Pool de conexiones
pool = pooling.MySQLConnectionPool(pool_name="paciente_pool", pool_size=5, **DB_CONFIG)

def get_conn_cursor():
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    return conn, cursor

def ensure_table():
    sql = """
    CREATE TABLE IF NOT EXISTS paciente (
        id_paciente INT AUTO_INCREMENT PRIMARY KEY,
        nombre_paciente VARCHAR(100) NOT NULL,
        email_paciente VARCHAR(100) UNIQUE NOT NULL
    );
    """
    conn, cur = get_conn_cursor()
    try:
        cur.execute(sql)
        conn.commit()
    finally:
        cur.close()
        conn.close()

# 🔧 Flask 3.x: NO usar @app.before_first_request
# Llamamos directamente una vez al iniciar el módulo/app:
ensure_table()

def bad_request(msg): return jsonify({"error": msg}), 400
def not_found(msg="Recurso no encontrado"): return jsonify({"error": msg}), 404

@app.get("/health")
def health(): return jsonify({"status": "ok"}), 200

@app.get("/pacientes")
def listar_pacientes():
    try:
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return bad_request("limit y offset deben ser enteros")
    sql = """SELECT id_paciente, nombre_paciente, email_paciente
             FROM paciente ORDER BY id_paciente LIMIT %s OFFSET %s"""
    conn, cur = get_conn_cursor()
    try:
        cur.execute(sql, (limit, offset))
        return jsonify(cur.fetchall()), 200
    finally:
        cur.close(); conn.close()

@app.get("/pacientes/<int:id_paciente>")
def obtener_paciente(id_paciente):
    sql = """SELECT id_paciente, nombre_paciente, email_paciente
             FROM paciente WHERE id_paciente = %s"""
    conn, cur = get_conn_cursor()
    try:
        cur.execute(sql, (id_paciente,))
        row = cur.fetchone()
        return (jsonify(row), 200) if row else not_found("Paciente no existe")
    finally:
        cur.close(); conn.close()

@app.post("/pacientes")
def crear_paciente():
    data = request.get_json(silent=True) or {}
    nombre, email = data.get("nombre_paciente"), data.get("email_paciente")
    if not nombre or not email:
        return bad_request("Campos requeridos: nombre_paciente, email_paciente")
    sql = "INSERT INTO paciente (nombre_paciente, email_paciente) VALUES (%s, %s)"
    conn, cur = get_conn_cursor()
    try:
        cur.execute(sql, (nombre, email)); conn.commit()
        return jsonify({"id_paciente": cur.lastrowid,
                        "nombre_paciente": nombre,
                        "email_paciente": email}), 201
    except Error as e:
        if getattr(e, "errno", None) == 1062:
            return jsonify({"error": "email_paciente ya existe"}), 409
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close(); conn.close()

@app.put("/pacientes/<int:id_paciente>")
def actualizar_paciente(id_paciente):
    data = request.get_json(silent=True) or {}
    campos, valores = [], []
    if "nombre_paciente" in data:
        campos.append("nombre_paciente = %s"); valores.append(data["nombre_paciente"])
    if "email_paciente" in data:
        campos.append("email_paciente = %s"); valores.append(data["email_paciente"])
    if not campos: return bad_request("Proporcione al menos un campo para actualizar")
    valores.append(id_paciente)
    sql = f"UPDATE paciente SET {', '.join(campos)} WHERE id_paciente = %s"
    conn, cur = get_conn_cursor()
    try:
        cur.execute(sql, tuple(valores)); conn.commit()
        if cur.rowcount == 0: return not_found("Paciente no existe")
        cur.execute("""SELECT id_paciente, nombre_paciente, email_paciente
                       FROM paciente WHERE id_paciente = %s""", (id_paciente,))
        return jsonify(cur.fetchone()), 200
    except Error as e:
        if getattr(e, "errno", None) == 1062:
            return jsonify({"error": "email_paciente ya existe"}), 409
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close(); conn.close()

@app.delete("/pacientes/<int:id_paciente>")
def eliminar_paciente(id_paciente):
    conn, cur = get_conn_cursor()
    try:
        cur.execute("DELETE FROM paciente WHERE id_paciente = %s", (id_paciente,))
        conn.commit()
        if cur.rowcount == 0: return not_found("Paciente no existe")
        return jsonify({"deleted": True, "id_paciente": id_paciente}), 200
    finally:
        cur.close(); conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
