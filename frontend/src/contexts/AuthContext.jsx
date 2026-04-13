import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      carregarPerfil();
    } else {
      setCarregando(false);
    }
  }, []);

  async function carregarPerfil() {
    try {
      const { data } = await api.get('/usuarios/me');
      setUsuario(data);
    } catch {
      localStorage.removeItem('token');
    } finally {
      setCarregando(false);
    }
  }

  async function login(email, senha) {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', senha);

    const { data } = await api.post('/login', params);
    localStorage.setItem('token', data.access_token);
    await carregarPerfil();
  }

  async function registrar(nome, email, senha) {
    await api.post('/usuarios', { nome, email, senha });
    await login(email, senha);
  }

  function logout() {
    localStorage.removeItem('token');
    setUsuario(null);
  }

  return (
    <AuthContext.Provider value={{ usuario, carregando, login, registrar, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth deve ser usado dentro de AuthProvider');
  return ctx;
}
