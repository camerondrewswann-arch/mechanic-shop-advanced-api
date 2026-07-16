from marshmallow import fields, validate

from ...extensions import ma
from ...models import Inventory


class InventorySchema(ma.SQLAlchemyAutoSchema):
    price = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        model = Inventory
        load_instance = False
        include_fk = True
        exclude = ("service_tickets",)


inventory_schema = InventorySchema()
inventory_items_schema = InventorySchema(many=True)
