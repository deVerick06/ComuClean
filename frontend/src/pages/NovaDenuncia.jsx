import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './NovaDenuncia.css';

const tipos = [
  { value: 'lixo_comum', label: 'Lixo comum', icon: '🗑️' },
  { value: 'entulho', label: 'Entulho', icon: '🧱' },
  { value: 'reciclavel', label: 'Reciclavel', icon: '♻️' },
];

export default function NovaDenuncia() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [tipo, setTipo] = useState('');
  const [descricao, setDescricao] = useState('');
  const [coords, setCoords] = useState(null);
  const [foto, setFoto] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState('');
  const [geoLoading, setGeoLoading] = useState(true);

  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setGeoLoading(false);
      },
      () => {
        setErro('Nao foi possivel obter sua localizacao. Ative o GPS.');
        setGeoLoading(false);
      }
    );
  }, []);

  function handleFoto(e) {
    const file = e.target.files[0];
    if (!file) return;
    setFoto(file);
    setPreview(URL.createObjectURL(file));
  }

  async function handleSubmit() {
    // Adicionei a validação da foto aqui também, já que no novo backend 
    // a foto (arquivo) é um campo obrigatório para criar a denúncia.
    if (!tipo || !coords || !foto) {
        setErro('Por favor, preencha os dados e adicione uma foto.');
        return;
    }

    setLoading(true);
    setErro('');

    try {
      const formData = new FormData();
      
      formData.append('tipo_lixo', tipo);
      formData.append('latitude', coords.lat);
      formData.append('longitude', coords.lng);
      
      if (descricao) {
        formData.append('descricao', descricao);
      }

      // 3. Adicionamos o arquivo da foto no mesmo pacote
      formData.append('arquivo', foto);
      await api.post('/denuncias', formData);

      navigate('/');
    } catch (err) {
      setErro(err.response?.data?.detail || 'Erro ao criar denuncia');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page nova-denuncia-page">
      <header className="nd-header">
        <button className="nd-back" onClick={() => step > 1 ? setStep(step - 1) : navigate(-1)}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <h1>Nova denuncia</h1>
        <div className="nd-steps">
          <span className={step >= 1 ? 'step-dot active' : 'step-dot'} />
          <span className={step >= 2 ? 'step-dot active' : 'step-dot'} />
          <span className={step >= 3 ? 'step-dot active' : 'step-dot'} />
        </div>
      </header>

      {erro && <div className="auth-error" style={{ margin: '0 1rem' }}>{erro}</div>}

      {step === 1 && (
        <div className="nd-content">
          <h2>Tipo de descarte</h2>
          <p className="nd-hint">Selecione o tipo de lixo encontrado</p>
          <div className="tipo-grid">
            {tipos.map((t) => (
              <button
                key={t.value}
                className={`tipo-card ${tipo === t.value ? 'selected' : ''}`}
                onClick={() => setTipo(t.value)}
              >
                <span className="tipo-icon">{t.icon}</span>
                <span className="tipo-label">{t.label}</span>
              </button>
            ))}
          </div>
          <button
            className="btn btn-primary btn-full"
            disabled={!tipo}
            onClick={() => setStep(2)}
          >
            Continuar
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="nd-content">
          <h2>Foto do local</h2>
          <p className="nd-hint">Foto obrigatoria do descarte irregular</p>

          {preview ? (
            <div className="foto-preview">
              <img src={preview} alt="Preview" />
              <button className="foto-remove" onClick={() => { setFoto(null); setPreview(null); }}>
                Remover
              </button>
            </div>
          ) : (
            <label className="foto-upload">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
              <span>Toque para tirar foto ou escolher imagem</span>
              <input
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleFoto}
                hidden
              />
            </label>
          )}

          <div className="input-group" style={{ marginTop: 'var(--space-md)' }}>
            <label htmlFor="descricao">Descricao (opcional)</label>
            <textarea
              id="descricao"
              rows={3}
              placeholder="Descreva o que encontrou..."
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
            />
          </div>

          <button className="btn btn-primary btn-full" disabled={!foto} onClick={() => setStep(3)}>
            Continuar
          </button>
          {!foto && <p className="nd-required">* A foto e obrigatoria para continuar</p>}
        </div>
      )}

      {step === 3 && (
        <div className="nd-content">
          <h2>Confirmar localizacao</h2>
          <p className="nd-hint">Sua localizacao atual sera usada</p>

          {geoLoading ? (
            <div className="geo-loading">
              <p>Obtendo localizacao...</p>
            </div>
          ) : coords ? (
            <div className="geo-info card">
              <div className="geo-pin">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
              </div>
              <div>
                <p className="geo-coords">{coords.lat.toFixed(6)}, {coords.lng.toFixed(6)}</p>
                <p className="geo-label">Localizacao capturada</p>
              </div>
            </div>
          ) : (
            <div className="geo-loading">
              <p>GPS indisponivel</p>
            </div>
          )}

          <div className="nd-summary card">
            <h3>Resumo</h3>
            <div className="summary-row">
              <span>Tipo</span>
              <span className={`badge badge-${tipo}`}>
                {tipos.find((t) => t.value === tipo)?.label}
              </span>
            </div>
            {descricao && (
              <div className="summary-row">
                <span>Descricao</span>
                <span className="summary-desc">{descricao}</span>
              </div>
            )}
            <div className="summary-row">
              <span>Foto</span>
              <span>{foto ? 'Sim' : 'Nao'}</span>
            </div>
          </div>

          <button
            className="btn btn-primary btn-full"
            disabled={loading || !coords}
            onClick={handleSubmit}
          >
            {loading ? 'Enviando...' : 'Enviar denuncia'}
          </button>
        </div>
      )}
    </div>
  );
}
