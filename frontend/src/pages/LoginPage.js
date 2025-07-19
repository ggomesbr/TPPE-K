import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { login, error, clearError } = useAuth();

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
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    
    try {
      const result = await login(formData.email, formData.password);
      
      if (!result.success) {
        console.error('Login failed:', result.error);
      }
      // If successful, AuthContext will handle the redirect
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormValid = formData.email && formData.password;

  return (
    <div className="form-container">
      <div className="form-card">
        <div className="form-header">
          <h1>🏥 Hospital System</h1>
          <p>Faça login para acessar o sistema</p>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              className="form-control"
              value={formData.email}
              onChange={handleChange}
              placeholder="seu.email@hospital.com"
              required
              autoComplete="email"
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Senha</label>
            <input
              type="password"
              id="password"
              name="password"
              className="form-control"
              value={formData.password}
              onChange={handleChange}
              placeholder="Digite sua senha"
              required
              autoComplete="current-password"
              disabled={isSubmitting}
            />
          </div>

          <button
            type="submit"
            className={`btn btn-primary ${isSubmitting ? 'btn-loading' : ''}`}
            disabled={!isFormValid || isSubmitting}
          >
            {isSubmitting ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <div className="form-link">
          <p>
            Não tem uma conta?{' '}
            <Link to="/register">Cadastre-se aqui</Link>
          </p>
        </div>

        {/* Demo credentials info */}
        <div className="alert alert-info" style={{ marginTop: '24px', fontSize: '12px' }}>
          <strong>Contas de demonstração:</strong><br />
          <strong>Email:</strong> joao.silva@hospital.com<br />
          <strong>Senha:</strong> senha123456<br />
          <em>ou</em><br />
          <strong>Email:</strong> maria.santos@hospital.com<br />
          <strong>Senha:</strong> senha123456
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
