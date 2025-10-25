# pip install mysql-connector-python flask flask-cors requests
import mysql.connector
from mysql.connector import IntegrityError

DB_CFG = dict(
    host="127.0.0.1",
    user="root",
    password="contrasena",
    database="testdb",
    port=3306,
)

def get_conn():
    # autocommit=True evita tener que llamar conn.commit() manualmente
    return mysql.connector.connect(**DB_CFG, autocommit=True)

def create_paciente(nombre_paciente, email_paciente):
    """
    Crea/actualiza (idempotente) un paciente por email.
    Si el email ya existe, solo actualiza el nombre.
    Retorna: {"status": "created"/"updated", "id_paciente": int}
    """
    sql = """
    INSERT INTO paciente (nombre_paciente, email_paciente)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE nombre_paciente = VALUES(nombre_paciente)
    """
    with get_conn() as conn, conn.cursor() as cur:
        try:
            cur.execute(sql, (nombre_paciente, email_paciente))
            # Para saber el id, buscamos por email (sirve tanto si creó como si actualizó)
            cur.execute("SELECT id_paciente FROM paciente WHERE email_paciente=%s", (email_paciente,))
            row = cur.fetchone()
            status = "created" if cur.rowcount == 1 else "updated"  # Heurística: 1=insert, 2=update (depende de versión)
            return {"status": status, "id_paciente": row[0] if row else None}
        except IntegrityError as e:
            # Aquí solo caeríamos por otra UNIQUE (p.ej. otra columna única)
            return {"status": "error", "error": str(e)}

def read_pacientes():
    with get_conn() as conn, conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT id_paciente, nombre_paciente, email_paciente FROM paciente ORDER BY id_paciente")
        return cur.fetchall()

def update_paciente(id_paciente, nombre_paciente=None, email_paciente=None):
    """
    Actualiza campos; maneja conflicto de UNIQUE en email.
    """
    sets = []
    params = []
    if nombre_paciente is not None:
        sets.append("nombre_paciente=%s")
        params.append(nombre_paciente)
    if email_paciente is not None:
        sets.append("email_paciente=%s")
        params.append(email_paciente)
    if not sets:
        return {"status": "noop"}

    params.append(id_paciente)
    sql = f"UPDATE paciente SET {', '.join(sets)} WHERE id_paciente=%s"

    with get_conn() as conn, conn.cursor() as cur:
        try:
            cur.execute(sql, tuple(params))
            return {"status": "ok", "rows_affected": cur.rowcount}
        except IntegrityError as e:
            # Ej: intentaste poner un email que ya existe en otro paciente
            return {"status": "error", "error": "Email ya registrado en otro paciente", "detail": str(e)}

def delete_paciente(id_paciente):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM paciente WHERE id_paciente=%s", (id_paciente,))
        return {"status": "ok", "rows_affected": cur.rowcount}

# ---------- Ejemplo de uso seguro/idempotente ----------
if __name__ == "__main__":
    print(create_paciente("John Doe", "john@paciente.com"))  # crea o actualiza
    print(create_paciente("Jane Doe", "jane@paciente.com"))  # crea o actualiza

    print("pacientes:", read_pacientes())

    # Actualizar (si cambias el email, puede chocar con otro existente)
    print(update_paciente(1, nombre_paciente="John D.", email_paciente="johndoe@paciente.com"))

    # delete_paciente(2)

    print("pacientes después de cambios:", read_pacientes())
