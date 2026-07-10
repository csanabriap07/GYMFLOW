import { apiClient } from './client';

export type Rol = 'empleado' | 'administrador';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  rol: Rol;
  permisos: string[];
}

export async function postLogin(email: string, password: string): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>('/auth/login', { email, password });
  return data;
}

export interface PermisoOut {
  codigo: string;
  descripcion: string | null;
}

export async function listPermissions(userId: number): Promise<PermisoOut[]> {
  const { data } = await apiClient.get<PermisoOut[]>(`/auth/usuarios/${userId}/permisos`);
  return data;
}

export async function listPermissionsCatalog(): Promise<PermisoOut[]> {
  const { data } = await apiClient.get<PermisoOut[]>('/auth/permisos');
  return data;
}

export async function grantPermission(userId: number, codigo: string): Promise<void> {
  await apiClient.post(`/auth/usuarios/${userId}/permisos`, { codigo });
}

export async function revokePermission(userId: number, codigo: string): Promise<void> {
  await apiClient.delete(`/auth/usuarios/${userId}/permisos/${codigo}`);
}
