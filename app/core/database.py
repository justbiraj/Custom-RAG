from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.types import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.core.config import POSTGRES_URL


Base = declarative_base()
engine = create_engine(POSTGRES_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=True)
    chunk_strategy = Column(String, nullable=True)
    embedding_model = Column(String, nullable=True)
    upload_time = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String, nullable=True)

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
init_db()
