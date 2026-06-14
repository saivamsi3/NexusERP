# NexusERP Architecture Specification

This document details the software architecture, database schemas, core domain logic, and cross-module workflows of the **NexusERP** system.

---

## 1. System Architecture

NexusERP is designed around a **Layered Architecture** pattern, enforcing separation of concerns between presentation, web requests, business domain services, and database persistence.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Presentation Layer (UI)                         │
│       - HTML5 Semantic Markup & Custom Styling                         │
│       - Bootstrap 5.3 & Bootstrap Icons CSS Framework                  │
│       - Dynamic Client Rendering (Jinja Templates, Vanilla JS)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP Requests / REST
┌───────────────────────────────────▼────────────────────────────────────┐
│                          API Router (Routes)                           │
│       - Flask Blueprints organizing HTTP route handlers                │
│       - Permission Decorators enforcing access control                 │
│       - WTForms Validation layer for clean request parameters          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Method Invocations
┌───────────────────────────────────▼────────────────────────────────────┐
│                     Business Logic Layer (Services)                    │
│       - Modular Service classes holding domain-specific workflows      │
│       - State Management machines (Reservation, Procurement engines)    │
│       - AI Integration controllers interfacing with external APIs      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ ORM Sessions
┌───────────────────────────────────▼────────────────────────────────────┐
│                    Data Access Layer (Models)                          │
│       - SQLAlchemy Domain Models mappings database tables              │
│       - Relationship mappings with cascading deletions                 │
│       - Standardized Audit Hook capturing state changes                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ SQLite Protocol
┌───────────────────────────────────▼────────────────────────────────────┐
│                        Database Layer (Storage)                        │
│       - SQLite persistent storage engine                               │
│       - Database Migrations managed via Alembic (Flask-Migrate)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Folder Structure

```text
app/
├── extensions/     # Third-party integrations (SQLAlchemy, LoginManager, Bcrypt, SocketIO)
├── models/         # Database entities (User, Product, SalesOrder, Bom, AuditLog, etc.)
├── routes/         # Flask blueprints mapping endpoints to view logic
├── services/       # Domain controllers implementing business workflows:
│   ├── auth/          # Authentication and authorization rules
│   ├── inventory/     # Inventory accounting, adjustments, and ledgering
│   ├── sales/         # Sales order workflows, order lines, and fulfillment
│   ├── purchase/      # Purchase order generation, supplier matching, and receiving
│   ├── manufacturing/ # Recipes (BOM), production ordering, work-center assignments
│   ├── procurement/   # Auto-replenishment engines (MTS & MTO rules)
│   ├── pos/           # Point of sale session management and terminal checkout
│   ├── analytics/     # Metrics calculation, KPI aggregations, and business health scoring
│   ├── audit/         # Operational action capturing and database change tracking
│   └── ai/            # Gemini-powered conversational business assistant
├── static/         # Public assets (custom stylesheets, browser scripts, images)
├── templates/      # Jinja templates split by domain blueprint
├── utils/          # Decorators, constants, custom validators, and barcode engines
└── seed/           # Seed scripts to populate initial user configurations and demo data
```

---

## 3. Database Schema & Core Entities

