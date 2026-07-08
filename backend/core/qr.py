import base64
import json


def decode_qr(payload: str) -> dict | None:
    try:
        decoded = base64.b64decode(payload)
        data = json.loads(decoded)
        if "cedula" in data:
            return {"cedula": data["cedula"]}
        if "id" in data:
            return {"id": data["id"]}
        return None
    except Exception:
        return None


def encode_qr(cedula: str) -> str:
    data = json.dumps({"cedula": cedula})
    return base64.b64encode(data.encode()).decode()
