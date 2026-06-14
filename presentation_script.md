# NexusERP: Live Demonstration & Presentation Script

This script has been updated to align perfectly with the actual database configurations, user accounts, routes, and simplified business terminology used in **NexusERP**.

---

## 🔑 Demo Account Credentials Quick Reference

| Username | Password | Role | Primary Features to Show |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | System Admin | User & Role Management, System Purge/Reset settings |
| `owner` | `owner123` | Business Owner | Factory Control Center, Analytics Dashboard, Reports |
| `inventory` | `inventory123` | Inventory Manager | Product Master, Stock Adjustments, Smart Purchasing Autopilot |
| `sales` | `sales123` | Sales User | Customer registry, Sales Orders, Delivery Risk Predictor |
| `purchase` | `purchase123` | Purchase User | Supplier Directory, Purchase Orders, Stock Receiving |
| `manufacturing` | `manufacturing123` | Manufacturing User | Product Recipes (BOM), Production Orders, Production Tasks |
| `cashier` | `cashier123` | POS Cashier | POS Terminal Checkout |

---

## 🎙️ Presentation Script

### 1. Introduction: The Problem & The Solution
**Speaker:**
> "Good morning, everyone. 
> 
> Today, we are presenting **NexusERP**—an intelligent manufacturing operating system designed to manage the complete business workflow from **Demand to Delivery**.
> 
> Many small and medium discrete manufacturing businesses still manage their operations using spreadsheets, fragmented WhatsApp group chats, and disconnected software systems. Because of this, they face constant headaches: inaccurate stock levels, delayed procurement, blind spots in production planning, duplicate manual entries, and a complete lack of real-time operational visibility.
> 
> To solve this problem, we developed **NexusERP**. Built on a lightweight, modular Flask architecture with a SQLite database, NexusERP integrates Product Management, Inventory Tracking, Sales, Smart Purchasing Autopilot, Purchasing, Manufacturing, Analytics, POS, and an AI Operations Copilot into a single, cohesive source of truth."
>
> *[Action: Show the login screen at `/auth/login`]*

---

### 2. System Administrator Portal
**Speaker:**
> "Let's begin by logging in as the **System Administrator** using the username `admin` and password `admin123`.
> 
> The Admin is responsible for secure access control across the entire system. From the Admin Portal, we can manage users, assign roles, and configure specific permissions.
> 
> Additionally, one of the vital utilities we built for developers and demo environments is the **Purge Business Data** utility in the Admin Settings. With a single confirmation code, we can purge all business transactions—such as sales orders, production orders, and stock movements—while preserving all user credentials, roles, and security rules. This makes it incredibly easy to reset the system for successive demo runs."
>
> *[Action: Navigate to `/auth/users` and show the user list. Then go to Settings at `/auth/settings` to point out the Purge Business Data section. Log out.]*

---

### 3. Business Owner: Analytics & Factory Control Center
**Speaker:**
> "Next, we log in as the **Business Owner** using the username `owner` and password `owner123`.
> 
> The Owner gets a complete birds-eye view of factory operations. First, they land on the **Factory Control Center**. This dashboard gives them instant visibility into pending Sales Orders, the active Production Order queue, pending Purchase Orders, delayed shipments, and critical material shortages.
> 
> When the owner navigates to the **Analytics Dashboard**, they see interactive, real-time Chart.js visualizations. They can monitor monthly revenue trends, compare sales vs. purchasing costs, view product category valuations, and review top-selling product metrics to make data-driven decisions."
>
> *[Action: Log in as `owner`. Show the Home Dashboard `/dashboard/` containing KPI cards and delayed order tables. Navigate to `/analytics/` to show charts for Revenue, Inventory Valuations, and Top Products. Log out.]*

---

### 4. Inventory Manager: Products & Sourcing
**Speaker:**
> "Now, we log in as the **Inventory Manager** using the username `inventory` and password `inventory123`.
> 
> The Inventory Manager manages the catalog and stock levels. Here on the **Products** page, products are configured with clear parameters: SKU, category, Selling Price, and Unit Cost. 
> 
> Most importantly, we configure the **Sourcing Method** for each product:
> * **Stock Before Demand** (Make to Stock - MTS): Ideal for high-turnover items.
> * **Stock After Demand** (Make to Order - MTO): Used for custom end-products.
> 
> We also define the **Minimum Stock Amount** (Reorder Level) and the **Extra Buffer Stock** (Safety Stock) which serve as the foundation for our automated purchasing logic."
>
> *[Action: Log in as `inventory`. Navigate to `/products/` and view details of a finished product (e.g., Dining Table, SKU `FG-TAB-001`) and a component (e.g., Wood Planks, SKU `RAW-WDP-001`). Show the Sourcing Method, Unit Cost, and Minimum Stock Amount fields. Log out.]*

---

### 5. Sales User: Sales Orders & Delivery Risk Predictor
**Speaker:**
> "Let's log in as the **Sales User** using the username `sales` and password `sales123`.
> 
> When a customer (e.g., Acme Corp) places an order, the Sales User creates a **Sales Order**. 
> 
> To prevent sales reps from overpromising, we built a standout feature: the **Delivery Risk Predictor**. When viewing a draft sales order, the predictor automatically calculates a risk level (Low, Medium, or High) based on current physical stock, component availability in the recipe, and the manufacturing queue. It shows exactly why an order is at risk (e.g., component shortages), ensuring we only commit to delivery dates we can actually hit."
>
> *[Action: Log in as `sales`. Navigate to `/sales/` and create a Sales Order for a customer. Open the order details and point out the 'Delivery Risk Predictor' widget on the right sidebar showing the risk rating (e.g., High Risk due to component shortages). Log out.]*

