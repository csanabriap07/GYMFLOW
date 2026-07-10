import { NavLink, Outlet } from 'react-router';

import { useAuth } from '../../context/useAuth';
import { STAFF_MENU_ITEMS } from '../../navigation/staffMenu';

function StaffLayout() {
  const auth = useAuth();

  const items = STAFF_MENU_ITEMS.filter((item) => {
    if (item.adminOnly && auth.rol !== 'administrador') return false;
    if (item.permission && !auth.hasPermission(item.permission)) return false;
    return true;
  });

  return (
    <div className="min-h-screen flex bg-member-bg">
      <aside className="w-56 shrink-0 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-member-navy-text text-lg font-semibold">GymFlow</h1>
          <p className="text-gray-500 text-xs">Conectado como: {auth.rol}</p>
        </div>

        <nav className="flex-1 p-3 flex flex-col gap-1">
          {items.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/staff/home'}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded px-3 py-2 text-sm font-medium ${
                  isActive
                    ? 'bg-member-navy text-white'
                    : 'text-gray-600 hover:bg-gray-50'
                }`
              }
            >
              <span aria-hidden="true">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-gray-200">
          <button
            onClick={() => auth.logout()}
            className="w-full flex items-center gap-2 rounded px-3 py-2 text-sm text-gray-600 hover:bg-gray-50"
          >
            <span aria-hidden="true">🚪</span>
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="flex-1 p-8">
        <Outlet />
      </main>
    </div>
  );
}

export default StaffLayout;
