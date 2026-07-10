import { isAxiosError } from 'axios';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Navigate } from 'react-router';

import { desbloquearDispositivo, getDispositivosBloqueados } from '../../api/checkin';
import { useAuth } from '../../context/useAuth';

const QUERY_KEY = ['dispositivos-bloqueados'];

function DispositivosBloqueados() {
  const auth = useAuth();
  const queryClient = useQueryClient();

  const query = useQuery({ queryKey: QUERY_KEY, queryFn: getDispositivosBloqueados });

  const desbloquear = useMutation({
    mutationFn: desbloquearDispositivo,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEY }),
  });

  if (isAxiosError(query.error) && query.error.response?.status === 401) {
    auth.logout();
    return <Navigate to="/staff/login" replace />;
  }

  const sinPermiso = isAxiosError(query.error) && query.error.response?.status === 403;

  return (
    <div>
      <h1 className="text-member-navy-text text-2xl font-semibold mb-4">Dispositivos bloqueados</h1>

      {sinPermiso && (
        <p className="text-red-600 bg-red-50 border border-red-200 rounded p-3 mb-4">
          No tienes permiso para ver esta información.
        </p>
      )}

      {query.isLoading && <p className="text-gray-500">Cargando…</p>}

      {query.data && (
        <table className="w-full bg-white rounded-card shadow border border-gray-200 text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b border-gray-200">
              <th className="p-3">Dispositivo</th>
              <th className="p-3">Intentos fallidos</th>
              <th className="p-3">Bloqueado hasta</th>
              <th className="p-3" />
            </tr>
          </thead>
          <tbody>
            {query.data.length === 0 && (
              <tr>
                <td colSpan={4} className="p-3 text-gray-500">
                  No hay dispositivos bloqueados.
                </td>
              </tr>
            )}
            {query.data.map((d) => (
              <tr key={d.device_id} className="border-b border-gray-100 last:border-0">
                <td className="p-3 text-gray-900 font-mono">{d.device_id}</td>
                <td className="p-3 text-gray-900">{d.intentos_fallidos}</td>
                <td className="p-3 text-gray-900">
                  {new Date(d.bloqueado_hasta).toLocaleString()}
                </td>
                <td className="p-3 text-right">
                  <button
                    onClick={() => desbloquear.mutate(d.device_id)}
                    disabled={desbloquear.isPending}
                    className="text-sm bg-member-navy text-white rounded px-3 py-1.5 disabled:opacity-50"
                  >
                    Desbloquear
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default DispositivosBloqueados;
