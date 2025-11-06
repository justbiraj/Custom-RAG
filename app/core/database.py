from sqlalcemy import create_engine, column, Integer, String, Datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.core.config import POSTGRES_URL


Base = declarative_base()
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Document(Base):
    __tablename__ = "documents"

    id = column(Integer, primary_key=True, index=True)
    filename = column(String, index=True, nullable=True)
    chunk_strategy = column(String, nullable=True)
    embedding_model = column(String, nullable=True)
    upload_time = column(Datetime, default=datetime.utcnow)

class Booking(Base):
    __tablename__ = "bookings"

    id = column(Integer, primary_key=True, index=True)
    name = column(String, nullable=False)
    email = column(String, nullable=False)
    date = column(String, nullable=False)
    time = column(String, nullable=False)
    
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()