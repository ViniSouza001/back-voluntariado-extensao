from sqlalchemy.orm import sessionmaker
from database.database import db

def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()