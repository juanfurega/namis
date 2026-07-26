import streamlit as st
from sqlalchemy import create_engine, text

# Construir la URL de conexión desde secrets.toml
host = st.secrets["mysql"]["host"]
port = st.secrets["mysql"]["port"]
database = st.secrets["mysql"]["database"]
user = st.secrets["mysql"]["user"]
password = st.secrets["mysql"]["password"]

connection_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"

try:
    # Crear el engine de SQLAlchemy
    engine = create_engine(connection_url)
    
    # Leer el script SQL
    with open("add_a_la_venta_column.sql", "r") as file:
        sql_script = file.read()
    
    # Ejecutar el script SQL
    with engine.connect() as connection:
        connection.execute(text(sql_script))
        connection.commit()
    
    print("Columna 'a_la_venta' agregada exitosamente a la tabla 'productos'")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    print(traceback.format_exc())
