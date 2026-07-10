import { createContext, useContext } from 'react';

import type { Rol } from '../api/auth';

export interface AuthContextValue {
  isAuthenticated: boolean;
  rol: Rol | null;
  permisos: string[];
  hasPermission: (codigo: string) => boolean;
  login: (token: string, rol: Rol, permisos: string[]) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>');
  }
  return context;
}
