# NexusERP – Shiv Furniture Factory Operating System

NexusERP is a customized, high-visibility manufacturing operating system designed specifically around the daily operations and critical pain points of **Shiv Furniture**. It replaces manual sheets and disconnected channels with a single, real-time command center linking sales demand, raw material inventory, BOM calculations, procurement suggestions, and manufacturing work orders.

---

## 🚀 Quick Start

### 1. Synchronize Dependencies
Ensure that the virtual environment packages are correctly installed and synchronized:
```bash
uv sync
```

### 2. Initialize Database & Seed Shiv Furniture Catalog
Reset the database schema and populate it with the complete Shiv Furniture master records (wood legs, tops, screws, cushions, dining tables, chairs, and their corresponding assembly BOM recipes):
```bash
.venv/bin/python app/seed/reset_db.py
```

### 3. Start Development Server
Launch the local development web server:
```bash
uv run flask run
```
Open [http://localhost:5000](http://localhost:5000) in your web browser.

---

## 🔑 Demo Login Credentials

You can test different operational permissions by logging in with the following default accounts (password is `<username>123` for role accounts):

| Username | Role | Primary Permissions |
| :--- | :--- | :--- |
| `owner` | **Business Owner** | Full management dashboard visibility, reports, audit logs |
| `inventory` | **Inventory Manager** | Product setup, inventory counts, adjustments, procurement triggers |
| `sales` | **Sales Rep** | Customer directory, Sales Orders, reserves stock, MTO checks |
| `purchase` | **Purchasing Agent** | Vendor registry, Purchase Orders, receives shipments |
| `manufacturing` | **Factory Operator** | BOM creation, Manufacturing Orders, work order execution |
| `cashier` | **POS Cashier** | Customer-facing Point of Sale checkout terminal |
| `admin` | **System Admin** | Global configuration and role/user management (password: `admin123`) |

---

## 🛠 Tech Stack

- **Core Framework**: Python 3.14, Flask 3.1
- **Database Layer**: SQLAlchemy (ORM), SQLite (Development) / PostgreSQL (Production)
- **Frontend & Styling**: Vanilla CSS, Bootstrap 5.3, Bootstrap Icons, custom glassmorphism components
- **Visualizations**: Chart.js (Interactive UI reports)
- **Migrations & Async**: Flask-Migrate, Flask-SocketIO
