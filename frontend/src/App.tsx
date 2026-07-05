import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { useAuthCtx } from './context/authContext';
import RoleGuard from './components/Roleguard';
import Layout from './components/layout/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import IngestPage from './pages/IngestPage';
import NeedsPage from './pages/NeedsPage';
import ProgramsPage from './pages/ProgramsPage';
import ProgramDetailPage from './pages/ProgramsDetailPage';
import ReportsPage from './pages/ReportsPage';
import AllocatePage from './pages/AllocatePage';
import TasksPage from './pages/TasksPage';
import InsightsPage from './pages/InsightsPage';
import ImpactPage from './pages/ImpactPage';
import VolunteersPage from './pages/VolunteersPage';
import AreaDetailPage from './pages/AreaDetailPage';
import LandingPage from './pages/LandingPage';

function AuthedApp() {
  const { user, loading } = useAuthCtx();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-b-2 border-blue-600" />
          <p className="text-sm text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <Routes>
      <Route element={<Layout user={user} />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/ingest" element={<IngestPage />} />
        <Route path="/needs" element={<NeedsPage />} />
        <Route path="/programs" element={<ProgramsPage />} />
        <Route path="/programs/:id" element={<ProgramDetailPage />} />
        <Route
          path="/allocate"
          element={
            <RoleGuard allow={['admin']}>
              <AllocatePage />
            </RoleGuard>
          }
        />
        <Route
          path="/tasks"
          element={
            <RoleGuard allow={['admin']}>
              <TasksPage />
            </RoleGuard>
          }
        />
        <Route
          path="/insights"
          element={
            <RoleGuard allow={['admin']}>
              <InsightsPage />
            </RoleGuard>
          }
        />
        <Route path="/impact" element={<ImpactPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/volunteers" element={<VolunteersPage />} />
        <Route path="/areas/:id" element={<AreaDetailPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="*" element={<AuthedApp />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
