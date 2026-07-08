import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { postCheckin, postGuestCheckin, postCheckinQr, type CheckinResponse } from "../../api";

type Status = "idle" | "loading" | "success" | "denied" | "error" | "locked";
type Mode = "member" | "guest";

export default function KioskoPage() {
  const [mode, setMode] = useState<Mode>("member");
  const [cedula, setCedula] = useState("");
  const [cedulaTitular, setCedulaTitular] = useState("");
  const [result, setResult] = useState<CheckinResponse | null>(null);
  const [status, setStatus] = useState<Status>("idle");

  const memberMutation = useMutation({
    mutationFn: (c: string) => postCheckin(c),
    onSuccess: (data) => {
      setResult(data);
      if (data.resultado === "exitoso") setStatus("success");
      else if (data.razon === "DISPOSITIVO_BLOQUEADO") setStatus("locked");
      else setStatus("denied");
    },
    onError: () => setStatus("error"),
  });

  const guestMutation = useMutation({
    mutationFn: ({ inv, tit }: { inv: string; tit: string }) => postGuestCheckin(inv, tit),
    onSuccess: (data) => {
      setResult(data);
      if (data.resultado === "exitoso") setStatus("success");
      else if (data.razon === "DISPOSITIVO_BLOQUEADO") setStatus("locked");
      else setStatus("denied");
    },
    onError: () => setStatus("error"),
  });

  const qrMutation = useMutation({
    mutationFn: (payload: string) => postCheckinQr(payload),
    onSuccess: (data) => {
      setResult(data);
      if (data.resultado === "exitoso") setStatus("success");
      else if (data.razon === "DISPOSITIVO_BLOQUEADO") setStatus("locked");
      else setStatus("denied");
    },
    onError: () => setStatus("error"),
  });

  const mutation = mode === "member" ? memberMutation : guestMutation;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cedula.trim()) return;
    if (mode === "guest" && !cedulaTitular.trim()) return;
    setStatus("loading");
    if (mode === "member") {
      memberMutation.mutate(cedula.trim());
    } else {
      guestMutation.mutate({ inv: cedula.trim(), tit: cedulaTitular.trim() });
    }
  };

  const handleQrScan = () => {
    const payload = prompt("Ingrese el código QR (o escanee):");
    if (!payload) return;
    setStatus("loading");
    qrMutation.mutate(payload);
  };

  const handleReset = () => {
    setCedula("");
    setCedulaTitular("");
    setResult(null);
    setStatus("idle");
  };

  if (status === "success" && result) {
    const isCourtesy = result.cortesia === true;
    const isGuest = result.cupos_invitados !== null;
    return (
      <div className={`min-h-screen flex items-center justify-center ${isCourtesy ? "bg-purple-100" : isGuest ? "bg-blue-100" : "bg-green-100"} p-6`}>
        <div className="text-center max-w-lg">
          <div className={`text-8xl mb-6 ${isCourtesy ? "text-purple-600" : isGuest ? "text-blue-600" : "text-green-600"}`}>
            {isCourtesy ? "&#127873;" : isGuest ? "&#128101;" : "&#10003;"}
          </div>
          <h1 className={`text-4xl font-bold mb-4 ${isCourtesy ? "text-purple-800" : isGuest ? "text-blue-800" : "text-green-800"}`}>
            {isCourtesy ? "CORTESÍA DE PRIMER DÍA" : isGuest ? "INVITADO REGISTRADO" : "ACCESO PERMITIDO"}
          </h1>
          <p className={`text-3xl mb-2 ${isCourtesy ? "text-purple-700" : isGuest ? "text-blue-700" : "text-green-700"}`}>
            {result.mensaje}
          </p>
          {!isCourtesy && !isGuest && (
            <p className="text-2xl text-green-600">
              Visitas restantes: {result.visitas_restantes}
            </p>
          )}
          {isCourtesy && (
            <p className="text-xl text-purple-600 mt-4">
              Acérquese a recepción para afiliarse y seguir entrenando.
            </p>
          )}
          <button
            onClick={handleReset}
            className={`mt-8 text-white text-2xl font-bold py-4 px-10 rounded-lg ${isCourtesy ? "bg-purple-600 hover:bg-purple-700" : isGuest ? "bg-blue-600 hover:bg-blue-700" : "bg-green-600 hover:bg-green-700"}`}
            style={{ minWidth: 48, minHeight: 48 }}
          >
            Nueva búsqueda
          </button>
        </div>
      </div>
    );
  }

  if (status === "denied" && result) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-100 p-6">
        <div className="text-center max-w-lg">
          <div className="text-8xl mb-6 text-red-600">&#10007;</div>
          <h1 className="text-4xl font-bold text-red-800 mb-4">
            ACCESO DENEGADO
          </h1>
          <p className="text-3xl text-red-700 mb-2">{result.mensaje}</p>
          <button
            onClick={handleReset}
            className="mt-8 bg-red-600 hover:bg-red-700 text-white text-2xl font-bold py-4 px-10 rounded-lg"
            style={{ minWidth: 48, minHeight: 48 }}
          >
            Intentar de nuevo
          </button>
        </div>
      </div>
    );
  }

  if (status === "locked") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-yellow-100 p-6">
        <div className="text-center max-w-lg">
          <div className="text-8xl mb-6 text-yellow-600">&#128274;</div>
          <h1 className="text-4xl font-bold text-yellow-800 mb-4">
            DISPOSITIVO BLOQUEADO
          </h1>
          <p className="text-3xl text-yellow-700 mb-2">
            Demasiados intentos fallidos.
          </p>
          <p className="text-2xl text-yellow-600">
            Espere unos minutos o consulte al personal de recepción.
          </p>
          <button
            onClick={handleReset}
            className="mt-8 bg-yellow-600 hover:bg-yellow-700 text-white text-2xl font-bold py-4 px-10 rounded-lg"
            style={{ minWidth: 48, minHeight: 48 }}
          >
            Volver
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-6">
      <div className="text-center max-w-md w-full">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">GymFlow</h1>
        <p className="text-xl text-gray-600 mb-4">
          Ingrese su cédula para acceder
        </p>

        <div className="flex justify-center gap-2 mb-6">
          <button
            onClick={() => { setMode("member"); handleReset(); }}
            className={`px-4 py-2 rounded-lg font-semibold ${mode === "member" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700"}`}
          >
            Socio
          </button>
          <button
            onClick={() => { setMode("guest"); handleReset(); }}
            className={`px-4 py-2 rounded-lg font-semibold ${mode === "guest" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700"}`}
          >
            Invitado
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {mode === "guest" && (
            <input
              type="text"
              inputMode="numeric"
              value={cedulaTitular}
              onChange={(e) => setCedulaTitular(e.target.value)}
              placeholder="Cédula del socio titular"
              className="w-full text-center text-2xl py-4 px-4 border-2 border-gray-300 rounded-xl focus:outline-none focus:border-blue-500"
              disabled={status === "loading"}
              style={{ minHeight: 56 }}
            />
          )}
          <input
            type="text"
            inputMode="numeric"
            value={cedula}
            onChange={(e) => setCedula(e.target.value)}
            placeholder={mode === "guest" ? "Cédula del invitado" : "Número de cédula"}
            className="w-full text-center text-3xl py-6 px-4 border-2 border-gray-300 rounded-xl focus:outline-none focus:border-blue-500"
            autoFocus
            disabled={status === "loading"}
            style={{ minHeight: 64 }}
          />
          <button
            type="submit"
            disabled={status === "loading" || !cedula.trim() || (mode === "guest" && !cedulaTitular.trim())}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white text-3xl font-bold py-6 px-8 rounded-xl"
            style={{ minHeight: 64 }}
          >
            {status === "loading" ? "Validando..." : "INGRESAR"}
          </button>
        </form>

        <button
          onClick={handleQrScan}
          disabled={status === "loading"}
          className="mt-6 w-full bg-gray-700 hover:bg-gray-800 disabled:bg-gray-400 text-white text-xl font-bold py-4 px-8 rounded-xl"
        >
          &#128247; Escanear QR
        </button>

        {status === "error" && (
          <p className="mt-4 text-xl text-red-600">
            Error de conexión. Intente nuevamente.
          </p>
        )}
      </div>
    </div>
  );
}
