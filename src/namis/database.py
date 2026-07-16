import streamlit as st
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# 1. Armamos la URL leyendo los secretos de Streamlit Cloud
db_user = st.secrets["mysql"]["user"]
db_pass = st.secrets["mysql"]["password"]
db_host = st.secrets["mysql"]["host"]
db_port = st.secrets["mysql"]["port"]
db_name = st.secrets["mysql"]["database"]

DATABASE_URL = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# 2. El resto de tu código queda igual
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

def get_session() -> Session:
    return SessionLocal()

@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
