import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import HcpDetailPage from './pages/HcpDetailPage';
import HcpListPage from './pages/HcpListPage';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import LogInteractionPage from './pages/LogInteractionPage';
import EditInteractionPage from './pages/EditInteractionPage';
import MyInteractionsPage from './pages/MyInteractionsPage';

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/hcps" element={<HcpListPage />} />
          <Route path="/hcps/:id" element={<HcpDetailPage />} />
          <Route path="/log-interaction" element={<LogInteractionPage />} />
          <Route path="/interactions/:id/edit" element={<EditInteractionPage />} />
          <Route path="/interactions" element={<MyInteractionsPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}