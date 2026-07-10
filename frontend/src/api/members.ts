import { apiClient } from './client';

export type Rol = 'invitado' | 'miembro' | 'empleado' | 'administrador';
export type EstadoUsuario = 'activo' | 'inactivo';

export interface User {
  id: number;
  cedula: string | null;
  nombre: string | null;
  email: string | null;
  rol: Rol;
  estado: EstadoUsuario;
  creado_en: string | null;
}

export interface UserCreate {
  cedula: string;
  nombre: string;
  email?: string | null;
  rol: Rol;
  estado?: EstadoUsuario;
  password?: string | null;
}

export type UserUpdate = Partial<UserCreate>;

export interface MembershipHistoryItem {
  id: number;
  tipo_id: number;
  monto: string;
  nota: string | null;
  fecha_inicio: string;
  fecha_vencimiento: string;
  visitas_restantes: number;
  cupo_invitados_restantes: number;
  vigente: boolean;
}

export interface MembershipActionRequest {
  tipo_id: number;
  monto: string;
  nota?: string | null;
}

export interface MembershipType {
  id: number;
  nombre: string;
  precio_base: string;
  visitas_totales: number;
  cupo_invitados: number;
  duracion_dias: number;
}

export async function listMembershipTypes(): Promise<MembershipType[]> {
  const { data } = await apiClient.get<MembershipType[]>('/membresias/tipos');
  return data;
}

export async function listUsers(): Promise<User[]> {
  const { data } = await apiClient.get<User[]>('/usuarios');
  return data;
}

export async function getUser(userId: number): Promise<User> {
  const { data } = await apiClient.get<User>(`/usuarios/${userId}`);
  return data;
}

export async function createUser(payload: UserCreate): Promise<User> {
  const { data } = await apiClient.post<User>('/usuarios', payload);
  return data;
}

export async function updateUser(userId: number, payload: UserUpdate): Promise<User> {
  const { data } = await apiClient.put<User>(`/usuarios/${userId}`, payload);
  return data;
}

export async function deleteUser(userId: number): Promise<User> {
  const { data } = await apiClient.delete<User>(`/usuarios/${userId}`);
  return data;
}

export async function getMembershipHistory(userId: number): Promise<MembershipHistoryItem[]> {
  const { data } = await apiClient.get<MembershipHistoryItem[]>(`/usuarios/${userId}/membresias`);
  return data;
}

export async function assignMembership(
  userId: number,
  payload: MembershipActionRequest,
): Promise<MembershipHistoryItem> {
  const { data } = await apiClient.post<MembershipHistoryItem>(
    `/usuarios/${userId}/membresias`,
    payload,
  );
  return data;
}

export async function renewMembership(
  userId: number,
  payload: MembershipActionRequest,
): Promise<MembershipHistoryItem> {
  const { data } = await apiClient.post<MembershipHistoryItem>(
    `/usuarios/${userId}/membresias/renovar`,
    payload,
  );
  return data;
}
