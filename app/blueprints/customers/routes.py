from flask import jsonify, request

from ...auth import encode_token, token_required
from ...extensions import cache, db, limiter
from ...models import Customer, ServiceTicket
from ..service_tickets.schemas import service_tickets_schema
from . import customers_bp
from .schemas import customer_schema, customers_schema, login_schema


@customers_bp.post("/")
@limiter.limit("10 per minute")
def create_customer():
    data = customer_schema.load(request.get_json() or {})
    if Customer.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 409

    customer = Customer(name=data["name"], email=data["email"])
    customer.set_password(data["password"])
    db.session.add(customer)
    db.session.commit()
    cache.clear()
    return jsonify(customer_schema.dump(customer)), 201


@customers_bp.post("/login")
@limiter.limit("5 per minute")
def login_customer():
    data = login_schema.load(request.get_json() or {})
    customer = Customer.query.filter_by(email=data["email"]).first()
    if not customer or not customer.check_password(data["password"]):
        return jsonify({"message": "Invalid email or password"}), 401

    return jsonify({"token": encode_token(customer.id), "customer": customer_schema.dump(customer)})


@customers_bp.get("/")
@cache.cached(timeout=60, query_string=True)
def get_customers():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    per_page = max(1, min(per_page, 50))

    pagination = Customer.query.order_by(Customer.id).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )
    return jsonify(
        {
            "items": customers_schema.dump(pagination.items),
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
            "total": pagination.total,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    )


@customers_bp.get("/<int:customer_id>")
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    return jsonify(customer_schema.dump(customer))


@customers_bp.get("/my-tickets")
@token_required
def get_my_tickets(auth_customer_id):
    tickets = ServiceTicket.query.filter_by(customer_id=auth_customer_id).order_by(ServiceTicket.id).all()
    return jsonify(service_tickets_schema.dump(tickets))


@customers_bp.put("/<int:customer_id>")
@token_required
def update_customer(auth_customer_id, customer_id):
    if auth_customer_id != customer_id:
        return jsonify({"message": "You may only update your own account"}), 403

    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    data = customer_schema.load(request.get_json() or {}, partial=True)
    if "email" in data:
        existing = Customer.query.filter(Customer.email == data["email"], Customer.id != customer_id).first()
        if existing:
            return jsonify({"message": "Email already registered"}), 409
        customer.email = data["email"]
    if "name" in data:
        customer.name = data["name"]
    if "password" in data:
        customer.set_password(data["password"])

    db.session.commit()
    cache.clear()
    return jsonify(customer_schema.dump(customer))


@customers_bp.delete("/<int:customer_id>")
@token_required
def delete_customer(auth_customer_id, customer_id):
    if auth_customer_id != customer_id:
        return jsonify({"message": "You may only delete your own account"}), 403

    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Customer deleted"})
