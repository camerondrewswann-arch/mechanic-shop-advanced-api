from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


service_mechanic = db.Table(
    "service_mechanic",
    db.Column("service_ticket_id", db.Integer, db.ForeignKey("service_tickets.id"), primary_key=True),
    db.Column("mechanic_id", db.Integer, db.ForeignKey("mechanics.id"), primary_key=True),
)

service_inventory = db.Table(
    "service_inventory",
    db.Column("service_ticket_id", db.Integer, db.ForeignKey("service_tickets.id"), primary_key=True),
    db.Column("inventory_id", db.Integer, db.ForeignKey("inventory.id"), primary_key=True),
)


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    service_tickets = db.relationship(
        "ServiceTicket",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Mechanic(db.Model):
    __tablename__ = "mechanics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    specialty = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)

    service_tickets = db.relationship(
        "ServiceTicket",
        secondary=service_mechanic,
        back_populates="mechanics",
        lazy=True,
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)

    service_tickets = db.relationship(
        "ServiceTicket",
        secondary=service_inventory,
        back_populates="inventory_parts",
        lazy=True,
    )


class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="open")
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)

    customer = db.relationship("Customer", back_populates="service_tickets")
    mechanics = db.relationship(
        "Mechanic",
        secondary=service_mechanic,
        back_populates="service_tickets",
        lazy=True,
    )
    inventory_parts = db.relationship(
        "Inventory",
        secondary=service_inventory,
        back_populates="service_tickets",
        lazy=True,
    )
