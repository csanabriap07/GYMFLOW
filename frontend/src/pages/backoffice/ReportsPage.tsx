import { useState } from "react";
import { getAttendanceReport, exportAttendanceReport, logout, type AttendanceRow } from "../../api";

export default function ReportsPage() {
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [rows, setRows] = useState<AttendanceRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fechaInicio || !fechaFin) return;
    setLoading(true);
    try {
      const data = await getAttendanceReport(fechaInicio, fechaFin);
      setRows(data);
      setSearched(true);
    } catch {
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: "csv" | "xlsx") => {
    if (!fechaInicio || !fechaFin) return;
    await exportAttendanceReport(fechaInicio, fechaFin, format);
  };

  return (
    <div style={{ padding: 32, maxWidth: 1000, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button onClick={() => window.location.href = "/backoffice"}
            style={{ padding: "8px 12px", background: "#374151", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
            ← Volver
          </button>
          <h1 style={{ fontSize: 24, fontWeight: 700 }}>Reportes de Asistencia</h1>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => { logout(); window.location.href = "/login"; }}
            style={{ padding: "8px 16px", background: "#6b7280", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
            Salir
          </button>
        </div>
      </div>

      <form onSubmit={handleSearch} style={{ display: "flex", gap: 8, alignItems: "flex-end", marginBottom: 24 }}>
        <div>
          <label style={{ display: "block", fontSize: 12, marginBottom: 4 }}>Fecha Inicio</label>
          <input type="date" value={fechaInicio} onChange={e => setFechaInicio(e.target.value)} required
            style={{ padding: 8, border: "1px solid #d1d5db", borderRadius: 4 }} />
        </div>
        <div>
          <label style={{ display: "block", fontSize: 12, marginBottom: 4 }}>Fecha Fin</label>
          <input type="date" value={fechaFin} onChange={e => setFechaFin(e.target.value)} required
            style={{ padding: 8, border: "1px solid #d1d5db", borderRadius: 4 }} />
        </div>
        <button type="submit" disabled={loading}
          style={{ padding: "8px 16px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
          {loading ? "Buscando..." : "Buscar"}
        </button>
        <button type="button" onClick={() => handleExport("csv")} disabled={!searched}
          style={{ padding: "8px 16px", background: "#16a34a", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
          Exportar CSV
        </button>
        <button type="button" onClick={() => handleExport("xlsx")} disabled={!searched}
          style={{ padding: "8px 16px", background: "#16a34a", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
          Exportar XLSX
        </button>
      </form>

      {searched && (
        <p style={{ marginBottom: 12, color: "#6b7280" }}>{rows.length} registros encontrados</p>
      )}

      {rows.length > 0 && (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid #d1d5db", textAlign: "left" }}>
              <th style={{ padding: 8 }}>ID</th>
              <th style={{ padding: 8 }}>Usuario</th>
              <th style={{ padding: 8 }}>Cédula</th>
              <th style={{ padding: 8 }}>Fecha/Hora</th>
              <th style={{ padding: 8 }}>Resultado</th>
              <th style={{ padding: 8 }}>Razón</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.id} style={{ borderBottom: "1px solid #e5e7eb" }}>
                <td style={{ padding: 8 }}>{r.id}</td>
                <td style={{ padding: 8 }}>{r.usuario_nombre}</td>
                <td style={{ padding: 8 }}>{r.usuario_cedula}</td>
                <td style={{ padding: 8 }}>{new Date(r.fecha_hora).toLocaleString()}</td>
                <td style={{ padding: 8 }}>
                  <span style={{ color: r.resultado === "exitoso" ? "#16a34a" : "#dc2626", fontWeight: 600 }}>
                    {r.resultado}
                  </span>
                </td>
                <td style={{ padding: 8 }}>{r.razon || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {searched && rows.length === 0 && (
        <p style={{ color: "#6b7280", textAlign: "center", marginTop: 24 }}>No hay registros en el rango seleccionado.</p>
      )}
    </div>
  );
}
