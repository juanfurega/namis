import pymysql
import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)

# Obtener DATABASE_URL
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://user:password@127.0.0.1:3306/namis_yogur",
)

# Parsear DATABASE_URL
# Formato: mysql+pymysql://user:password@host:port/database?params
db_url = DATABASE_URL.replace("mysql+pymysql://", "")
user_pass, rest = db_url.split("@")
user, password = user_pass.split(":")
host_port_db, _ = rest.split("?") if "?" in rest else (rest, "")
host_port, database = host_port_db.split("/")
host, port = host_port.split(":")

# Conectar a MySQL
connection = pymysql.connect(
    host=host,
    port=int(port),
    user=user,
    password=password,
    database=database
)

try:
    with connection.cursor() as cursor:
        # Verificar si la columna ya existe
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'ventas' AND COLUMN_NAME = 'es_deudor'
        """, (database,))
        result = cursor.fetchone()
        
        if result:
            print("La columna 'es_deudor' ya existe en la tabla 'ventas'")
        else:
            # Agregar la columna
            cursor.execute("""
                ALTER TABLE ventas ADD COLUMN es_deudor BOOLEAN DEFAULT FALSE
            """)
            connection.commit()
            print("Columna 'es_deudor' agregada exitosamente a la tabla 'ventas'")
            
finally:
    connection.close()
