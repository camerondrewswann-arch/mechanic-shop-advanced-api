from marshmallow import fields, validate

from ...extensions import ma
from ...models import ServiceTicket


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    customer_id = fields.Integer(load_only=True, required=False)
    status = fields.String(validate=validate.OneOf(["open", "in progress", "completed", "cancelled"]))
    customer = fields.Method("get_customer", dump_only=True)
    mechanics = fields.Method("get_mechanics", dump_only=True)
    inventory_parts = fields.Method("get_inventory_parts", dump_only=True)

    class Meta:
        model = ServiceTicket
        load_instance = False
        include_fk = True
        exclude = ()

    def get_customer(self, ticket):
        return {
            "id": ticket.customer.id,
            "name": ticket.customer.name,
            "email": ticket.customer.email,
        }

    def get_mechanics(self, ticket):
        return [
            {
                "id": mechanic.id,
                "name": mechanic.name,
                "email": mechanic.email,
                "specialty": mechanic.specialty,
            }
            for mechanic in ticket.mechanics
        ]

    def get_inventory_parts(self, ticket):
        return [
            {"id": part.id, "name": part.name, "price": part.price}
            for part in ticket.inventory_parts
        ]


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
