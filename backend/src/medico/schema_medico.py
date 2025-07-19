from typing import Optional
from pydantic import BaseModel, EmailStr


class MedicoBase(BaseModel):
    """Classe base para definir os modelos do médico"""
    nome: str
    crm: str
    especialidade: str
    email: EmailStr
    hospital_id: int


class MedicoRequest(MedicoBase):
    """Modelo para requisições de criação de médico"""
    senha: str


class MedicoResponse(MedicoBase):
    """Modelo para respostas da API de médico"""
    id: int
    
    class Config:
        from_attributes = True  # Pydantic v2 syntax (was orm_mode = True)


class MedicoUpdate(BaseModel):
    """Modelo para atualização parcial de médico"""
    nome: Optional[str] = None
    crm: Optional[str] = None
    especialidade: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    hospital_id: Optional[int] = None