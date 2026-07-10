import { useState, type ReactNode } from 'react';

import { clearStoredToken, getStoredToken, setStoredToken } from '../api/client';
import type { Rol } from '../api/auth';
import { AuthContext } from './useAuth';

const ROL_KEY = 'gymflow-staff-rol';
const PERMISOS_KEY = 'gymflow-staff-permisos';

function leerPermisosGuardados(): string[] {
  const raw = localStorage.getItem(PERMISOS_KEY);
  if (!raw) return [];
  try {
    return JSON.parse(raw) as string[];
  } catch {
    return [];
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getStoredToken());
  const [rol, setRol] = useState<Rol | null>(() => localStorage.getItem(ROL_KEY) as Rol | null);
  const [permisos, setPermisos] = useState<string[]>(() => leerPermisosGuardados());

  function login(nuevoToken: string, nuevoRol: Rol, nuevosPermisos: string[]) {
    setStoredToken(nuevoToken);
    localStorage.setItem(ROL_KEY, nuevoRol);
    localStorage.setItem(PERMISOS_KEY, JSON.stringify(nuevosPermisos));
    setToken(nuevoToken);
    setRol(nuevoRol);
    setPermisos(nuevosPermisos);
  }

  function logout() {
    clearStoredToken();
    localStorage.removeItem(ROL_KEY);
    localStorage.removeItem(PERMISOS_KEY);
    setToken(null);
    setRol(null);
    setPermisos([]);
  }

  function hasPermission(codigo: string): boolean {
    return rol === 'administrador' || permisos.includes(codigo);
  }

  return (
    <AuthContext.Provider
      value={{ isAuthenticated: token !== null, rol, permisos, hasPermission, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}
