import { Route, Routes } from 'react-router';

import CheckinKiosk from './components/CheckinKiosk';
import Home from './components/Home';
import DispositivosBloqueados from './components/backoffice/DispositivosBloqueados';
import LoginForm from './components/backoffice/LoginForm';
import PermissionsPage from './components/backoffice/PermissionsPage';
import ProtectedRoute from './components/backoffice/ProtectedRoute';
import StaffHome from './components/backoffice/StaffHome';
import StaffLayout from './components/backoffice/StaffLayout';
import UsersPage from './components/backoffice/UsersPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<CheckinKiosk />} />
      <Route path="/home" element={<Home />} />
      <Route path="/staff/login" element={<LoginForm />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<StaffLayout />}>
          <Route path="/staff/home" element={<StaffHome />} />
          <Route path="/staff/usuarios" element={<UsersPage />} />
          <Route path="/staff/permisos" element={<PermissionsPage />} />
          <Route path="/staff/dispositivos-bloqueados" element={<DispositivosBloqueados />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
