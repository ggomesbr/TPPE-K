from sqlalchemy.orm import Session
from ..model.models import Medico
from typing import List, Optional


class MedicoRepository:
    """Repository para operações de banco de dados do médico"""
    
    @staticmethod
    def find_all(database: Session) -> List[Medico]:
        """Função para fazer uma query de todos os médicos da DB"""
        return database.query(Medico).all()
    
    @staticmethod
    def save(database: Session, medico: Medico) -> Medico:
        """Função para salvar um objeto médico na DB"""
        if medico.id:
            database.merge(medico)
        else:
            database.add(medico)
        database.commit()
        database.refresh(medico)
        return medico
    
    @staticmethod
    def find_by_id(database: Session, medico_id: int) -> Optional[Medico]:
        """Função para fazer uma query por ID de um médico na DB"""
        return database.query(Medico).filter(Medico.id == medico_id).first()
    
    @staticmethod
    def find_by_crm(database: Session, crm: str) -> Optional[Medico]:
        """Função para fazer uma query por CRM de um médico na DB"""
        return database.query(Medico).filter(Medico.crm == crm).first()
    
    @staticmethod
    def find_by_email(database: Session, email: str) -> Optional[Medico]:
        """Função para fazer uma query por email de um médico na DB"""
        return database.query(Medico).filter(Medico.email == email).first()
    
    @staticmethod
    def find_by_especialidade(database: Session, especialidade: str) -> List[Medico]:
        """Função para buscar médicos por especialidade"""
        return database.query(Medico).filter(
            Medico.especialidade.ilike(f"%{especialidade}%")
        ).all()
    
    @staticmethod
    def exists_by_id(database: Session, medico_id: int) -> bool:
        """Função que verifica se o médico existe pelo ID na DB"""
        medico = database.query(Medico).filter(Medico.id == medico_id).first()
        return medico is not None
    
    @staticmethod
    def exists_by_crm(database: Session, crm: str, exclude_id: Optional[int] = None) -> bool:
        """Função que verifica se já existe um médico com esse CRM"""
        query = database.query(Medico).filter(Medico.crm == crm)
        if exclude_id:
            query = query.filter(Medico.id != exclude_id)
        return query.first() is not None
    
    @staticmethod
    def exists_by_email(database: Session, email: str, exclude_id: Optional[int] = None) -> bool:
        """Função que verifica se já existe um médico com esse email"""
        query = database.query(Medico).filter(Medico.email == email)
        if exclude_id:
            query = query.filter(Medico.id != exclude_id)
        return query.first() is not None
    
    @staticmethod
    def delete_by_id(database: Session, medico_id: int) -> None:
        """Função para deletar um médico da DB"""
        medico = database.query(Medico).filter(Medico.id == medico_id).first()
        if medico:
            database.delete(medico)
            database.commit()
    
    @staticmethod
    def count_all(database: Session) -> int:
        """Função para contar todos os médicos"""
        return database.query(Medico).count()
    
    @staticmethod
    def count_by_especialidade(database: Session, especialidade: str) -> int:
        """Função para contar médicos por especialidade"""
        return database.query(Medico).filter(
            Medico.especialidade.ilike(f"%{especialidade}%")
        ).count()