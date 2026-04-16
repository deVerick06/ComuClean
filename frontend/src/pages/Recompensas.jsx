import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import './Recompensas.css';

export default function Recompensas() {
  const { usuario, carregarPerfil } = useAuth();
  const [recompensas, setRecompensas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [resgatando, setResgatando] = useState(null);
  const [mensagem, setMensagem] = useState(null);

  useEffect(() => {
    carregarRecompensas();
  }, []);

  async function carregarRecompensas() {
    try {
      const { data } = await api.get('/recompensas');
      setRecompensas(data);
    } catch (err) {
      console.error('Erro ao carregar recompensas:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleResgatar(recompensa) {
    setResgatando(recompensa.id);
    setMensagem(null);
    try {
      await api.post(`/recompensas/${recompensa.id}/resgatar`);
      setMensagem({ tipo: 'sucesso', texto: `"${recompensa.nome}" resgatado com sucesso!` });
      await carregarPerfil();
      await carregarRecompensas();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Erro ao resgatar recompensa';
      setMensagem({ tipo: 'erro', texto: detail });
    } finally {
      setResgatando(null);
    }
  }

  if (loading) {
    return (
      <div className="page recompensas-page">
        <p className="recompensas-loading">Carregando recompensas...</p>
      </div>
    );
  }

  return (
    <div className="page recompensas-page">
      <div className="recompensas-header">
        <div>
          <h1>Recompensas</h1>
          <p className="recompensas-subtitle">Troque seus pontos por premios</p>
        </div>
        <div className="recompensas-saldo">
          <span className="recompensas-saldo-valor">{usuario?.pontos || 0}</span>
          <span className="recompensas-saldo-label">pontos</span>
        </div>
      </div>

      {mensagem && (
        <div className={`recompensas-msg recompensas-msg-${mensagem.tipo}`}>
          {mensagem.texto}
        </div>
      )}

      {recompensas.length === 0 ? (
        <div className="recompensas-empty card">
          <p>Nenhuma recompensa disponivel no momento</p>
        </div>
      ) : (
        <div className="recompensas-grid">
          {recompensas.map((r) => {
            const podePagar = (usuario?.pontos || 0) >= r.pontos_necessarios;
            const esgotado = r.estoque <= 0;

            return (
              <div key={r.id} className="recompensa-card card">
                <div className="recompensa-info">
                  <h3 className="recompensa-nome">{r.nome}</h3>
                  {r.descricao && (
                    <p className="recompensa-desc">{r.descricao}</p>
                  )}
                  <div className="recompensa-meta">
                    <span className="recompensa-custo">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                      </svg>
                      {r.pontos_necessarios} pontos
                    </span>
                    <span className="recompensa-estoque">
                      {r.estoque} {r.estoque === 1 ? 'disponivel' : 'disponiveis'}
                    </span>
                  </div>
                </div>
                <button
                  className="btn btn-primary recompensa-btn"
                  disabled={!podePagar || esgotado || resgatando === r.id}
                  onClick={() => handleResgatar(r)}
                >
                  {resgatando === r.id
                    ? 'Resgatando...'
                    : esgotado
                      ? 'Esgotado'
                      : !podePagar
                        ? 'Pontos insuficientes'
                        : 'Resgatar'}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
