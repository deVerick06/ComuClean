import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Cadastro from './pages/Cadastro';
import Home from './pages/Home';
import NovaDenuncia from './pages/NovaDenuncia';
import Perfil from './pages/Perfil';
import Ranking from './pages/Ranking';
import Recompensas from './pages/Recompensas';
import './styles/global.css';

function RotaProtegida() {
  const { usuario, carregando } = useAuth();

  if (carregando) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100dvh',
        color: 'var(--text-tertiary)',
      }}>
        Carregando...
      </div>
    );
  }

  if (!usuario) return <Navigate to="/login" replace />;

  return (
    <>
      <Outlet />
      <Navbar />
    </>
  );
}

function RotaPublica() {
  const { usuario, carregando } = useAuth();
  if (carregando) return null;
  if (usuario) return <Navigate to="/" replace />;
  return <Outlet />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<RotaPublica />}>
            <Route path="/login" element={<Login />} />
            <Route path="/cadastro" element={<Cadastro />} />
          </Route>

          <Route element={<RotaProtegida />}>
            <Route path="/" element={<Home />} />
            <Route path="/denunciar" element={<NovaDenuncia />} />
            <Route path="/ranking" element={<Ranking />} />
            <Route path="/recompensas" element={<Recompensas />} />
            <Route path="/perfil" element={<Perfil />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
