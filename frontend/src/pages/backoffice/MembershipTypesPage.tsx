import { useEffect, useState } from "react";
import {
  getMembershipTypes,
  createMembershipType,
  updateMembershipType,
  deactivateMembershipType,
  deleteMembershipType,
  logout,
  type MembershipTypeOut,
  type MembershipTypeCreate,
} from "../../api";

export default function MembershipTypesPage() {
  const [tipos, setTipos] = useState<MembershipTypeOut[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editTipo, setEditTipo] = useState<MembershipTypeOut | null>(null);
  const [form, setForm] = useState<MembershipTypeCreate>({
    nombre: "",
    precio_base: "0",
    visitas_totales: 10,
    cupo_invitados: 0,
    duracion_dias: 30,
    activo: true,
  });
  const [error, setError] = useState("");

  const load = () => getMembershipTypes().then(setTipos);
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      if (editTipo) {
        await updateMembershipType(editTipo.id, form);
      } else {
        await createMembershipType(form);
      }
      setShowForm(false);
      setEditTipo(null);
      resetForm();
      load();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error";
      setError(msg);
    }
  };

  const handleDeactivate = async (id: number) => {
    if (!confirm("Desactivar este tipo de membresía?")) return;
    setError("");
    try {
      await deactivateMembershipType(id);
      load();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error";
      setError(msg);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Eliminar este tipo de membresía?")) return;
    setError("");
    try {
      await deleteMembershipType(id);
      load();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error";
      setError(msg);
    }
  };

  const startEdit = (t: MembershipTypeOut) => {
    setEditTipo(t);
    setForm({
      nombre: t.nombre,
      precio_base: t.precio_base,
      visitas_totales: t.visitas_totales,
      cupo_invitados: t.cupo_invitados,
      duracion_dias: t.duracion_dias,
      activo: t.activo,
    });
    setShowForm(true);
  };

  const resetForm = () => {
    setForm({ nombre: "", precio_base: "0", visitas_totales: 10, cupo_invitados: 0, duracion_dias: 30, activo: true });
  };

  return (
    <div style={{ padding: 32, maxWidth: 900, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button onClick={() => window.location.href = "/backoffice"}
            style={{ padding: "8px 12px", background: "#374151", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
            ← Volver
          </button>
          <h1 style={{ fontSize: 24, fontWeight: 700 }}>Tipos de Membresia</h1>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => { setShowForm(true); setEditTipo(null); resetForm(); }}
            style={{ padding: "8px 16px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
            + Nuevo
          </button>
          <button onClick={() => { logout(); window.location.href = "/login"; }}
            style={{ padding: "8px 16px", background: "#6b7280", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
            Salir
          </button>
        </div>
      </div>

      {error && <p style={{ color: "#dc2626", marginBottom: 12 }}>{error}</p>}

      {showForm && (
        <div style={{ background: "#f3f4f6", padding: 16, borderRadius: 8, marginBottom: 24 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 12 }}>{editTipo ? "Editar" : "Nuevo"} Tipo</h2>
          <form onSubmit={handleSubmit} style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "flex-end" }}>
            <input placeholder="Nombre" value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} required style={{ padding: 8, border: "1px solid #d1d5db", borderRadius: 4, width: 160 }} />
            <input placeholder="Precio base" type="number" step="0.01" value={form.precio_base} onChange={e => setForm({...form, precio_base: e.target.value})} required style={{ padding: 8, border: "1px solid #d1d5db", borderRadius: 4, width: 100 }} />
            <input placeholder="Visitas totales" type="number" value={form.visitas_totales} onChange={e => setForm({...form, visitas_totales: parseInt(e.target.value) || 0})} required style={{ padding: 8, border: "1px solid #d1d5db", borderRadius: 4, width: 100 }} />
            <input placeholder="Cupos invitados" type="number" value={form.cupo_invitados} onChange={e => setForm({...form, cupo_invitados: parseInt(e.target.value) || 0})} style={{ padding: 8, border: "1px solid #d1d5db", borderRadius: 4, width: 100 }} />
            <input placeholder="Duración (días)" type="number" value={form.duracion_dias} onChange={e => setForm({...form, duracion_dias: parseInt(e.target.value) || 0})} required style={{ padding: 8, border: "1px solid #d1d5db", borderRadius: 4, width: 100 }} />
            <label style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <input type="checkbox" checked={form.activo} onChange={e => setForm({...form, activo: e.target.checked})} />
              Activo
            </label>
            <button type="submit" style={{ padding: "8px 16px", background: "#16a34a", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
              {editTipo ? "Guardar" : "Crear"}
            </button>
            <button type="button" onClick={() => { setShowForm(false); setEditTipo(null); }}
              style={{ padding: "8px 16px", background: "#dc2626", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
              Cancelar
            </button>
          </form>
        </div>
      )}

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #d1d5db", textAlign: "left" }}>
            <th style={{ padding: 8 }}>ID</th>
            <th style={{ padding: 8 }}>Nombre</th>
            <th style={{ padding: 8 }}>Precio</th>
            <th style={{ padding: 8 }}>Visitas</th>
            <th style={{ padding: 8 }}>Invitados</th>
            <th style={{ padding: 8 }}>Días</th>
            <th style={{ padding: 8 }}>Estado</th>
            <th style={{ padding: 8 }}>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {tipos.map(t => (
            <tr key={t.id} style={{ borderBottom: "1px solid #e5e7eb" }}>
              <td style={{ padding: 8 }}>{t.id}</td>
              <td style={{ padding: 8 }}>{t.nombre}</td>
              <td style={{ padding: 8 }}>${t.precio_base}</td>
              <td style={{ padding: 8 }}>{t.visitas_totales}</td>
              <td style={{ padding: 8 }}>{t.cupo_invitados}</td>
              <td style={{ padding: 8 }}>{t.duracion_dias}</td>
              <td style={{ padding: 8 }}>
                <span style={{ color: t.activo ? "#16a34a" : "#dc2626", fontWeight: 600 }}>
                  {t.activo ? "Activo" : "Inactivo"}
                </span>
              </td>
              <td style={{ padding: 8, display: "flex", gap: 4 }}>
                <button onClick={() => startEdit(t)} style={{ padding: "4px 8px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer", fontSize: 12 }}>Editar</button>
                {t.activo && (
                  <button onClick={() => handleDeactivate(t.id)} style={{ padding: "4px 8px", background: "#f59e0b", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer", fontSize: 12 }}>Desactivar</button>
                )}
                <button onClick={() => handleDelete(t.id)} style={{ padding: "4px 8px", background: "#dc2626", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer", fontSize: 12 }}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
