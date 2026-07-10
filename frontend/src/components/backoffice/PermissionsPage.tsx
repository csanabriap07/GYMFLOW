import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';

import {
  grantPermission,
  listPermissions,
  listPermissionsCatalog,
  revokePermission,
} from '../../api/auth';
import { listUsers } from '../../api/members';

function PermissionsPage() {
  const queryClient = useQueryClient();
  const usuarios = useQuery({ queryKey: ['usuarios'], queryFn: listUsers });
  const catalogo = useQuery({ queryKey: ['catalogo-permisos'], queryFn: listPermissionsCatalog });
  const [userId, setUserId] = useState<number | null>(null);
  const [codigo, setCodigo] = useState('');

  const permisosQueryKey = ['permisos', userId];
  const permisos = useQuery({
    queryKey: permisosQueryKey,
    queryFn: () => listPermissions(userId as number),
    enabled: userId !== null,
  });

  const yaOtorgados = new Set(permisos.data?.map((p) => p.codigo));
  const disponiblesParaOtorgar = catalogo.data?.filter((p) => !yaOtorgados.has(p.codigo)) ?? [];

  const otorgar = useMutation({
    mutationFn: () => grantPermission(userId as number, codigo),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: permisosQueryKey });
      setCodigo('');
    },
  });

  const quitar = useMutation({
    mutationFn: (c: string) => revokePermission(userId as number, c),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: permisosQueryKey }),
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (userId === null || otorgar.isPending) return;
    otorgar.mutate();
  }

  return (
    <div>
      <h1 className="text-member-navy-text text-2xl font-semibold mb-4">Permisos de usuario</h1>

      <div className="mb-4">
        <label className="block text-xs text-gray-600 mb-1" htmlFor="usuario">
          Usuario
        </label>
        <select
          id="usuario"
          value={userId ?? ''}
          onChange={(e) => setUserId(e.target.value ? Number(e.target.value) : null)}
          className="border border-gray-300 rounded px-2 py-1 text-sm w-64"
        >
          <option value="">Selecciona un usuario…</option>
          {usuarios.data
            ?.filter((u) => u.rol === 'empleado' || u.rol === 'administrador')
            .map((u) => (
              <option key={u.id} value={u.id}>
                {u.nombre} ({u.email})
              </option>
            ))}
        </select>
      </div>

      {userId !== null && (
        <div className="bg-white rounded-card shadow border border-gray-200 p-4">
          {permisos.data && permisos.data.length === 0 && (
            <p className="text-gray-500 text-sm mb-3">Sin permisos individuales otorgados.</p>
          )}

          {permisos.data && permisos.data.length > 0 && (
            <ul className="mb-4">
              {permisos.data.map((p) => (
                <li
                  key={p.codigo}
                  className="flex items-center justify-between border-b border-gray-100 last:border-0 py-2 text-sm"
                >
                  <div>
                    <span className="text-gray-900 font-mono">{p.codigo}</span>
                    {p.descripcion && (
                      <p className="text-gray-500 text-xs">{p.descripcion}</p>
                    )}
                  </div>
                  <button
                    onClick={() => quitar.mutate(p.codigo)}
                    className="text-sm text-red-600 border border-red-200 rounded px-2 py-1 hover:bg-red-50"
                  >
                    Quitar
                  </button>
                </li>
              ))}
            </ul>
          )}

          {catalogo.data && disponiblesParaOtorgar.length === 0 && (
            <p className="text-gray-500 text-sm">
              Ya tiene otorgados todos los permisos del catálogo.
            </p>
          )}

          {disponiblesParaOtorgar.length > 0 && (
            <form onSubmit={handleSubmit} className="flex items-end gap-2">
              <div>
                <label className="block text-xs text-gray-600 mb-1" htmlFor="codigo">
                  Permiso
                </label>
                <select
                  id="codigo"
                  required
                  value={codigo}
                  onChange={(e) => setCodigo(e.target.value)}
                  className="w-96 border border-gray-300 rounded px-2 py-1 text-sm"
                >
                  <option value="" disabled>
                    Selecciona…
                  </option>
                  {disponiblesParaOtorgar.map((p) => (
                    <option key={p.codigo} value={p.codigo}>
                      {p.codigo}
                      {p.descripcion ? ` — ${p.descripcion}` : ''}
                    </option>
                  ))}
                </select>
              </div>
              <button
                type="submit"
                disabled={otorgar.isPending}
                className="bg-member-navy text-white rounded px-3 py-1.5 text-sm disabled:opacity-50"
              >
                Otorgar
              </button>
            </form>
          )}

          {otorgar.isError && (
            <p className="text-red-600 text-sm mt-2">No se pudo otorgar el permiso.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default PermissionsPage;
