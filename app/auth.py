from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import current_app, jsonify, request
from jose import ExpiredSignatureError, JWTError, jwt


def _encode_token(subject_id: int, role: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        hours=current_app.config["JWT_EXPIRES_HOURS"]
    )
    payload = {
        "sub": str(subject_id),
        "role": role,
        "exp": expires,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def encode_token(customer_id: int) -> str:
    return _encode_token(customer_id, "customer")


def encode_mechanic_token(mechanic_id: int) -> str:
    return _encode_token(mechanic_id, "mechanic")


def _read_bearer_token():
    header = request.headers.get("Authorization", "")
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None, (jsonify({"message": "Bearer token required"}), 401)

    try:
        payload = jwt.decode(
            parts[1],
            current_app.config["JWT_SECRET_KEY"],
            algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
        return payload, None
    except ExpiredSignatureError:
        return None, (jsonify({"message": "Token has expired"}), 401)
    except JWTError:
        return None, (jsonify({"message": "Invalid token"}), 401)


def token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        payload, error = _read_bearer_token()
        if error:
            return error
        if payload.get("role") != "customer":
            return jsonify({"message": "Customer token required"}), 403
        return function(int(payload["sub"]), *args, **kwargs)

    return decorated


def mechanic_token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        payload, error = _read_bearer_token()
        if error:
            return error
        if payload.get("role") != "mechanic":
            return jsonify({"message": "Mechanic token required"}), 403
        return function(int(payload["sub"]), *args, **kwargs)

    return decorated
