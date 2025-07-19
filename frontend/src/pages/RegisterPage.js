import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    password: '',
    confirm_password: '',
    role: 'doctor',
    crm: '',
    especialidade: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  
  const { register, error, clearError } = useAuth();

  // Clear error when component mounts or form data changes
  useEffect(() => {
    clearError();
  }, [formData, clearError]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.nome.trim()) {
      errors.nome = 'Nome é obrigatório';
    }

    if (!formData.email.trim()) {
      errors.email = 'Email é obrigatório';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email inválido';
    }

    if (!formData.password) {
      errors.password = 'Senha é obrigatória';
    } else if (formData.password.length < 6) {
      errors.password = 'Senha deve ter pelo menos 6 caracteres';
    }

    if (!formData.confirm_password) {
      errors.confirm_password = 'Confirmação de senha é obrigatória';
    } else if (formData.password !== formData.confirm_password) {
      errors.confirm_password = 'Senhas não coincidem';
    }

    if (formData.role === 'doctor') {
      if (!formData.crm.trim()) {
        errors.crm = 'CRM é obrigatório para médicos';
      }
      if (!formData.especialidade.trim()) {
        errors.especialidade = 'Especialidade é obrigatória para médicos';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (isSubmitting) return;
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const result = await register(formData);
      
      if (!result.success) {
        console.error('Registration failed:', result.error);
      }
      // If successful, AuthContext will handle the redirect
    } catch (error) {
      console.error('Registration error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormValid = formData.nome && formData.email && formData.password && 
                     formData.confirm_password && 
                     (formData.role !== 'doctor' || (formData.crm && formData.especialidade));

  return (
    <div className="form-container">
      <div className="form-card" style={{ maxWidth: '500px' }}>
        <div className="form-header">
          <h1>🏥 Cadastro</h1>
          <p>Crie sua conta no sistema hospitalar</p>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="nome">Nome completo</label>
            <input
              type="text"
              id="nome"
              name="nome"
              className={`form-control ${validationErrors.nome ? 'error' : ''}`}
              value={formData.nome}
              onChange={handleChange}
              placeholder="Ex: Dr. João Silva"
              required
              disabled={isSubmitting}
            />
            {validationErrors.nome && (
              <div className="alert alert-error" style={{ marginTop: '8px', marginBottom: '0' }}>
                {validationErrors.nome}
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              className={`form-control ${validationErrors.email ? 'error' : ''}`}
              value={formData.email}
              onChange={handleChange}
              placeholder="seu.email@hospital.com"
              required
              autoComplete="email"
              disabled={isSubmitting}
            />
            {validationErrors.email && (
              <div className="alert alert-error" style={{ marginTop: '8px', marginBottom: '0' }}>
                {validationErrors.email}
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="role">Função</label>
            <select
              id="role"
              name="role"
              className="form-control"
              value={formData.role}
              onChange={handleChange}
              disabled={isSubmitting}
            >
              <option value="doctor">Médico</option>
              <option value="nurse">Enfermeiro</option>
              <option value="admin">Administrador</option>
              <option value="user">Usuário</option>
            </select>
          </div>

          {formData.role === 'doctor' && (
            <>
              <div className="form-group">
                <label htmlFor="crm">CRM</label>
                <input
                  type="text"
                  id="crm"
                  name="crm"
                  className={`form-control ${validationErrors.crm ? 'error' : ''}`}
                  value={formData.crm}
                  onChange={handleChange}
                  placeholder="Ex: 12345-SP"
                  required
                  disabled={isSubmitting}
                />
                {validationErrors.crm && (
                  <div className="alert alert-error" style={{ marginTop: '8px', marginBottom: '0' }}>
                    {validationErrors.crm}
                  </div>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="especialidade">Especialidade</label>
                <input
                  type="text"
                  id="especialidade"
                  name="especialidade"
                  className={`form-control ${validationErrors.especialidade ? 'error' : ''}`}
                  value={formData.especialidade}
                  onChange={handleChange}
                  placeholder="Ex: Cardiologia"
                  required
                  disabled={isSubmitting}
                />
                {validationErrors.especialidade && (
                  <div className="alert alert-error" style={{ marginTop: '8px', marginBottom: '0' }}>
                    {validationErrors.especialidade}
                  </div>
                )}
              </div>
            </>
          )}

          <div className="form-group">
            <label htmlFor="password">Senha</label>
            <input
              type="password"
              id="password"
              name="password"
              className={`form-control ${validationErrors.password ? 'error' : ''}`}
              value={formData.password}
              onChange={handleChange}
              placeholder="Mínimo 6 caracteres"
              required
              autoComplete="new-password"
              disabled={isSubmitting}
            />
            {validationErrors.password && (
              <div className="alert alert-error" style={{ marginTop: '8px', marginBottom: '0' }}>
                {validationErrors.password}
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="confirm_password">Confirmar senha</label>
            <input
              type="password"
              id="confirm_password"
              name="confirm_password"
              className={`form-control ${validationErrors.confirm_password ? 'error' : ''}`}
              value={formData.confirm_password}
              onChange={handleChange}
              placeholder="Digite a senha novamente"
              required
              autoComplete="new-password"
              disabled={isSubmitting}
            />
            {validationErrors.confirm_password && (
              <div className="alert alert-error" style={{ marginTop: '8px', marginBottom: '0' }}>
                {validationErrors.confirm_password}
              </div>
            )}
          </div>

          <button
            type="submit"
            className={`btn btn-primary ${isSubmitting ? 'btn-loading' : ''}`}
            disabled={!isFormValid || isSubmitting}
          >
            {isSubmitting ? 'Cadastrando...' : 'Cadastrar'}
          </button>
        </form>

        <div className="form-link">
          <p>
            Já tem uma conta?{' '}
            <Link to="/login">Faça login aqui</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
