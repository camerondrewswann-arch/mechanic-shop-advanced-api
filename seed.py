from app import create_app
from app.extensions import db
from app.models import Customer, Inventory, Mechanic, ServiceTicket


app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    customer = Customer(name="Demo Customer", email="customer@example.com")
    customer.set_password("password123")

    mechanic = Mechanic(
        name="Demo Mechanic",
        email="mechanic@example.com",
        specialty="Brakes and diagnostics",
    )
    mechanic.set_password("wrench123")

    part = Inventory(name="Brake Pad Set", price=79.99)
    ticket = ServiceTicket(
        description="Replace front brake pads",
        status="open",
        customer=customer,
    )
    ticket.mechanics.append(mechanic)
    ticket.inventory_parts.append(part)

    db.session.add_all([customer, mechanic, part, ticket])
    db.session.commit()
    print("Seed complete.")
    print("Customer: customer@example.com / password123")
    print("Mechanic: mechanic@example.com / wrench123")
