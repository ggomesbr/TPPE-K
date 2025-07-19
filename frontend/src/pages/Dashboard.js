import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { hospitalService } from '../services/api';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDoctors();
  }, []);

  const loadDoctors = async () => {
    try {
      setLoading(true);
      const response = await hospitalService.getDoctors();
      setDoctors(response);
      setError(null);
    } catch (error) {
      console.error('Failed to load doctors:', error);
      setError('Erro ao carregar médicos');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    if (window.confirm('Tem certeza que deseja sair?')) {
      logout();
    }
  };

  const formatRole = (role) => {
    const roles = {
      'doctor': 'Médico',
      'nurse': 'Enfermeiro',
      'admin': 'Administrador',
      'user': 'Usuário'
    };
    return roles[role] || role;
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1 className="dashboard-title">🏥 Sistema Hospitalar</h1>
        
        <div className="user-info">
          <span className="user-name">
            Olá, <strong>{user?.nome}</strong> ({formatRole(user?.role)})
          </span>
          <button onClick={handleLogout} className="logout-btn">
            Sair
          </button>
        </div>
      </header>

      <main className="dashboard-content">
        <div className="welcome-card">
          <h2>Bem-vindo ao Dashboard!</h2>
          <p>
            Você está logado como <strong>{formatRole(user?.role)}</strong>.
            {user?.crm && ` CRM: ${user.crm}`}
            {user?.especialidade && ` - ${user.especialidade}`}
          </p>
        </div>

        {/* Doctors Section */}
        <div style={{ marginTop: '40px' }}>
          <div style={{ 
            background: 'white', 
            padding: '30px', 
            borderRadius: '12px', 
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)' 
          }}>
            <h3 style={{ marginBottom: '20px', color: '#333' }}>👨‍⚕️ Médicos Cadastrados</h3>
            
            {loading && (
              <div style={{ textAlign: 'center', padding: '20px' }}>
                <div className="spinner"></div>
                <p>Carregando médicos...</p>
              </div>
            )}

            {error && (
              <div className="alert alert-error">
                {error}
              </div>
            )}

            {!loading && !error && doctors.length === 0 && (
              <div className="alert alert-info">
                Nenhum médico cadastrado no sistema.
              </div>
            )}

            {!loading && !error && doctors.length > 0 && (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ 
                  width: '100%', 
                  borderCollapse: 'collapse',
                  fontSize: '14px'
                }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f8f9fa' }}>
                      <th style={{ 
                        padding: '12px', 
                        textAlign: 'left', 
                        border: '1px solid #dee2e6',
                        fontWeight: '600'
                      }}>
                        Nome
                      </th>
                      <th style={{ 
                        padding: '12px', 
                        textAlign: 'left', 
                        border: '1px solid #dee2e6',
                        fontWeight: '600'
                      }}>
                        CRM
                      </th>
                      <th style={{ 
                        padding: '12px', 
                        textAlign: 'left', 
                        border: '1px solid #dee2e6',
                        fontWeight: '600'
                      }}>
                        Especialidade
                      </th>
                      <th style={{ 
                        padding: '12px', 
                        textAlign: 'left', 
                        border: '1px solid #dee2e6',
                        fontWeight: '600'
                      }}>
                        Email
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {doctors.map((doctor) => (
                      <tr key={doctor.id}>
                        <td style={{ 
                          padding: '12px', 
                          border: '1px solid #dee2e6' 
                        }}>
                          {doctor.nome}
                        </td>
                        <td style={{ 
                          padding: '12px', 
                          border: '1px solid #dee2e6' 
                        }}>
                          {doctor.crm}
                        </td>
                        <td style={{ 
                          padding: '12px', 
                          border: '1px solid #dee2e6' 
                        }}>
                          {doctor.especialidade}
                        </td>
                        <td style={{ 
                          padding: '12px', 
                          border: '1px solid #dee2e6' 
                        }}>
                          {doctor.email}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {!loading && !error && (
              <div style={{ marginTop: '20px', textAlign: 'center' }}>
                <button 
                  onClick={loadDoctors}
                  className="btn btn-secondary"
                  style={{ width: 'auto', padding: '8px 16px' }}
                >
                  🔄 Atualizar Lista
                </button>
              </div>
            )}
          </div>
        </div>

        {/* User Info Section */}
        <div style={{ marginTop: '40px' }}>
          <div style={{ 
            background: 'white', 
            padding: '30px', 
            borderRadius: '12px', 
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)' 
          }}>
            <h3 style={{ marginBottom: '20px', color: '#333' }}>👤 Suas Informações</h3>
            
            <div style={{ display: 'grid', gap: '16px' }}>
              <div>
                <strong>Nome:</strong> {user?.nome}
              </div>
              <div>
                <strong>Email:</strong> {user?.email}
              </div>
              <div>
                <strong>Função:</strong> {formatRole(user?.role)}
              </div>
              {user?.crm && (
                <div>
                  <strong>CRM:</strong> {user.crm}
                </div>
              )}
              {user?.especialidade && (
                <div>
                  <strong>Especialidade:</strong> {user.especialidade}
                </div>
              )}
              <div>
                <strong>Status:</strong> <span style={{ color: 'green' }}>Ativo</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
