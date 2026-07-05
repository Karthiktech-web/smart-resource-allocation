import { createContext, useContext } from 'react';
import type { User } from 'firebase/auth';

export type Role = 'admin' | 'volunteer' | 'viewer';

export interface AuthState {
  user: User | null;
  role: Role;
  ngoId: string | null;
  loading: boolean;
}

const DEFAULT_API_URLS = ['http://127.0.0.1:8000', 'http://localhost:8000'];

export function getApiBaseUrls(): string[] {
  const configured = import.meta.env.VITE_API_URL?.trim();
  const urls = [configured, ...DEFAULT_API_URLS].filter(Boolean) as string[];
  return Array.from(new Set(urls));
}

export const AuthContext = createContext<AuthState>({
  user: null,
  role: 'viewer',
  ngoId: null,
  loading: true,
});

export function useAuthCtx() {
  return useContext(AuthContext);
}

export async function resolveProfile(
  user: User,
): Promise<{ role: Role; ngoId: string | null }> {
  const token = await user.getIdToken();
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };

  const urls = getApiBaseUrls();
  let lastError: unknown;

  for (const baseUrl of urls) {
    try {
      await fetch(`${baseUrl}/api/users/register`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          uid: user.uid,
          email: user.email ?? '',
          name: user.displayName ?? '',
          photo_url: user.photoURL ?? null,
        }),
      }).catch(() => undefined);

      const res = await fetch(`${baseUrl}/api/users/me`, { headers });
      if (!res.ok) return { role: 'volunteer', ngoId: null };
      const data = await res.json();
      return { role: (data.role as Role) ?? 'volunteer', ngoId: data.ngo_id ?? null };
    } catch (error) {
      lastError = error;
    }
  }

  console.warn('Unable to resolve auth profile from backend:', lastError);
  return { role: 'viewer', ngoId: null };
}