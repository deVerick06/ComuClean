import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import api from '../services/api';
import HeatmapLayer from '../components/HeatmapLayer';
import './Home.css';
import 'leaflet/dist/leaflet.css';

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

function criarIcone(status) {
  const cores = {
    aberta: '#3b82f6',
    em_analise: '#f59e0b',
    resolvida: '#22c55e',
  };
  const cor = cores[status] || '#6b7280';

  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      width: 14px;
      height: 14px;
      background: ${cor};
      border: 2.5px solid white;
      border-radius: 50%;
      box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    "></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });
}

function ChangeView({ center }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);
  return null;
}

export default function Home() {
  const [denuncias, setDenuncias] = useState([]);
  const [filtroStatus, setFiltroStatus] = useState('');
  const [view, setView] = useState('mapa');
  const [centro, setCentro] = useState([-14.235, -51.9253]);
  const [camadaMapa, setCamadaMapa] = useState('pinos');

  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (pos) => setCentro([pos.coords.latitude, pos.coords.longitude]),
      () => {}
    );
  }, []);

  useEffect(() => {
    carregarDenuncias();
  }, [filtroStatus]);

  async function carregarDenuncias() {
    try {
      const params = {};
      if (filtroStatus) params.status = filtroStatus;
      const { data } = await api.get('/denuncias', { params });
      setDenuncias(data);
    } catch (err) {
      console.error('Erro ao carregar denuncias:', err);
    }
  }

  return (
    <div className="page home-page">
      <header className="home-header">
        <h1 className="home-title">ComuClean</h1>
        <div className="home-toggle">
          <button
            className={`toggle-btn ${view === 'mapa' ? 'active' : ''}`}
            onClick={() => setView('mapa')}
          >
            Mapa
          </button>
          <button
            className={`toggle-btn ${view === 'feed' ? 'active' : ''}`}
            onClick={() => setView('feed')}
          >
            Feed
          </button>
        </div>
      </header>

      <div className="home-filters">
        <button
          className={`filter-chip ${filtroStatus === '' ? 'active' : ''}`}
          onClick={() => setFiltroStatus('')}
        >
          Todas
        </button>
        <button
          className={`filter-chip ${filtroStatus === 'aberta' ? 'active' : ''}`}
          onClick={() => setFiltroStatus('aberta')}
        >
          Abertas
        </button>
        <button
          className={`filter-chip ${filtroStatus === 'em_analise' ? 'active' : ''}`}
          onClick={() => setFiltroStatus('em_analise')}
        >
          Em analise
        </button>
        <button
          className={`filter-chip ${filtroStatus === 'resolvida' ? 'active' : ''}`}
          onClick={() => setFiltroStatus('resolvida')}
        >
          Resolvidas
        </button>
      </div>

      {view === 'mapa' ? (
        <div className="map-wrapper">
          <div className="map-layer-toggle">
            <button
              className={`layer-btn ${camadaMapa === 'pinos' ? 'active' : ''}`}
              onClick={() => setCamadaMapa('pinos')}
            >
              Pinos
            </button>
            <button
              className={`layer-btn ${camadaMapa === 'calor' ? 'active' : ''}`}
              onClick={() => setCamadaMapa('calor')}
            >
              Mapa de calor
            </button>
          </div>
          <MapContainer center={centro} zoom={14} className="map-container" zoomControl={false}>
            <ChangeView center={centro} />
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {camadaMapa === 'pinos' && denuncias.map((d) => (
              <Marker key={d.id} position={[d.latitude, d.longitude]} icon={criarIcone(d.status)}>
                <Popup>
                  <div className="popup-content">
                    <span className={`badge badge-${d.tipo_lixo}`}>
                      {tipoLabels[d.tipo_lixo]}
                    </span>
                    <span className={`badge badge-${d.status}`}>
                      {statusLabels[d.status]}
                    </span>
                    {d.total_urgentes > 0 && (
                      <span className="popup-urgentes">{d.total_urgentes} urgente(s)</span>
                    )}
                    {d.descricao && <p>{d.descricao}</p>}
                  </div>
                </Popup>
              </Marker>
            ))}
            {camadaMapa === 'calor' && (
              <HeatmapLayer
                pontos={denuncias
                  .filter((d) => d.status !== 'resolvida')
                  .map((d) => [d.latitude, d.longitude, 0.5 + (d.total_urgentes * 0.2)])}
              />
            )}
          </MapContainer>
        </div>
      ) : (
        <div className="feed-list">
          {denuncias.length === 0 ? (
            <div className="feed-empty">
              <p>Nenhuma denuncia encontrada</p>
            </div>
          ) : (
            denuncias.map((d) => (
              <DenunciaCard key={d.id} denuncia={d} onUpdate={carregarDenuncias} />
            ))
          )}
        </div>
      )}
    </div>
  );
}

