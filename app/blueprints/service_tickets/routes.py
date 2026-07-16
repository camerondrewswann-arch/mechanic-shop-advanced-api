from flask import jsonify, request

from ...auth import mechanic_token_required, token_required
from ...extensions import cache, db
from ...models import Inventory, Mechanic, ServiceTicket
from . import service_tickets_bp
from .schemas import service_ticket_schema, service_tickets_schema


@service_tickets_bp.post("/")
@token_required
def create_service_ticket(auth_customer_id):
    data = service_ticket_schema.load(request.get_json() or {})
    ticket = ServiceTicket(
        description=data["description"],
        status=data.get("status", "open"),
        customer_id=auth_customer_id,
    )
    db.session.add(ticket)
    db.session.commit()
    cache.clear()
    return jsonify(service_ticket_schema.dump(ticket)), 201


@service_tickets_bp.get("/")
@cache.cached(timeout=60, query_string=True)
def get_service_tickets():
    query = ServiceTicket.query
    status = request.args.get("status")
    customer_id = request.args.get("customer_id", type=int)

    if status:
        query = query.filter_by(status=status)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)

    return jsonify(service_tickets_schema.dump(query.order_by(ServiceTicket.id).all()))


@service_tickets_bp.get("/<int:ticket_id>")
def get_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"message": "Service ticket not found"}), 404
    return jsonify(service_ticket_schema.dump(ticket))


@service_tickets_bp.put("/<int:ticket_id>")
@mechanic_token_required
def update_service_ticket(auth_mechanic_id, ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"message": "Service ticket not found"}), 404

    data = service_ticket_schema.load(request.get_json() or {}, partial=True)
    if "description" in data:
        ticket.description = data["description"]
    if "status" in data:
        ticket.status = data["status"]

    db.session.commit()
    cache.clear()
    return jsonify(service_ticket_schema.dump(ticket))


@service_tickets_bp.put("/<int:ticket_id>/edit")
@mechanic_token_required
def edit_ticket_mechanics(auth_mechanic_id, ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"message": "Service ticket not found"}), 404

    data = request.get_json() or {}
    add_ids = data.get("add_ids", [])
    remove_ids = data.get("remove_ids", [])

    if not isinstance(add_ids, list) or not isinstance(remove_ids, list):
        return jsonify({"message": "add_ids and remove_ids must be lists"}), 400

    requested_ids = set(add_ids) | set(remove_ids)
    mechanics = Mechanic.query.filter(Mechanic.id.in_(requested_ids)).all() if requested_ids else []
    mechanic_by_id = {mechanic.id: mechanic for mechanic in mechanics}
    missing_ids = sorted(requested_ids - set(mechanic_by_id))
    if missing_ids:
        return jsonify({"message": "Mechanic IDs not found", "missing_ids": missing_ids}), 404

    for mechanic_id in add_ids:
        mechanic = mechanic_by_id[mechanic_id]
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    for mechanic_id in remove_ids:
        mechanic = mechanic_by_id[mechanic_id]
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    cache.clear()
    return jsonify(service_ticket_schema.dump(ticket))


@service_tickets_bp.put("/<int:ticket_id>/add-part/<int:part_id>")
@mechanic_token_required
def add_part_to_ticket(auth_mechanic_id, ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"message": "Service ticket not found"}), 404

    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"message": "Inventory item not found"}), 404

    if part in ticket.inventory_parts:
        return jsonify({"message": "Part already assigned to this ticket"}), 409

    ticket.inventory_parts.append(part)
    db.session.commit()
    cache.clear()
    return jsonify(service_ticket_schema.dump(ticket))


@service_tickets_bp.put("/<int:ticket_id>/remove-part/<int:part_id>")
@mechanic_token_required
def remove_part_from_ticket(auth_mechanic_id, ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"message": "Service ticket not found"}), 404

    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"message": "Inventory item not found"}), 404

    if part not in ticket.inventory_parts:
        return jsonify({"message": "Part is not assigned to this ticket"}), 404

    ticket.inventory_parts.remove(part)
    db.session.commit()
    cache.clear()
    return jsonify(service_ticket_schema.dump(ticket))


@service_tickets_bp.delete("/<int:ticket_id>")
@mechanic_token_required
def delete_service_ticket(auth_mechanic_id, ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"message": "Service ticket not found"}), 404

    db.session.delete(ticket)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Service ticket deleted"})
