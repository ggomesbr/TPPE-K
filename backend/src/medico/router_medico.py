from sqlalchemy.orm import Session
from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from ..database.database import get_database
from ..model.models import Medico
from ..security import hash_password
from .repository_medico import MedicoRepository
from .schema_medico import MedicoRequest, MedicoResponse, MedicoUpdate

# Tables will be created in main.py startup event

router = APIRouter(
    prefix="/medicos",
    tags=["medicos"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/", 
    response_model=MedicoResponse, 
    status_code=status.HTTP_201_CREATED
)
def create_medico(
    request: MedicoRequest, 
    database: Session = Depends(get_database)
):
    """Cria e salva um novo médico"""
    
    # Verificar se CRM já existe
    if MedicoRepository.exists_by_crm(database, request.crm):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CRM já cadastrado no sistema"
        )
    
    # Verificar se email já existe
    if MedicoRepository.exists_by_email(database, request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado no sistema"
        )
    
    # Criar dados do médico com senha hasheada
    medico_data = request.model_dump()
    medico_data["senha"] = hash_password(medico_data["senha"])
    
    # Criar médico
    medico = MedicoRepository.save(database, Medico(**medico_data))
    return MedicoResponse.model_validate(medico)


@router.get("/", response_model=List[MedicoResponse])
def find_all_medicos(database: Session = Depends(get_database)):
    """Busca todos os médicos"""
    medicos = MedicoRepository.find_all(database)
    return [MedicoResponse.model_validate(medico) for medico in medicos]


@router.get("/{medico_id}", response_model=MedicoResponse)
def find_medico_by_id(
    medico_id: int, 
    database: Session = Depends(get_database)
):
    """Busca médico por ID"""
    medico = MedicoRepository.find_by_id(database, medico_id)
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    return MedicoResponse.model_validate(medico)


@router.get("/crm/{crm}", response_model=MedicoResponse)
def find_medico_by_crm(
    crm: str, 
    database: Session = Depends(get_database)
):
    """Busca médico por CRM"""
    medico = MedicoRepository.find_by_crm(database, crm)
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    return MedicoResponse.model_validate(medico)


@router.get("/especialidade/{especialidade}", response_model=List[MedicoResponse])
def find_medicos_by_especialidade(
    especialidade: str, 
    database: Session = Depends(get_database)
):
    """Busca médicos por especialidade"""
    medicos = MedicoRepository.find_by_especialidade(database, especialidade)
    return [MedicoResponse.model_validate(medico) for medico in medicos]


@router.put("/{medico_id}", response_model=MedicoResponse)
def update_medico(
    medico_id: int,
    request: MedicoUpdate,
    database: Session = Depends(get_database)
):
    """Atualiza dados de um médico"""
    
    # Verificar se médico existe
    medico = MedicoRepository.find_by_id(database, medico_id)
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    
    # Verificar se CRM já existe (excluindo o próprio médico)
    if request.crm and MedicoRepository.exists_by_crm(database, request.crm, medico_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CRM já cadastrado para outro médico"
        )
    
    # Verificar se email já existe (excluindo o próprio médico)
    if request.email and MedicoRepository.exists_by_email(database, request.email, medico_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado para outro médico"
        )
    
    # Atualizar campos fornecidos
    update_data = request.model_dump(exclude_unset=True)
    
    # Hash da senha se fornecida
    if "senha" in update_data:
        update_data["senha"] = hash_password(update_data["senha"])
    
    for field, value in update_data.items():
        setattr(medico, field, value)
    
    # Salvar alterações
    medico_atualizado = MedicoRepository.save(database, medico)
    return MedicoResponse.model_validate(medico_atualizado)


@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medico(
    medico_id: int, 
    database: Session = Depends(get_database)
):
    """Remove médico"""
    if not MedicoRepository.exists_by_id(database, medico_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    
    MedicoRepository.delete_by_id(database, medico_id)


@router.get("/count/total")
def count_medicos(database: Session = Depends(get_database)):
    """Conta total de médicos"""
    count = MedicoRepository.count_all(database)
    return {"count": count}


@router.get("/count/especialidade/{especialidade}")
def count_medicos_por_especialidade(
    especialidade: str, 
    database: Session = Depends(get_database)
):
    """Conta médicos por especialidade"""
    count = MedicoRepository.count_by_especialidade(database, especialidade)
    return {"count": count, "especialidade": especialidade}