import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth } from './lib/firebase';
import Layout from './components/layout/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import IngestPage from './pages/IngestPage';
import NeedsPage from './pages/NeedsPage';
import ProgramsPage from './pages/ProgramsDetailPage';
import AllocatePage from './pages/AllocatePage';
import ImpactPage from './pages/ImpactPage';
import VolunteersPage from './pages/VolunteersPage';
import AreaDetailPage from './pages/AreaDetailPage';
import AreaDetailPage from './pages/AreaDetailPage';
<Route path="/areas/:id" element={<AreaDetailPage />} />


function App() {
  const [user, loading] = useAuthState(auth);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-500 text-sm">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout user={user} />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/ingest" element={<IngestPage />} />
          <Route path="/needs" element={<NeedsPage />} />
          <Route path="/programs" element={<ProgramsPage />} />
          <Route path="/allocate" element={<AllocatePage />} />
          <Route path="/impact" element={<ImpactPage />} />
          <Route path="/volunteers" element={<VolunteersPage />} />
          <Route path="/areas/:id" element={<AreaDetailPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;