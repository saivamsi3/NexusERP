from app.extensions import db
from app.models.customer import Customer
from app.models.vendor import Vendor
from app.models.user import User
from app.models.role import Role
from app.seed.roles_seed import seed_roles_and_permissions
from app.seed.sample_products import seed_sample_products


def seed_demo_data():
    seed_roles_and_permissions()
    # Create admin user
    if not User.query.filter_by(username="admin").first():
        admin_role = Role.query.filter_by(name="Admin").first()
        admin = User(username="admin", email="admin@nexuserp.com", full_name="System Admin")
        admin.set_password("admin123")
        admin.role_id = admin_role.id if admin_role else None
        db.session.add(admin)

    # Demo users representing each role
    demo_users_data = [
        {"username": "sales", "email": "sales@nexuserp.com", "full_name": "Sales Rep", "password": "sales123", "role_name": "Sales User"},
        {"username": "purchase", "email": "purchase@nexuserp.com", "full_name": "Purchasing Agent", "password": "purchase123", "role_name": "Purchase User"},
        {"username": "manufacturing", "email": "manufacturing@nexuserp.com", "full_name": "Factory Operator", "password": "manufacturing123", "role_name": "Manufacturing User"},
        {"username": "inventory", "email": "inventory@nexuserp.com", "full_name": "Warehouse Manager", "password": "inventory123", "role_name": "Inventory Manager"},
        {"username": "owner", "email": "owner@nexuserp.com", "full_name": "Business Owner", "password": "owner123", "role_name": "Business Owner"},
        {"username": "cashier", "email": "cashier@nexuserp.com", "full_name": "POS Cashier", "password": "cashier123", "role_name": "POS Cashier"},
    ]

    for ud in demo_users_data:
        if not User.query.filter_by(username=ud["username"]).first():
            role = Role.query.filter_by(name=ud["role_name"]).first()
            user = User(username=ud["username"], email=ud["email"], full_name=ud["full_name"])
            user.set_password(ud["password"])
            user.role_id = role.id if role else None
            db.session.add(user)
    db.session.commit()
    seed_sample_products()
    # Customers
    customers_data = [
        {"name": "Acme Corp", "contact_person": "John Doe", "email": "john@acme.com", "phone": "555-0101", "city": "New York", "state": "NY"},
        {"name": "Global Industries", "contact_person": "Jane Smith", "email": "jane@global.com", "phone": "555-0102", "city": "Chicago", "state": "IL"},
        {"name": "TechParts Ltd", "contact_person": "Bob Wilson", "email": "bob@techparts.com", "phone": "555-0103", "city": "San Francisco", "state": "CA"},
    ]
    for cd in customers_data:
        if not Customer.query.filter_by(email=cd["email"]).first():
            db.session.add(Customer(**cd))
    # Vendors
    vendors_data = [
        {"name": "SteelMasters Inc", "contact_person": "Alice Brown", "email": "alice@steelmasters.com", "phone": "555-0201", "city": "Detroit", "state": "MI", "lead_time_days": 7},
        {"name": "RawSupply Co", "contact_person": "Charlie Davis", "email": "charlie@rawsupply.com", "phone": "555-0202", "city": "Houston", "state": "TX", "lead_time_days": 5},
        {"name": "PackPro Ltd", "contact_person": "Diana Evans", "email": "diana@packpro.com", "phone": "555-0203", "city": "Seattle", "state": "WA", "lead_time_days": 3},
    ]
    for vd in vendors_data:
        if not Vendor.query.filter_by(email=vd["email"]).first():
            db.session.add(Vendor(**vd))
    db.session.commit()
