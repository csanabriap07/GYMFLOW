import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8001",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("gymflow_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && window.location.pathname !== "/login") {
      localStorage.removeItem("gymflow_token");
      localStorage.removeItem("gymflow_rol");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  rol: string;
  expires_in: number;
}

export interface CheckinResponse {
  resultado: string;
  mensaje: string;
  razon: string | null;
  nombre: string | null;
  visitas_restantes: number | null;
  cupos_invitados: number | null;
  membresia: Record<string, unknown> | null;
  bloqueado_hasta: string | null;
  cortesia: boolean | null;
}

function getDeviceId(): string {
  let id = localStorage.getItem("gymflow_device_id");
  if (!id) {
    id = "device-" + Math.random().toString(36).substring(2) + Date.now().toString(36);
    localStorage.setItem("gymflow_device_id", id);
  }
  return id;
}

export function postLogin(email: string, password: string) {
  return api.post<LoginResponse>("/auth/login", { email, password }).then((r) => {
    localStorage.setItem("gymflow_token", r.data.access_token);
    localStorage.setItem("gymflow_rol", r.data.rol);
    return r.data;
  });
}

export function logout() {
  localStorage.removeItem("gymflow_token");
  localStorage.removeItem("gymflow_rol");
}

export function postCheckin(cedula: string) {
  return api
    .post<CheckinResponse>("/checkin", { cedula }, { headers: { "X-Device-Id": getDeviceId() } })
    .then((r) => r.data);
}

export function postGuestCheckin(cedulaInvitado: string, cedulaTitular: string) {
  return api
    .post<CheckinResponse>(
      "/checkin/guest",
      { cedula_invitado: cedulaInvitado, cedula_titular: cedulaTitular },
      { headers: { "X-Device-Id": getDeviceId() } }
    )
    .then((r) => r.data);
}

export function postCheckinQr(qrPayload: string) {
  return api
    .post<CheckinResponse>(
      "/checkin/qr",
      null,
      { params: { qr_payload: qrPayload }, headers: { "X-Device-Id": getDeviceId() } }
    )
    .then((r) => r.data);
}

export interface UserOut {
  id: number;
  cedula: string | null;
  nombre: string | null;
  email: string | null;
  rol: string;
  estado: string;
}

export interface UserCreate {
  cedula: string;
  nombre: string;
  email: string;
  rol?: string;
  password?: string;
}

export function getUsers() {
  return api.get<UserOut[]>("/usuarios").then((r) => r.data);
}

export function createUser(data: UserCreate) {
  return api.post<UserOut>("/usuarios", data).then((r) => r.data);
}

export function updateUser(id: number, data: Partial<UserCreate>) {
  return api.put<UserOut>(`/usuarios/${id}`, data).then((r) => r.data);
}

export function deleteUser(id: number) {
  return api.delete(`/usuarios/${id}`).then((r) => r.data);
}

export function assignMembership(userId: number, tipoId: number) {
  return api.post(`/usuarios/${userId}/membresia`, null, { params: { tipo_id: tipoId } }).then((r) => r.data);
}

export interface MembershipSummary {
  tipo: string;
  estado: string;
  visitas_restantes: number;
  cupo_invitados_restantes: number;
  fecha_inicio: string;
  fecha_vencimiento: string;
  proximo_pago: string;
}

export function getMembershipSummary(cedula: string) {
  return api.get<MembershipSummary>("/membresias/summary", { params: { cedula } }).then((r) => r.data);
}

export function searchUsers(q: string) {
  return api.get<UserOut[]>("/usuarios/search", { params: { q } }).then((r) => r.data);
}

export interface MembershipTypeOut {
  id: number;
  nombre: string;
  precio_base: string;
  visitas_totales: number;
  cupo_invitados: number;
  duracion_dias: number;
  activo: boolean;
}

export interface MembershipTypeCreate {
  nombre: string;
  precio_base: string;
  visitas_totales: number;
  cupo_invitados: number;
  duracion_dias: number;
  activo: boolean;
}

export function getMembershipTypes() {
  return api.get<MembershipTypeOut[]>("/membresias/tipos").then((r) => r.data);
}

export function createMembershipType(data: MembershipTypeCreate) {
  return api.post<MembershipTypeOut>("/membresias/tipos", data).then((r) => r.data);
}

export function updateMembershipType(id: number, data: Partial<MembershipTypeCreate>) {
  return api.put<MembershipTypeOut>(`/membresias/tipos/${id}`, data).then((r) => r.data);
}

export function deactivateMembershipType(id: number) {
  return api.patch<MembershipTypeOut>(`/membresias/tipos/${id}/desactivar`).then((r) => r.data);
}

export function deleteMembershipType(id: number) {
  return api.delete(`/membresias/tipos/${id}`).then((r) => r.data);
}

export interface AttendanceRow {
  id: number;
  usuario_id: number;
  usuario_nombre: string;
  usuario_cedula: string;
  fecha_hora: string;
  resultado: string;
  razon: string | null;
}

export function getAttendanceReport(fechaInicio: string, fechaFin: string) {
  return api.get<AttendanceRow[]>("/reports/attendance", {
    params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin },
  }).then((r) => r.data);
}

export function exportAttendanceReport(fechaInicio: string, fechaFin: string, format: "csv" | "xlsx") {
  return api.get("/reports/attendance/export", {
    params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin, format },
    responseType: "blob",
  }).then((r) => {
    const url = window.URL.createObjectURL(new Blob([r.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `asistencia.${format}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  });
}
