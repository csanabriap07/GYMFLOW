export interface StaffMenuItem {
  label: string;
  description?: string;
  path: string;
  icon: string;
  /** Si no se especifica, visible para cualquier staff logueado. */
  permission?: string;
  /** Si es true, solo visible para rol administrador (no alcanza con un permiso individual). */
  adminOnly?: boolean;
}

export const STAFF_MENU_ITEMS: StaffMenuItem[] = [
  {
    label: 'Inicio',
    path: '/staff/home',
    icon: '🏠',
  },
  {
    label: 'Usuarios',
    description: 'CRUD de usuarios, asignar y renovar membresías.',
    path: '/staff/usuarios',
    icon: '👥',
    permission: 'members.gestionar_usuarios',
  },
  {
    label: 'Permisos de usuario',
    description: 'Otorgar o quitar permisos individuales a un empleado.',
    path: '/staff/permisos',
    icon: '🔑',
    adminOnly: true,
  },
  {
    label: 'Dispositivos bloqueados',
    description: 'Ver y desbloquear kioscos bloqueados por intentos fallidos.',
    path: '/staff/dispositivos-bloqueados',
    icon: '🔒',
    permission: 'checkin.ver_dispositivos_bloqueados',
  },
];
