# Repair Management Platform (ERPNext v16)

A modular, multi-industry repair management application built on top of Frappe/ERPNext v15/v16. Designed for GSM workshops, computer repairs, bike shops, and more.

## 🚀 Key Features
- **Multi-Industry Support**: Industry-agnostic core with specific templates.
- **Dynamic Diagnostic Checklists**: Auto-generated quality checks for technicians.
- **Stock Integration**: Automatic Material Issue for spare parts upon repair completion.
- **Customer Portal**: Live repair tracking via IMEI or Serial Number.
- **Loyalty & Billing**: Customer credit wallets and Gift Card management.

---

## 🛠 Business Process (How to use)

The platform follows a standardized repair lifecycle designed for efficiency and quality control.

### 1. Reception & Device Registration
- **Step**: Create a **Repair Device**.
- **Process**: Scan the IMEI or Serial Number. Assign it to a **Customer** and select the **Industry** (e.g., Cell Phone & Wireless Repair).
- **Goal**: Establish a unique identity for the asset in the system.

### 2. Opening a Repair Order
- **Step**: Create a **Repair Order**.
- **Process**: Link the registered device. Set the initial status to `Diagnostic Pending`.
- **Result**: A unique tracking ID is generated for the customer.

### 3. Technical Diagnostic
- **Step**: Create a **Diagnostic Report**.
- **Automation**: Upon creation, the system looks at the industry/device type and **auto-generates a Diagnostic Checklist** from a template (e.g., "Smartphone Standard Diagnostic").
- **Constraint**: Technicians must complete the checklist. Mandatory items (like "Power On") must be marked as **OK** to proceed.

### 4. Quotation & Approval
- **Step**: Generate a Quotation (standard ERPNext) or update the Repair Order.
- **Validation**: The system will **block** moving the status to `Quoted` or `Repair in Progress` if mandatory diagnostic checks failed.

### 5. Repair & Spare Parts
- **Step**: Add **Spare Parts** to the Repair Order table.
- **Process**: Select the part (Item), the warehouse, and the quantity used.
- **Goal**: Track the cost of materials used for the repair.

### 6. Completion & Stock Issue
- **Step**: Set status to `Completed` and **Submit** the Repair Order.
- **Automation**: The platform automatically creates a **Stock Entry (Material Issue)** for all spare parts listed, reducing your stock levels correctly and linking the transaction to the repair.

### 7. Customer Live Tracking
- **Step**: Public Tracking.
- **Process**: The customer visits `/track` on your website.
- **Lookup**: They enter their Order ID or IMEI to see the real-time status (e.g., "Ready for Collection", "Repair in Progress").

---

## 📦 Installation

```bash
bench get-app repair_management_platform https://github.com/khechine/repair_management_platform.git
bench --site [your-site] install-app repair_management_platform
bench --site [your-site] migrate
```

## 📄 License
MIT
