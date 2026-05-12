from sqlalchemy.orm import sessionmaker
from database.database import db

def take_session():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()
