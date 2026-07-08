import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import KioskoPage from "./pages/kiosko/KioskoPage";
import LoginPage from "./pages/backoffice/LoginPage";
import BackofficePage from "./pages/backoffice/BackofficePage";
import MembershipTypesPage from "./pages/backoffice/MembershipTypesPage";
import ReportsPage from "./pages/backoffice/ReportsPage";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem("gymflow_token");
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<KioskoPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/backoffice"
          element={
            <ProtectedRoute>
              <BackofficePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/backoffice/tipos-membresia"
          element={
            <ProtectedRoute>
              <MembershipTypesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/backoffice/reportes"
          element={
            <ProtectedRoute>
              <ReportsPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
