from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Usuario(Base):
    """Modelo para usuários do sistema de autenticação"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    senha = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")  # user, doctor, admin, nurse
    crm = Column(String(20), nullable=True)  # For doctors
    especialidade = Column(String(100), nullable=True)  # For doctors
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reset_token = Column(String(100), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)


class Medico(Base):
    """Modelo para médicos do hospital"""
    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    crm = Column(String(20), nullable=False, unique=True)
    especialidade = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    senha = Column(String(255), nullable=False)
    hospital_id = Column(Integer, nullable=False)  # Removed FK constraint temporarily