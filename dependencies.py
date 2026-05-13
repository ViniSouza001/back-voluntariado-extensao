from sqlalchemy.orm import sessionmaker
from database.database import db

def get_session():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()