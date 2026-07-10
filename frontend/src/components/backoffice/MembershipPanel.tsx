import { isAxiosError } from 'axios';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';

import {
  assignMembership,
  getMembershipHistory,
  listMembershipTypes,
  renewMembership,
  type MembershipActionRequest,
} from '../../api/members';
import { useAuth } from '../../context/useAuth';

function MembershipPanel({ userId }: { userId: number }) {
  const auth = useAuth();
  const queryClient = useQueryClient();
  const queryKey = ['membresias', userId];

  const historial = useQuery({ queryKey, queryFn: () => getMembershipHistory(userId) });
  const tipos = useQuery({ queryKey: ['tipos-membresia'], queryFn: listMembershipTypes });
  const nombreTipo = (tipoId: number) =>
    tipos.data?.find((t) => t.id === tipoId)?.nombre ?? `#${tipoId}`;

  const [tipoId, setTipoId] = useState('');
  const [monto, setMonto] = useState('');
  const [nota, setNota] = useState('');

  const tieneMembresia = (historial.data?.length ?? 0) > 0;
  const puedeRenovar = auth.hasPermission('membership.renovar');

  const mutation = useMutation({
    mutationFn: (payload: MembershipActionRequest) =>
      tieneMembresia ? renewMembership(userId, payload) : assignMembership(userId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      setTipoId('');
      setMonto('');
      setNota('');
    },
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (mutation.isPending) return;
    mutation.mutate({ tipo_id: Number(tipoId), monto, nota: nota || null });
  }

  const sinPermisoParaRenovar = tieneMembresia && !puedeRenovar;

  return (
    <div className="mt-4 border-t border-gray-200 pt-4">
      <h3 className="text-member-navy-text font-medium mb-2">Membresías</h3>

      {historial.isLoading && <p className="text-gray-500 text-sm">Cargando…</p>}

      {historial.data && historial.data.length === 0 && (
        <p className="text-gray-500 text-sm mb-3">Sin membresía todavía.</p>
      )}

      {historial.data && historial.data.length > 0 && (
        <table className="w-full text-sm mb-3">
          <thead>
            <tr className="text-left text-gray-500 border-b border-gray-200">
              <th className="py-1 pr-2">Tipo</th>
              <th className="py-1 pr-2">Vigente</th>
              <th className="py-1 pr-2">Inicio</th>
              <th className="py-1 pr-2">Vencimiento</th>
              <th className="py-1 pr-2">Visitas</th>
              <th className="py-1 pr-2">Monto</th>
              <th className="py-1">Nota</th>
            </tr>
          </thead>
          <tbody>
            {historial.data.map((m) => (
              <tr key={m.id} className="border-b border-gray-100 last:border-0">
                <td className="py-1 pr-2 text-gray-900">{nombreTipo(m.tipo_id)}</td>
                <td className="py-1 pr-2">
                  {m.vigente ? (
                    <span className="text-member-success font-medium">Vigente</span>
                  ) : (
                    <span className="text-gray-400">—</span>
                  )}
                </td>
                <td className="py-1 pr-2 text-gray-700">{m.fecha_inicio}</td>
                <td className="py-1 pr-2 text-gray-700">{m.fecha_vencimiento}</td>
                <td className="py-1 pr-2 text-gray-700">{m.visitas_restantes}</td>
                <td className="py-1 pr-2 text-gray-700">{m.monto}</td>
                <td className="py-1 text-gray-700">{m.nota ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {sinPermisoParaRenovar && (
        <p className="text-amber-700 bg-amber-50 border border-amber-200 rounded p-2 text-sm mb-3">
          No tienes el permiso <code>membership.renovar</code> — no puedes renovar la membresía
          de este usuario.
        </p>
      )}

      {!sinPermisoParaRenovar && tipos.data && tipos.data.length === 0 && (
        <p className="text-amber-700 bg-amber-50 border border-amber-200 rounded p-2 text-sm mb-3">
          No hay tipos de membresía activos todavía — se configuran en otra pantalla (pendiente).
        </p>
      )}

      {!sinPermisoParaRenovar && tipos.data && tipos.data.length > 0 && (
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-2">
          <div>
            <label className="block text-xs text-gray-600 mb-1" htmlFor="tipo_id">
              Tipo
            </label>
            <select
              id="tipo_id"
              required
              value={tipoId}
              onChange={(e) => setTipoId(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1 text-sm"
            >
              <option value="" disabled>
                Selecciona…
              </option>
              {tipos.data.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.nombre} — ${t.precio_base} · {t.duracion_dias}d · {t.visitas_totales} visitas
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1" htmlFor="monto">
              Monto
            </label>
            <input
              id="monto"
              type="number"
              step="0.01"
              required
              value={monto}
              onChange={(e) => setMonto(e.target.value)}
              className="w-28 border border-gray-300 rounded px-2 py-1 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1" htmlFor="nota">
              Nota (opcional)
            </label>
            <input
              id="nota"
              type="text"
              value={nota}
              onChange={(e) => setNota(e.target.value)}
              className="w-40 border border-gray-300 rounded px-2 py-1 text-sm"
            />
          </div>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="bg-member-navy text-white rounded px-3 py-1.5 text-sm disabled:opacity-50"
          >
            {tieneMembresia ? 'Renovar' : 'Asignar'}
          </button>
        </form>
      )}

      {mutation.isError && (
        <p className="text-red-600 text-sm mt-2">
          {isAxiosError(mutation.error) && mutation.error.response?.status === 404
            ? 'Tipo de membresía no encontrado.'
            : isAxiosError(mutation.error) && mutation.error.response?.status === 409
              ? 'Conflicto: revisa si ya tiene o no tiene una membresía previa.'
              : 'No se pudo guardar la membresía.'}
        </p>
      )}
    </div>
  );
}

export default MembershipPanel;
