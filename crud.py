# pip install mysql-connector-python flask flask-cors requests
import mysql.connector

# Configurar conexión
conn = mysql.connector.connect(
    host="127.0.0.1",  # Docker expone en localhost
    user="root",
    password="contrasena",
    database="testdb",
    port=3306  # Puerto mapeado en Docker
)
cursor = conn.cursor()

# Crear un paciente
def create_paciente(nombre_paciente, email_paciente):
    cursor.execute("INSERT INTO paciente (nombre_paciente, email_paciente) VALUES (%s, %s)", 
                   (nombre_paciente, email_paciente))
    conn.commit()

# Leer todos los pacientes
def read_paciente():
    cursor.execute("SELECT * FROM paciente")
    return cursor.fetchall()

# Actualizar un paciente
def update_paciente(id_paciente, nombre_paciente, email_paciente):
    cursor.execute("UPDATE paciente SET nombre_paciente=%s, email_paciente=%s WHERE id_paciente=%s", 
                   (nombre_paciente, email_paciente, id_paciente))
    conn.commit()

# Eliminar un paciente
def delete_paciente(id_paciente):
    cursor.execute("DELETE FROM paciente WHERE id_paciente=%s", (id_paciente,))
    conn.commit()

# Ejemplo de uso
create_paciente("John Doe", "john@paciente.com")
create_paciente("Jane Doe", "jane@paciente.com")

print("pacientes:", read_paciente())

update_paciente(1, "John. D", "johndoe@paciente.com")
#delete_paciente(2)

print("pacientes después de cambios:", read_pacientes())

cursor.close()
conn.close()
