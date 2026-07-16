from flask import jsonify, request

from ...auth import mechanic_token_required
from ...extensions import cache, db
from ...models import Inventory
from . import inventory_bp
from .schemas import inventory_items_schema, inventory_schema


@inventory_bp.post("/")
@mechanic_token_required
def create_inventory_item(auth_mechanic_id):
    data = inventory_schema.load(request.get_json() or {})
    item = Inventory(name=data["name"], price=data["price"])
    db.session.add(item)
    db.session.commit()
    cache.clear()
    return jsonify(inventory_schema.dump(item)), 201


@inventory_bp.get("/")
@cache.cached(timeout=60, query_string=True)
def get_inventory_items():
    return jsonify(inventory_items_schema.dump(Inventory.query.order_by(Inventory.id).all()))


@inventory_bp.get("/<int:item_id>")
def get_inventory_item(item_id):
    item = db.session.get(Inventory, item_id)
    if not item:
        return jsonify({"message": "Inventory item not found"}), 404
    return jsonify(inventory_schema.dump(item))


@inventory_bp.put("/<int:item_id>")
@mechanic_token_required
def update_inventory_item(auth_mechanic_id, item_id):
    item = db.session.get(Inventory, item_id)
    if not item:
        return jsonify({"message": "Inventory item not found"}), 404

    data = inventory_schema.load(request.get_json() or {}, partial=True)
    if "name" in data:
        item.name = data["name"]
    if "price" in data:
        item.price = data["price"]

    db.session.commit()
    cache.clear()
    return jsonify(inventory_schema.dump(item))


@inventory_bp.delete("/<int:item_id>")
@mechanic_token_required
def delete_inventory_item(auth_mechanic_id, item_id):
    item = db.session.get(Inventory, item_id)
    if not item:
        return jsonify({"message": "Inventory item not found"}), 404

    for ticket in list(item.service_tickets):
        ticket.inventory_parts.remove(item)
    db.session.delete(item)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Inventory item deleted"})
