import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import './Perfil.css';

const tipoLabels = {
  lixo_comum: 'Lixo comum',
  entulho: 'Entulho',
  reciclavel: 'Reciclavel',
};

const statusLabels = {
  aberta: 'Aberta',
  em_analise: 'Em analise',
  resolvida: 'Resolvida',
};

export default function Perfil() {
  const { usuario, logout } = useAuth();
  const navigate = useNavigate();
  const [denuncias, setDenuncias] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarMinhasDenuncias();
  }, []);

  async function carregarMinhasDenuncias() {
    try {
      const { data } = await api.get('/usuarios/me/denuncias');
      setDenuncias(data);
    } catch (err) {
      console.error('Erro ao carregar denuncias:', err);
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    logout();
    navigate('/login');
  }

  if (!usuario) return null;

  const inicial = usuario.nome.charAt(0).toUpperCase();

  return (
    <div className="page perfil-page">
      <div className="perfil-top">
        <div className="perfil-avatar">{inicial}</div>
        <h1 className="perfil-nome">{usuario.nome}</h1>
        <p className="perfil-email">{usuario.email}</p>

        <div className="perfil-stats">
          <div className="stat-card">
            <span className="stat-value">{usuario.pontos}</span>
            <span className="stat-label">Pontos</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{denuncias.length}</span>
            <span className="stat-label">Denuncias</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">
              {denuncias.filter((d) => d.status === 'resolvida').length}
            </span>
            <span className="stat-label">Resolvidas</span>
          </div>
        </div>
      </div>

      <div className="perfil-section">
        <h2>Minhas denuncias</h2>

        {loading ? (
          <p className="perfil-loading">Carregando...</p>
        ) : denuncias.length === 0 ? (
          <div className="perfil-empty card">
            <p>Voce ainda nao fez nenhuma denuncia</p>
          </div>
        ) : (
          <div className="perfil-list">
            {denuncias.map((d) => (
              <div key={d.id} className="card perfil-denuncia">
                <div className="perfil-denuncia-top">
                  <span className={`badge badge-${d.tipo_lixo}`}>
                    {tipoLabels[d.tipo_lixo]}
                  </span>
                  <span className={`badge badge-${d.status}`}>
                    {statusLabels[d.status]}
                  </span>
                </div>
                {d.descricao && <p className="perfil-denuncia-desc">{d.descricao}</p>}
                <span className="perfil-denuncia-date">
                  {new Date(d.criada_em).toLocaleDateString('pt-BR')}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="perfil-section">
        <button className="btn btn-secondary btn-full" onClick={handleLogout}>
          Sair da conta
        </button>
      </div>
    </div>
  );
}
