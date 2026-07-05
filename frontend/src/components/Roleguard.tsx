import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthCtx, type Role } from '../context/authContext';

interface RoleGuardProps {
  allow: Role[];
  children: ReactNode;
}

export default function RoleGuard({ allow, children }: RoleGuardProps) {
  const { role, loading } = useAuthCtx();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
      </div>
    );
  }

  return allow.includes(role) ? <>{children}</> : <Navigate to="/" replace />;
}