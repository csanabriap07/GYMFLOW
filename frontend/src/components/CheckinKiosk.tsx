import { isAxiosError } from 'axios';
import { useMutation } from '@tanstack/react-query';
import { useRef, useState } from 'react';

import { postCheckin, type CheckinResponse } from '../api/checkin';
import NumericKeypad from './NumericKeypad';

const REINICIO_MS = 4000;

type Resultado = CheckinResponse | { resultado: 'denegado'; mensaje: string };

function CheckinKiosk() {
  const [cedula, setCedula] = useState('');
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const reinicioRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const mutation = useMutation({
    mutationFn: postCheckin,
    onSuccess: (data) => mostrarResultado(data),
    onError: (error) => {
      const noEncontrado = isAxiosError(error) && error.response?.status === 404;
      mostrarResultado({
        resultado: 'denegado',
        mensaje: noEncontrado
          ? 'Cédula no registrada.'
          : 'No se pudo validar el ingreso. Intenta de nuevo.',
      });
    },
  });

  function mostrarResultado(data: Resultado) {
    setResultado(data);
    setCedula('');
    reinicioRef.current = setTimeout(() => setResultado(null), REINICIO_MS);
  }

  function handleSubmit() {
    if (cedula.length === 0 || mutation.isPending) return;
    mutation.mutate(cedula);
  }

  if (resultado) {
    const exitoso = resultado.resultado === 'exitoso';
    return (
      <div
        className={`min-h-screen flex items-center justify-center p-8 ${
          exitoso ? 'bg-green-600' : 'bg-red-600'
        }`}
      >
        <p className="text-white text-4xl font-bold text-center leading-snug">
          {resultado.mensaje}
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-member-bg flex items-center justify-center p-8">
      <div className="bg-white rounded-card shadow-md p-10 w-full max-w-md text-center">
        <h1 className="text-member-navy-text text-2xl font-bold">GymFlow</h1>
        <p className="text-member-muted mt-1 mb-6">Ingresa tu número de cédula</p>

        <div className="h-16 rounded-card bg-member-bg text-member-navy-text text-3xl font-mono flex items-center justify-center tracking-widest mb-6">
          {cedula || '—'}
        </div>

        <NumericKeypad
          disabled={mutation.isPending}
          onDigit={(d) => setCedula((prev) => (prev.length < 20 ? prev + d : prev))}
          onBackspace={() => setCedula((prev) => prev.slice(0, -1))}
          onSubmit={handleSubmit}
        />
      </div>
    </div>
  );
}

export default CheckinKiosk;
