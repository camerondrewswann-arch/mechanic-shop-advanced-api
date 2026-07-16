from marshmallow import fields, validate

from ...extensions import ma
from ...models import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True, required=True, validate=validate.Length(min=6))
    ticket_count = fields.Integer(dump_only=True)

    class Meta:
        model = Mechanic
        load_instance = False
        include_fk = True
        exclude = ("password_hash", "service_tickets")


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
mechanic_login_schema = MechanicSchema(only=("email", "password"))
