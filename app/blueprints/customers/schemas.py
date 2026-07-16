from marshmallow import fields, validate

from ...extensions import ma
from ...models import Customer


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True, required=True, validate=validate.Length(min=6))
    service_tickets = fields.Method("get_service_tickets", dump_only=True)

    class Meta:
        model = Customer
        load_instance = False
        include_fk = True
        exclude = ("password_hash",)

    def get_service_tickets(self, customer):
        return [
            {
                "id": ticket.id,
                "description": ticket.description,
                "status": ticket.status,
            }
            for ticket in customer.service_tickets
        ]


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = CustomerSchema(only=("email", "password"))
