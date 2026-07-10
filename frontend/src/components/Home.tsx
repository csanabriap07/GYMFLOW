import { Link } from 'react-router';

import { useAuth } from '../context/useAuth';

function Home() {
  const auth = useAuth();

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-8">
      <div className="bg-white rounded-lg shadow p-8 w-full max-w-sm border border-gray-200">
        <h1 className="text-gray-900 text-xl font-semibold mb-1">GymFlow</h1>
        <p className="text-gray-500 text-sm mb-6">¿A dónde quieres ir?</p>

        <div className="flex flex-col gap-3">
          <Link
            to="/"
            className="w-full text-center bg-gray-900 text-white rounded px-3 py-2 font-medium"
          >
            Kiosco de check-in
          </Link>
          <Link
            to={auth.isAuthenticated ? '/staff/home' : '/staff/login'}
            className="w-full text-center border border-gray-300 text-gray-900 rounded px-3 py-2 font-medium hover:bg-gray-50"
          >
            Portal Staff
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Home;
