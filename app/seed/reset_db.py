import sys
import os

# Add the root directory to path to enable running as script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app import create_app
from app.extensions import db
from app.seed.demo_data import seed_demo_data

def reset_and_seed():
    app = create_app()
    with app.app_context():
        print("Dropping all existing database tables...")
        db.drop_all()
        print("Creating all database tables...")
        db.create_all()
        print("Seeding new Shiv Furniture demo data...")
        seed_demo_data()
        print("Database reset and seeding completed successfully!")

if __name__ == "__main__":
    reset_and_seed()
