import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..database.database import get_database, Base
from ..model.models import Medico

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_hospital.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_database():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_database] = override_get_database

client = TestClient(app)

# Test data
MEDICO_TEST_DATA = {
    "nome": "Dr. João Silva",
    "crm": "12345-SP",
    "especialidade": "Cardiologia",
    "email": "joao.silva@hospital.com",
    "senha": "senha123",
    "hospital_id": 1
}

MEDICO_UPDATE_DATA = {
    "nome": "Dr. João Silva Santos",
    "especialidade": "Cardiologia Pediátrica"
}


class TestMedico:
    """Testes para a entidade Médico"""
    
    def setup_method(self):
        """Setup para cada teste"""
        Base.metadata.create_all(bind=engine)
    
    def teardown_method(self):
        """Cleanup após cada teste"""
        Base.metadata.drop_all(bind=engine)
    
    def test_create_medico_success(self):
        """Teste de criação de médico com sucesso"""
        response = client.post("/api/medicos/", json=MEDICO_TEST_DATA)
        assert response.status_code == 201
        
        data = response.json()
        assert data["nome"] == MEDICO_TEST_DATA["nome"]
        assert data["crm"] == MEDICO_TEST_DATA["crm"]
        assert data["especialidade"] == MEDICO_TEST_DATA["especialidade"]
        assert data["email"] == MEDICO_TEST_DATA["email"]
        assert "id" in data
    
    def test_create_medico_duplicate_crm(self):
        """Teste de criação de médico com CRM duplicado"""
        # Criar primeiro médico
        client.post("/api/medicos/", json=MEDICO_TEST_DATA)
        
        # Tentar criar médico com mesmo CRM
        duplicate_data = MEDICO_TEST_DATA.copy()
        duplicate_data["email"] = "outro@hospital.com"
        
        response = client.post("/api/medicos/", json=duplicate_data)
        assert response.status_code == 400
        assert "CRM já cadastrado" in response.json()["detail"]
    
    def test_create_medico_duplicate_email(self):
        """Teste de criação de médico com email duplicado"""
        # Criar primeiro médico
        client.post("/api/medicos/", json=MEDICO_TEST_DATA)
        
        # Tentar criar médico com mesmo email
        duplicate_data = MEDICO_TEST_DATA.copy()
        duplicate_data["crm"] = "54321-RJ"
        
        response = client.post("/api/medicos/", json=duplicate_data)
        assert response.status_code == 400
        assert "Email já cadastrado" in response.json()["detail"]
    
    def test_get_all_medicos(self):
        """Teste de busca de todos os médicos"""
        # Criar alguns médicos
        client.post("/api/medicos/", json=MEDICO_TEST_DATA)
        
        medico2_data = MEDICO_TEST_DATA.copy()
        medico2_data["crm"] = "54321-RJ"
        medico2_data["email"] = "maria@hospital.com"
        medico2_data["nome"] = "Dra. Maria Santos"
        client.post("/api/medicos/", json=medico2_data)
        
        response = client.get("/api/medicos/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
    
    def test_get_medico_by_id(self):
        """Teste de busca de médico por ID"""
        # Criar médico
        create_response = client.post("/api/medicos/", json=MEDICO_TEST_DATA)
        medico_id = create_response.json()["id"]
        
        # Buscar por ID
        response = client.get(f"/api/medicos/{medico_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == medico_id
        assert data["nome"] == MEDICO_TEST_DATA["nome"]
    
    def test_get_medico_by_id_not_found(self):
        """Teste de busca de médico por ID inexistente"""
        response = client.get("/api/medicos/999")
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]
    
    def test_get_medico_by_crm(self):
        """Teste de busca de médico por CRM"""
        # Criar médico
        client.post("/api/medicos/", json=MEDICO_TEST_DATA)
        
        # Buscar por CRM
        response = client.get(f"/api/medicos/crm/{MEDICO_TEST_DATA['crm']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["crm"] == MEDICO_TEST_DATA["crm"]
    
    def test_get_medicos_by_especialidade(self):
        """Teste de busca de médicos por especialidade"""
        # Criar médico
        client.post("/api/medicos/", json=MEDICO_TEST_DATA)
        
        # Buscar por especialidade
        response = client.get(f"/api/medicos/especialidade/{MEDICO_TEST_DATA['especialidade']}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        assert data[0]["especialidade"] == MEDICO_TEST_DATA["especialidade"]
    
    def test_update_medico(self):
        """Teste de atualização de médico"""
        # Criar médico
        create_response = client.post("/api/medicos/", json=MEDICO_TEST_DATA)
        medico_id = create_response.json()["id"]
        
        # Atualizar médico
        response = client.put(f"/api/medicos/{medico_id}", json=MEDICO_UPDATE_DATA)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nome"] == MEDICO_UPDATE_DATA["nome"]
        assert data["especialidade"] == MEDICO_UPDATE_DATA["especialidade"]
    
    def test_update_medico_not_found(self):
        """Teste de atualização de médico inexistente"""
        response = client.put("/api/medicos/999", json=MEDICO_UPDATE_DATA)
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]
    
    def test_delete_medico(self):
        """Teste de remoção de médico"""
        # Criar médico
        create_response = client.post("/api/medicos/", json=MEDICO_TEST_DATA)
        medico_id = create_response.json()["id"]
        
        # Remover médico
        response = client.delete(f"/api/medicos/{medico_id}")
        assert response.status_code == 204
        
        # Verificar se médico não é mais encontrado
        get_response = client.get(f"/api/medicos/{medico_id}")
        assert get_response.status_code == 404
    
    def test_delete_medico_not_found(self):
        """Teste de remoção de médico inexistente"""
        response = client.delete("/api/medicos/999")
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]
    
    def test_count_medicos(self):
        """Teste de contagem de médicos"""
        # Criar alguns médicos
        client.post("/api/medicos/", json=MEDICO_TEST_DATA)
        
        medico2_data = MEDICO_TEST_DATA.copy()
        medico2_data["crm"] = "54321-RJ"
        medico2_data["email"] = "maria@hospital.com"
        client.post("/api/medicos/", json=medico2_data)
        
        response = client.get("/api/medicos/count/total")
        assert response.status_code == 200
        
        data = response.json()
        assert data["count"] == 2
    
    def test_count_medicos_by_especialidade(self):
        """Teste de contagem de médicos por especialidade"""
        # Criar médico
        client.post("/api/medicos/", json=MEDICO_TEST_DATA)
        
        response = client.get(f"/api/medicos/count/especialidade/{MEDICO_TEST_DATA['especialidade']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["count"] == 1
        assert data["especialidade"] == MEDICO_TEST_DATA["especialidade"]


if __name__ == "__main__":
    pytest.main([__file__])