```mermaid
classDiagram
    class User {
        +int id
        +string username
        +string email
        +string password_hash
        +bool is_active
    }
    class Role {
        +int id
        +string name
        +string description
    }
    class Permission {
        +int id
        +string code
        +string name
    }
    class Product {
        +int id
        +string name
        +string sku
        +string barcode
        +string category
        +string product_type
        +float cost_price
        +float sales_price
        +int safety_stock
        +int reorder_level
        +string procurement_type
    }
    class Inventory {
        +int id
        +int product_id
        +int on_hand_qty
        +int reserved_qty
        +int incoming_qty
        +int outgoing_qty
    }
    class StockLedger {
        +int id
        +int product_id
        +string movement_type
        +int quantity
        +int balance_before
        +int balance_after
        +datetime created_at
    }
    class Customer {
        +int id
        +string name
        +float credit_limit
    }
    class SalesOrder {
        +int id
        +string order_number
        +int customer_id
        +string status
        +float total_amount
    }
    class SalesOrderLine {
        +int id
        +int sales_order_id
        +int product_id
        +int quantity
        +float unit_price
    }
    class Vendor {
        +int id
        +string name
        +int lead_time_days
    }
    class PurchaseOrder {
        +int id
        +string order_number
        +int vendor_id
        +string status
        +float total_amount
    }
    class PurchaseOrderLine {
        +int id
        +int purchase_order_id
        +int product_id
        +int quantity
        +float unit_cost
    }
    class Bom {
        +int id
        +int product_id
        +string name
        +float total_cost
    }
    class BomComponent {
        +int id
        +int bom_id
        +int product_id
        +int quantity
    }
    class ManufacturingOrder {
        +int id
        +string mo_number
        +int product_id
        +int bom_id
        +int quantity
        +string status
    }
    class WorkOrder {
        +int id
        +int mo_id
        +string operation_name
        +string status
        +int duration_minutes
    }
    class AuditLog {
        +int id
        +int user_id
        +string action
        +string module
        +string old_values
        +string new_values
        +datetime created_at
    }

    User "many" --> "many" Role
    Role "many" --> "many" Permission
    Product "1" --> "1" Inventory
    Product "1" --> "many" StockLedger
    Product "1" --> "many" SalesOrderLine
    Product "1" --> "many" PurchaseOrderLine
    Product "1" --> "many" BomComponent
    Product "1" --> "many" Bom
    Customer "1" --> "many" SalesOrder
    SalesOrder "1" --> "many" SalesOrderLine
    Vendor "1" --> "many" PurchaseOrder
    PurchaseOrder "1" --> "many" PurchaseOrderLine
    Bom "1" --> "many" BomComponent
    Bom "1" --> "many" ManufacturingOrder
    ManufacturingOrder "1" --> "many" WorkOrder
    User "1" --> "many" AuditLog
```

---

## 4. Key Business Workflows

### 4.1 Sales Demand-to-Delivery
Manages customer orders from creation through credit verification, inventory allocation, and fulfillment.

```mermaid
sequenceDiagram
    autonumber
    actor Sales as Sales Representative
    participant SO as Sales Module
    participant Inv as Inventory Module
    participant Mfg as Manufacturing Module
    participant Ledger as Stock Ledger

    Sales->>SO: Create Sales Order (Draft)
    Sales->>SO: Confirm Sales Order
    SO->>Inv: Validate Free Stock Availability (Free = OnHand - Reserved)
    alt Stock Available
        Inv-->>SO: Stock Validated
        SO->>Inv: Reserve Stock (reserved_qty += requested_qty)
        SO->>SO: Update Status to CONFIRMED
    else Stock Shortage (MTO / MTS Triggered)
        Inv-->>SO: Stock Shortage Detected
        SO->>Mfg: Request Manufacturing Order (MO)
        SO->>SO: Update Status to CONFIRMED
    end
    
    Note over SO, Inv: Fulfill Goods (Pick & Pack)
    
    Sales->>SO: Mark Order as Delivered
    SO->>Inv: Consume Stock
    Inv->>Inv: Update Balances (on_hand -= qty, reserved -= qty)
    Inv->>Ledger: Write Movement Entry (delivery)
    SO->>SO: Update Status to DELIVERED
```

### 4.2 Automated Procurement (Smart Purchasing)
Monitors component stock and triggers replenishment rules (Make-to-Stock reorder targets).

```mermaid
sequenceDiagram
    autonumber
    participant Engine as Procurement Engine
    participant Inv as Inventory Module
    participant PO as Purchase Module
    participant Vendor as Supplier Portal

    Loop Hourly Check
        Engine->>Inv: Check On-Hand Stock vs Minimum Stock Amount (Reorder Level)
        alt Stock <= Reorder Level
            Engine->>Engine: Calculate Replenishment Qty (safety_stock * 2)
            Engine->>Engine: Resolve Default Supplier for Product
            Engine->>PO: Generate Draft Purchase Order (PO)
            PO-->>Engine: Draft PO Created
        end
    end
    
    actor PurchaseAgent as Purchasing Agent
    PurchaseAgent->>PO: Review & Confirm PO
    PO->>Inv: Register Expected Stock (incoming_qty += PO_qty)
    PO->>Vendor: Send PO Notification
    
    actor WhseManager as Warehouse Manager
    Vendor->>WhseManager: Ship Components to Warehouse
    WhseManager->>PO: Receive Goods (GRN Entry)
    PO->>Inv: Update Balances (on_hand += received_qty, incoming -= received_qty)
    Inv->>Inv: Write Stock Ledger Entry (receipt)
    PO->>PO: Update Status to RECEIVED
```