---

### 6. Smart Purchasing Autopilot: Automated Replenishment
**Speaker:**
> "Let's log back in as the **Inventory Manager** (or Admin) to solve the shortage we just identified. We navigate to the **Smart Purchasing Autopilot** dashboard.
> 
> The Smart Purchasing engine can run in three modes: **Manual**, **Semi-Automatic**, and **Fully Automatic**.
> 
> When we run the autopilot, the engine automatically calculates shortages. For any finished goods with shortages, it creates draft **Production Orders**. For any components with shortages, it determines the best supplier based on price and lead times, then auto-creates draft **Purchase Orders**.
> 
> We also integrated the **AI Procurement Advisor** directly onto this page. It parses our live database status to display natural-language, actionable guidance telling us exactly what is critical today and what stockouts are predicted for the coming week."
>
> *[Action: Log in as `inventory`. Go to `/procurement/`. Point out the AI Procurement Advisor's text suggestions. Click the 'Run Autopilot' button. Show the newly created draft Purchase Orders and Production Orders on the dashboard. Log out.]*

---

### 7. Purchase User: Procurement & Supplier Receiving
**Speaker:**
> "We log in as the **Purchase User** using the username `purchase` and password `purchase123`.
> 
> The Purchase User manages supplier relationships and reviews the draft Purchase Orders generated by the Autopilot.
> 
> Once confirmed, the Purchase User executes the order. When the shipment physically arrives, the user clicks **Receive Products**. The system automatically increases the physical inventory count, logs a stock movement in the Ledger, and updates the status to 'Fully Received' in real time."
>
> *[Action: Log in as `purchase`. Go to `/purchase/` to see the POs. Open the draft PO, click 'Confirm', then navigate to the 'Receive' tab and click 'Receive Products'. Go to `/inventory/` to show that the component stock level has increased. Log out.]*

---

### 8. Manufacturing User: Recipes & Production Tasks
**Speaker:**
> "Now that the components are in stock, we log in as the **Manufacturing User** using `manufacturing` and `manufacturing123`.
> 
> We navigate to **Product Recipes** (BOM) to see the exact ingredients required for assembly (e.g., 4 Wood Legs, 1 Table Top, 12 Screws, and Paint for a Dining Table).
> 
> We then open the auto-generated **Production Order** (MO). Since components are now available, we click 'Confirm' to reserve them from stock. The system moves the order to 'In Progress' and generates specific **Production Tasks** (Work Orders) for each workstation: Assembly, Painting, and Packaging. 
> 
> Operators mark each task as 'Started' and then 'Completed' as they execute the work. Once the final task is completed, the system consumes the components, adds the finished Dining Table to inventory, and updates the Stock Ledger."
>
> *[Action: Log in as `manufacturing`. Go to `/bom/` to view the recipe. Go to `/manufacturing/` to view the Production Orders. Open the active order, confirm stock reservation, then go to `/workorders/` and mark the tasks (Assembly, Painting, Packaging) as completed. Log out.]*

---

### 9. POS Cashier: Retail Sales Terminal
**Speaker:**
> "To cater to walk-in clients, NexusERP includes an integrated **POS (Point of Sale) Terminal**. Let's log in as the **Cashier** using the username `cashier` and password `cashier123`.
> 
> Instead of using a separate, disconnected billing system, the cashier opens the POS terminal directly inside the ERP.
> 
> They select products, add them to the cart, complete the checkout process, and instantly generate a print-friendly receipt. Because this terminal is fully integrated, every POS sale immediately deducts stock, creates inventory ledger entries, and records revenue in the general database."
>
> *[Action: Log in as `cashier`. Go to `/pos/`. Select a product, add it to the cart, click 'Checkout', complete payment, and show the receipt modal. Log out.]*

---

### 10. AI Operations Copilot
**Speaker:**
> "Finally, let's explore our ultimate standout feature—the **AI Operations Copilot**, accessible by any logged-in user.
> 
> Integrating the Google Gemini API directly with our database, the Copilot answers natural language queries from our team. We can ask it:
> * *'What should I manufacture today?'*
> * *'Which components are running low?'*
> * *'Why is this sales order delayed?'*
> 
> Instead of querying tables manually or writing SQL, the AI parses the current snapshot of our inventory, purchase status, and production queue to provide immediate, context-aware business insights. It acts as an intelligent assistant for factory floor execution."
>
> *[Action: Log in as any user (e.g., `owner`). Go to `/copilot/` and send a test question like: "What should I manufacture today?" Show the AI generating a list of production priorities based on real-time shortages.]*

---

### 11. Conclusion
**Speaker:**
> "In summary, NexusERP solves the critical pain points of discrete manufacturing by bridging the gap between Sales, Purchasing, Inventory, POS, and Manufacturing. 
> 
> With automated shortage calculations, delivery risk evaluation, work order tracking, and an AI Operations Copilot, NexusERP replaces chaotic spreadsheets with a single, intelligent source of truth.
> 
> Thank you."

---
