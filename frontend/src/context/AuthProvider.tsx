import { useEffect, useState, type ReactNode } from 'react';
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from '../lib/firebase';
import { AuthContext, resolveProfile, type AuthState } from './authContext';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    role: 'viewer',
    ngoId: null,
    loading: true,
  });

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, async (user) => {
      if (!user) {
        setState({ user: null, role: 'viewer', ngoId: null, loading: false });
        return;
      }

      try {
        const { role, ngoId } = await resolveProfile(user);
        setState({ user, role, ngoId, loading: false });
      } catch (error) {
        console.error('Failed to resolve auth profile:', error);
        setState({ user, role: 'viewer', ngoId: null, loading: false });
      }
    });
    return () => unsub();
  }, []);

  return <AuthContext.Provider value={state}>{children}</AuthContext.Provider>;
}