function DenunciaCard({ denuncia, onUpdate }) {
  const d = denuncia;
  const [loading, setLoading] = useState(false);
  const [showProva, setShowProva] = useState(false);
  const [foto, setFoto] = useState(null);
  const [erro, setErro] = useState('');

  async function handleUrgente() {
    setLoading(true);
    setErro('');
    try {
      await api.post('/validacoes', {
        denuncia_id: d.id,
        tipo_validacao: 'ainda_sujo',
      });
      onUpdate();
    } catch (err) {
      setErro(err.response?.data?.detail || 'Erro');
    } finally {
      setLoading(false);
    }
  }

  async function handleResolvido() {
    if (!foto) return;
    setLoading(true);
    setErro('');
    try {
      const pos = await new Promise((resolve, reject) =>
        navigator.geolocation.getCurrentPosition(resolve, reject)
      );

      const { data: validacao } = await api.post('/validacoes', {
        denuncia_id: d.id,
        tipo_validacao: 'ja_limpo',
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude,
      });

      const formData = new FormData();
      formData.append('arquivo', foto);
      await api.post(`/validacoes/${validacao.id}/imagem`, formData);

      setShowProva(false);
      setFoto(null);
      onUpdate();
    } catch (err) {
      setErro(err.response?.data?.detail || 'Erro ao enviar prova');
    } finally {
      setLoading(false);
    }
  }

  const resolvida = d.status === 'resolvida';

  return (
    <div className="card denuncia-card">
      <div className="denuncia-card-top">
        <span className={`badge badge-${d.tipo_lixo}`}>
          {tipoLabels[d.tipo_lixo]}
        </span>
        <span className={`badge badge-${d.status}`}>
          {statusLabels[d.status]}
        </span>
      </div>

      {d.descricao && <p className="denuncia-card-desc">{d.descricao}</p>}

      <div className="denuncia-card-meta">
        <span className="denuncia-card-date">
          {new Date(d.criada_em).toLocaleDateString('pt-BR')}
        </span>
        {d.total_urgentes > 0 && (
          <span className="urgente-count">{d.total_urgentes} urgente(s)</span>
        )}
      </div>

      {erro && <p className="card-erro">{erro}</p>}

      {!resolvida && (
        <div className="denuncia-card-actions">
          <button
            className="action-btn action-urgente"
            onClick={handleUrgente}
            disabled={loading}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            Urgente
          </button>
          <button
            className="action-btn action-resolvido"
            onClick={() => setShowProva(!showProva)}
            disabled={loading}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            Resolvido
          </button>
        </div>
      )}

      {showProva && (
        <div className="prova-section">
          <p className="prova-hint">Tire uma foto como prova e esteja proximo ao local</p>
          {foto ? (
            <div className="prova-preview">
              <img src={URL.createObjectURL(foto)} alt="Prova" />
              <button className="prova-remove" onClick={() => setFoto(null)}>Remover</button>
            </div>
          ) : (
            <label className="prova-upload">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
              <span>Tirar foto de prova</span>
              <input
                type="file"
                accept="image/*"
                capture="environment"
                onChange={(e) => setFoto(e.target.files[0])}
                hidden
              />
            </label>
          )}
          <button
            className="btn btn-primary btn-full"
            disabled={!foto || loading}
            onClick={handleResolvido}
          >
            {loading ? 'Enviando...' : 'Enviar prova'}
          </button>
        </div>
      )}
    </div>
  );
}
