import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import './Ranking.css';

const medalhas = ['🥇', '🥈', '🥉'];

export default function Ranking() {
  const { usuario } = useAuth();
  const [ranking, setRanking] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarRanking();
  }, []);

  async function carregarRanking() {
    try {
      const { data } = await api.get('/ranking?limite=20');
      setRanking(data);
    } catch (err) {
      console.error('Erro ao carregar ranking:', err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="page ranking-page">
        <p className="ranking-loading">Carregando ranking...</p>
      </div>
    );
  }

  return (
    <div className="page ranking-page">
      <div className="ranking-header">
        <h1>Ranking da Comunidade</h1>
        <p className="ranking-subtitle">Os moradores mais engajados</p>
      </div>

      {ranking.length === 0 ? (
        <div className="ranking-empty card">
          <p>Nenhum morador no ranking ainda</p>
        </div>
      ) : (
        <div className="ranking-list">
          {ranking.map((r) => {
            const isMe = usuario && r.nome === usuario.nome;
            const isTop3 = r.posicao <= 3;

            return (
              <div
                key={r.posicao}
                className={`ranking-item card ${isMe ? 'ranking-item-me' : ''} ${isTop3 ? 'ranking-item-top' : ''}`}
              >
                <div className="ranking-posicao">
                  {isTop3 ? (
                    <span className="ranking-medalha">{medalhas[r.posicao - 1]}</span>
                  ) : (
                    <span className="ranking-numero">{r.posicao}</span>
                  )}
                </div>
                <div className="ranking-info">
                  <span className="ranking-nome">
                    {r.nome}
                    {isMe && <span className="ranking-voce"> (voce)</span>}
                  </span>
                </div>
                <div className="ranking-pontos">
                  <span className="ranking-pontos-valor">{r.pontos}</span>
                  <span className="ranking-pontos-label">pts</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
