# Servicios Web CRUD para tabla en MySQL

Este repositorio contiene un ejercicio de conexión a una instancia de **MySQL** que corre dentro de un contenedor Docker en **GitHub Codespaces** utilizando el paquete **mysql-connector-python** para Python.

## Prerequisitos

Antes de comenzar, asegúrate de tener:

- **GitHub Codespaces** habilitado.
- **Docker** ejecutándose en tu Codespace.
- **Python 3** instalado.
- **mysql-connector-python** instalado en tu entorno Python.

### Iniciar la instancia de MySQL en Docker

Para iniciar una instancia de **MySQL** en un contenedor Docker, ejecuta el siguiente comando en la terminal de tu **GitHub Codespace**:

```sh
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=contrasena -e MYSQL_DATABASE=testdb -p 3306:3306 -d mysql:latest
```

### Conectarse al contenedor a través de la herramienta de linea de comandos
```sh
docker exec -it mysql-container mysql -u root -pcontrasena
```
Luego, ingresa la contraseña que configuraste (contrasena).

### Dentro de mysql ejecuta
```sh
USE testdb;
```

```sh
CREATE TABLE paciente (
    id_paciente INT AUTO_INCREMENT PRIMARY KEY,
    nombre_paciente VARCHAR(100) NOT NULL,
    email_paciente VARCHAR(100) UNIQUE NOT NULL
);
```
**Para salir escriba *quit*** y presione enter

# Probar código python que se conecta a servidor

### En la terminal ejecuta

Instalamos las librerías necesarias para nuestros códigos
```sh
pip install mysql-connector-python flask flask-cors requests
```

Ejecutamos un programa de python que genera y modifica algunos registros
```sh
python crud.py
```
Esto creará un par de registros en la tabla

# Probar servicios web

## Prerequisitos

- Existe la table paciente


### Ejecución de servidor de servicios web

Ejecuta el siguiente comando en la terminal de tu **GitHub Codespace**:

```sh
cd webservices
```

```sh
python ws_crud.py
```

Esto ejecutará los servicios web, puerto 8000

### Ejemplos para consumir servicios web desde la terminal

Abra **otra terminal**  (no cierre la terminal que está ejecutando el servidor), y ejecute el siguiente comando para obtener todos los pacientes:
```sh
curl -X GET http://127.0.0.1:8000/pacientes
```
Agregar un paciente:
```sh
curl -X POST http://127.0.0.1:8000/pacientes -H "Content-Type: application/json" -d '{"nombre_paciente": "Juan Lopez", "email_paciente": "juan@gmail.com"}'
```

Actualizar un paciente:
```sh
curl -X PUT http://127.0.0.1:8000/pacientes/1 -H "Content-Type: application/json" -d '{"nombre_paciente": "Jonh R. Doe", "email_paciente": "johndoe123gmail.com", "age": 26}'
```

Borrar un paciente:
```sh
curl -X DELETE http://127.0.0.1:8000/pacientes/3
```

# Respaldo y restauración de base de datos
Respaldo
```sh
docker exec mysql-container mysqldump -u root -pcontrasena testdb > backup.sql
```

Restauración
```sh
docker exec -i mysql-container mysql -u root -pcontrasena testdb < backup.sql
```