### 4.3 Manufacturing Execution
Explodes product recipes, tracks component consumption, and registers manufactured products.

```mermaid
sequenceDiagram
    autonumber
    actor Mgr as Production Manager
    participant MO as Manufacturing Order
    participant Recipe as Product Recipe (BOM)
    participant Inv as Inventory Module
    participant Task as Production Task (Work Order)

    Mgr->>MO: Create Production Order
    MO->>Recipe: Explode Recipe Components & Routing Operations
    Recipe-->>MO: Components & Tasks List
    MO->>MO: Confirm Production Order
    
    loop Check Component Availability
        MO->>Inv: Verify Component On-Hand
        alt Component Missing
            MO->>Inv: Trigger Sourcing / Smart Purchase Request
        else Component Available
            MO->>Inv: Reserve Components (reserved_qty += required_qty)
        end
    end

    MO->>Task: Generate Production Tasks (Assembly, Painting, Packaging)
    
    actor Operator as Shop Floor Operator
    Operator->>Task: Start Task (Assembly)
    Task->>Inv: Consume Reserved Components (on_hand -= qty, reserved -= qty)
    Operator->>Task: Complete Task (Assembly)
    Operator->>Task: Start & Complete Painting / Packaging
    
    Task-->>MO: All Tasks Finished
    MO->>Inv: Add Finished Product to Inventory (on_hand += produced_qty)
    MO->>MO: Update Status to COMPLETED
```

---

## 5. Security & Permission Matrix

Access controls are managed via Role-Based Access Control (RBAC). Blueprint endpoints are secured using `@permission_required("code")` checks.

| Role | Domain Modules Access | Allowed Permissions |
| :--- | :--- | :--- |
| **System Admin** | User settings, Database parameters, Log view | `view_users`, `manage_roles`, `view_audit_logs`, `db_reset` |
| **Business Owner**| Dashboard analytics, Financial summaries, Copilot | `view_dashboard`, `view_reports`, `view_analytics`, `use_copilot` |
| **Sales Rep** | Customers catalog, Sales orders, Terminal checkout | `view_customers`, `manage_customers`, `manage_sales`, `confirm_sales` |
| **Inventory Mgr** | Products list, Stock adjustments, Transfers | `view_products`, `manage_products`, `view_stock`, `adjust_stock` |
| **Purchasing Agent**| Suppliers registry, Purchase orders | `view_vendors`, `manage_vendors`, `manage_purchases`, `receive_purchases` |
| **Production Mgr**| BOM definitions, Production scheduling, Tasks | `view_recipes`, `manage_recipes`, `manage_production`, `complete_tasks` |
| **POS Cashier** | Retail sales terminal | `pos_checkout`, `manage_sessions` |

---

## 6. Audit Logging System

The Audit Engine captures modifications to tracking entities. Every write operation writes a record to the `AuditLog` database table.

```json
{
  "timestamp": "2026-06-14T09:40:00.123Z",
  "user_id": 4,
  "action": "UPDATE",
  "module": "Sales Order",
  "reference_number": "SO-202606-0012",
  "old_values": {
    "status": "CONFIRMED",
    "delivery_risk": "MEDIUM"
  },
  "new_values": {
    "status": "DELIVERED",
    "delivery_risk": "LOW"
  },
  "ip_address": "127.0.0.1"
}
```

---

## 7. AI Operations Copilot Integration

The AI Operations Copilot parses operational commands to deliver contextual summaries. It processes database entities in real-time to compute structured insights.

```text
User Command: "Show me all orders at risk."
        │
        ▼
[Intent Engine] parses keywords: "orders", "at risk", "delayed"
        │
        ▼
[SQL Aggregator] queries SQLite:
 - SalesOrders where status = 'CONFIRMED' and expected_delivery < NOW()
 - Inventory where free_to_use_qty < safety_stock
        │
        ▼
[Context Builder] compiles data payload
        │
        ▼
[Google Gemini API] processes prompt with schema:
 - Generates natural language summary explaining bottlenecks (e.g., missing wood planks for Table assembly).
```
