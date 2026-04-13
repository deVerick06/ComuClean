import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

export default function HeatmapLayer({ pontos }) {
  const map = useMap();

  useEffect(() => {
    if (!pontos.length) return;

    // pontos = [[lat, lng, intensidade], ...]
    const heat = L.heatLayer(pontos, {
      radius: 35,
      blur: 25,
      maxZoom: 17,
      max: 1.0,
      gradient: {
        0.2: '#22c55e',  // Verde - Nível Baixo
        0.5: '#facc15',  // Amarelo - Nível Médio
        0.8: '#ef4444',  // Vermelho - Nível Crítico
      },
    });

    heat.addTo(map);
    return () => map.removeLayer(heat);
  }, [pontos, map]);

  return null;
}
