import { useAuthCtx } from '../context/authContext';

// Backed by AuthContext so role/ngoId resolve from the backend profile.
export function useAuth() {
  const { user, role, ngoId, loading } = useAuthCtx();
  return { user, role, ngoId, loading };
}