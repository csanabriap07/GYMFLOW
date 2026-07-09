import axios from 'axios';

export type CheckinResultado = 'exitoso' | 'denegado';

export interface CheckinResponse {
  resultado: CheckinResultado;
  mensaje: string;
  nombre: string | null;
  visitas_restantes: number | null;
}

const apiClient = axios.create({ baseURL: '/api' });

export async function postCheckin(cedula: string): Promise<CheckinResponse> {
  const { data } = await apiClient.post<CheckinResponse>('/checkin', { cedula });
  return data;
}
