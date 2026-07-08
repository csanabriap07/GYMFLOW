import { useEffect, useState } from "react";
import { getUsers, searchUsers, createUser, updateUser, deleteUser, getMembershipTypes, assignMembership, logout, type UserOut, type MembershipTypeOut } from "../../api";

export default function BackofficePage() {
  const [users, setUsers] = useState<UserOut[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editUser, setEditUser] = useState<UserOut | null>(null);
  const [form, setForm] = useState({ cedula: "", nombre: "", email: "", rol: "miembro", password: "" });
  const [showAssign, setShowAssign] = useState(false);
  const [assignUser, setAssignUser] = useState<UserOut | null>(null);
  const [tipos, setTipos] = useState<MembershipTypeOut[]>([]);
  const [selectedTipo, setSelectedTipo] = useState<number | "">("");
  const [error, setError] = useState("");

  const load = () => getUsers().then(setUsers);
  useEffect(() => { load(); }, []);

  const handleSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const q = e.target.value;
    setSearchQuery(q);
    if (!q.trim()) { load(); return; }
    try {
      const results = await searchUsers(q);
      setUsers(results);
    } catch { /* ignore */ }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      if (editUser) {
        const data: Record<string, string> = {};
        if (form.nombre) data.nombre = form.nombre;
        if (form.email) data.email = form.email;
        if (form.rol) data.rol = form.rol;
        if (form.cedula) data.cedula = form.cedula;
        await updateUser(editUser.id, data);
      } else {
        await createUser(form);
      }
      setShowForm(false);
      setEditUser(null);
      setForm({ cedula: "", nombre: "", email: "", rol: "miembro", password: "" });
      load();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al guardar";
      setError(msg);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Eliminar este usuario?")) return;
    await deleteUser(id);
    load();
  };

  const startEdit = (u: UserOut) => {
    setEditUser(u);
    setForm({ cedula: u.cedula || "", nombre: u.nombre || "", email: u.email || "", rol: u.rol, password: "" });
    setShowForm(true);
  };

  const openAssign = async (u: UserOut) => {
    setAssignUser(u);
    setSelectedTipo("");
    const tiposData = await getMembershipTypes();
    setTipos(tiposData.filter(t => t.activo));
    setShowAssign(true);
  };

  const handleAssign = async () => {
    if (!assignUser || !selectedTipo) return;
    try {
      await assignMembership(assignUser.id, selectedTipo);
      setShowAssign(false);
      setAssignUser(null);
      load();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al asignar";
      setError(msg);
    }
  };

  const inputStyle = { padding: 8, border: "1px solid #d1d5db", borderRadius: 4 };
  const labelStyle = { display: "block", fontSize: 12, color: "#6b7280", marginBottom: 4 };

  return (
    <div style={{ padding: 32, maxWidth: 900, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>Gestion de Usuarios</h1>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => window.location.href = "/backoffice/tipos-membresia"}
            style={{ padding: "8px 16px", background: "#7c3aed", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
            Tipos Membresia
          </button>
          <button onClick={() => window.location.href = "/backoffice/reportes"}
            style={{ padding: "8px 16px", background: "#0891b2", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
            Reportes
          </button>
          <button onClick={() => { setShowForm(true); setEditUser(null); setError(""); setForm({ cedula: "", nombre: "", email: "", rol: "miembro", password: "" }); }}
            style={{ padding: "8px 16px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
            + Nuevo
          </button>
          <button onClick={() => { logout(); window.location.href = "/login"; }}
            style={{ padding: "8px 16px", background: "#6b7280", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
            Salir
          </button>
        </div>
      </div>

      <div style={{ marginBottom: 16 }}>
        <input
          placeholder="Buscar por nombre o cedula..."
          value={searchQuery}
          onChange={handleSearch}
          style={{ width: "100%", padding: "10px 12px", border: "1px solid #d1d5db", borderRadius: 4, fontSize: 14 }}
        />
      </div>

      {error && <p style={{ color: "#dc2626", marginBottom: 12 }}>{error}</p>}

      {showForm && (
        <div style={{ background: "#f3f4f6", padding: 16, borderRadius: 8, marginBottom: 24 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 12 }}>{editUser ? "Editar" : "Nuevo"} Usuario</h2>
          <form onSubmit={handleSubmit} style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "flex-end" }}>
            <div>
              <label style={labelStyle}>Cedula</label>
              <input placeholder="Ej: 12345678" value={form.cedula} onChange={e => setForm({...form, cedula: e.target.value})} required style={{ ...inputStyle, width: 140 }} />
            </div>
            <div>
              <label style={labelStyle}>Nombre completo</label>
              <input placeholder="Ej: Juan Perez" value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} required style={{ ...inputStyle, width: 180 }} />
            </div>
            <div>
              <label style={labelStyle}>Correo electronico</label>
              <input placeholder="Ej: juan@email.com" type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} required style={{ ...inputStyle, width: 200 }} />
            </div>
            <div>
              <label style={labelStyle}>Rol</label>
              <select value={form.rol} onChange={e => setForm({...form, rol: e.target.value})} style={{ ...inputStyle, width: 140 }}>
                <option value="miembro">Miembro</option>
                <option value="empleado">Empleado</option>
                <option value="administrador">Admin</option>
              </select>
            </div>
            {!editUser && (
              <div>
                <label style={labelStyle}>Contrasena</label>
                <input placeholder="Minimo 6 caracteres" type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} style={{ ...inputStyle, width: 160 }} />
              </div>
            )}
            <button type="submit" style={{ padding: "8px 16px", background: "#16a34a", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
              {editUser ? "Guardar" : "Crear"}
            </button>
            <button type="button" onClick={() => { setShowForm(false); setEditUser(null); setError(""); }}
              style={{ padding: "8px 16px", background: "#dc2626", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
              Cancelar
            </button>
          </form>
        </div>
      )}

      {showAssign && assignUser && (
        <div style={{ background: "#ede9fe", padding: 16, borderRadius: 8, marginBottom: 24, border: "1px solid #c4b5fd" }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>Asignar Membresia</h2>
          <p style={{ fontSize: 13, color: "#6b7280", marginBottom: 12 }}>
            Usuario: <strong>{assignUser.nombre || "Sin nombre"}</strong> (Cedula: {assignUser.cedula || "-"})
          </p>
          <div style={{ marginBottom: 12 }}>
            <label style={{ ...labelStyle, fontSize: 13, color: "#374151" }}>Tipo de membresia a asignar:</label>
            <select value={selectedTipo} onChange={e => setSelectedTipo(Number(e.target.value))} style={{ ...inputStyle, width: "100%", fontSize: 14 }}>
              <option value="">-- Seleccionar un tipo --</option>
              {tipos.map(t => (
                <option key={t.id} value={t.id}>
                  {t.nombre} — ${t.precio_base} — {t.visitas_totales} visitas — {t.cupo_invitados} invitados — {t.duracion_dias} dias
                </option>
              ))}
            </select>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={handleAssign} disabled={!selectedTipo}
              style={{ padding: "8px 16px", background: selectedTipo ? "#7c3aed" : "#9ca3af", color: "#fff", border: "none", borderRadius: 4, cursor: selectedTipo ? "pointer" : "not-allowed" }}>
              Asignar Membresia
            </button>
            <button onClick={() => { setShowAssign(false); setAssignUser(null); }}
              style={{ padding: "8px 16px", background: "#6b7280", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
              Cancelar
            </button>
          </div>
        </div>
      )}

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #d1d5db", textAlign: "left" }}>
            <th style={{ padding: 8 }}>ID</th>
            <th style={{ padding: 8 }}>Cedula</th>
            <th style={{ padding: 8 }}>Nombre</th>
            <th style={{ padding: 8 }}>Email</th>
            <th style={{ padding: 8 }}>Rol</th>
            <th style={{ padding: 8 }}>Estado</th>
            <th style={{ padding: 8 }}>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {users.map(u => (
            <tr key={u.id} style={{ borderBottom: "1px solid #e5e7eb" }}>
              <td style={{ padding: 8 }}>{u.id}</td>
              <td style={{ padding: 8 }}>{u.cedula || "-"}</td>
              <td style={{ padding: 8 }}>{u.nombre || "-"}</td>
              <td style={{ padding: 8 }}>{u.email || "-"}</td>
              <td style={{ padding: 8 }}>{u.rol}</td>
              <td style={{ padding: 8 }}>{u.estado}</td>
              <td style={{ padding: 8, display: "flex", gap: 4 }}>
                <button onClick={() => startEdit(u)} style={{ padding: "4px 8px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer", fontSize: 12 }}>Editar</button>
                <button onClick={() => openAssign(u)} style={{ padding: "4px 8px", background: "#7c3aed", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer", fontSize: 12 }}>Membresia</button>
                <button onClick={() => handleDelete(u.id)} style={{ padding: "4px 8px", background: "#dc2626", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer", fontSize: 12 }}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
