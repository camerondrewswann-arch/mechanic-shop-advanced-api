from flask import jsonify, request
from sqlalchemy import func

from ...auth import encode_mechanic_token, mechanic_token_required
from ...extensions import cache, db, limiter
from ...models import Mechanic, service_mechanic
from . import mechanics_bp
from .schemas import mechanic_login_schema, mechanic_schema, mechanics_schema


@mechanics_bp.post("/")
@limiter.limit("10 per minute")
def create_mechanic():
    data = mechanic_schema.load(request.get_json() or {})
    if Mechanic.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 409

    mechanic = Mechanic(
        name=data["name"],
        email=data["email"],
        specialty=data.get("specialty"),
    )
    mechanic.set_password(data["password"])
    db.session.add(mechanic)
    db.session.commit()
    cache.clear()
    return jsonify(mechanic_schema.dump(mechanic)), 201


@mechanics_bp.post("/login")
@limiter.limit("5 per minute")
def login_mechanic():
    data = mechanic_login_schema.load(request.get_json() or {})
    mechanic = Mechanic.query.filter_by(email=data["email"]).first()
    if not mechanic or not mechanic.check_password(data["password"]):
        return jsonify({"message": "Invalid email or password"}), 401

    return jsonify(
        {
            "token": encode_mechanic_token(mechanic.id),
            "mechanic": mechanic_schema.dump(mechanic),
        }
    )


@mechanics_bp.get("/")
@cache.cached(timeout=60, query_string=True)
def get_mechanics():
    return jsonify(mechanics_schema.dump(Mechanic.query.order_by(Mechanic.id).all()))


@mechanics_bp.get("/ranked")
@cache.cached(timeout=60, query_string=True)
def ranked_mechanics():
    rows = (
        db.session.query(Mechanic, func.count(service_mechanic.c.service_ticket_id).label("ticket_count"))
        .outerjoin(service_mechanic, Mechanic.id == service_mechanic.c.mechanic_id)
        .group_by(Mechanic.id)
        .order_by(func.count(service_mechanic.c.service_ticket_id).desc(), Mechanic.name.asc())
        .all()
    )
    return jsonify(
        [
            {
                **mechanic_schema.dump(mechanic),
                "ticket_count": ticket_count,
            }
            for mechanic, ticket_count in rows
        ]
    )


@mechanics_bp.get("/<int:mechanic_id>")
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"message": "Mechanic not found"}), 404
    return jsonify(mechanic_schema.dump(mechanic))


@mechanics_bp.put("/<int:mechanic_id>")
@mechanic_token_required
def update_mechanic(auth_mechanic_id, mechanic_id):
    if auth_mechanic_id != mechanic_id:
        return jsonify({"message": "You may only update your own account"}), 403

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"message": "Mechanic not found"}), 404

    data = mechanic_schema.load(request.get_json() or {}, partial=True)
    if "email" in data:
        existing = Mechanic.query.filter(Mechanic.email == data["email"], Mechanic.id != mechanic_id).first()
        if existing:
            return jsonify({"message": "Email already registered"}), 409
        mechanic.email = data["email"]
    if "name" in data:
        mechanic.name = data["name"]
    if "specialty" in data:
        mechanic.specialty = data["specialty"]
    if "password" in data:
        mechanic.set_password(data["password"])

    db.session.commit()
    cache.clear()
    return jsonify(mechanic_schema.dump(mechanic))


@mechanics_bp.delete("/<int:mechanic_id>")
@mechanic_token_required
def delete_mechanic(auth_mechanic_id, mechanic_id):
    if auth_mechanic_id != mechanic_id:
        return jsonify({"message": "You may only delete your own account"}), 403

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"message": "Mechanic not found"}), 404

    db.session.delete(mechanic)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Mechanic deleted"})
