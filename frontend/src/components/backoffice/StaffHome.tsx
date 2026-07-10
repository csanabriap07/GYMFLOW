import { useAuth } from '../../context/useAuth';

function StaffHome() {
  const auth = useAuth();

  return (
    <div>
      <h1 className="text-member-navy-text text-2xl font-semibold">Bienvenido</h1>
      <p className="text-member-muted text-sm mt-1">
        Conectado como {auth.rol}. Usa el menú de la izquierda para navegar.
      </p>
    </div>
  );
}

export default StaffHome;
