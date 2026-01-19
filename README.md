# Repair Management Platform (ERPNext v16)

A comprehensive, modular, multi-industry repair management application built on top of Frappe/ERPNext v15/v16. Designed for GSM workshops, computer repairs, bike shops, and more.

## 🚀 Key Features

### Core Operations
- **Multi-Industry Support**: Industry-agnostic core with specific templates for different repair industries
- **Dynamic Diagnostic Checklists**: Auto-generated quality checks for technicians based on industry
- **Stock Integration**: Automatic Material Issue for spare parts upon repair completion
- **Customer Portal**: Live repair tracking via IMEI or Serial Number
- **Loyalty & Billing**: Customer credit wallets and Gift Card management

### Advanced Analytics & Reporting (NEW)
- **Dashboard Charts**: 5 comprehensive charts tracking repairs by status, revenue by industry, monthly trends, technician performance, and priority distribution
- **KPI Cards**: Real-time metrics including active repairs, monthly revenue, pending diagnostics, completed repairs, and average turnaround time
- **Repair Analytics Report**: Comprehensive filterable report with customer, device, financial, and timeline data
- **Financial Summary Report**: Revenue analysis, parts costs, labor breakdown, and profitability margins by industry
- **Technician Performance Report**: Track completion rates, average turnaround time, revenue per technician, and workload

### Quality & Customer Experience
- **Customer Feedback System**: Multi-dimensional rating system (overall, service quality, technician, turnaround, price, communication)
- **Email Notifications**: Automated customer notifications for all status changes with detailed information
- **Warranty Tracking**: Built-in warranty expiry date tracking for completed repairs
- **SLA Management**: Service Level Agreement tracking with automatic status updates (Within SLA, At Risk, Breached)

### Financial Management
- **Total Amount Calculation**: Automatic calculation from tasks and spare parts
- **Payment Tracking**: Track paid amounts and outstanding balances
- **Turnaround Time Tracking**: Automatic calculation of repair completion time in days
- **Custom Print Formats**: Professional repair order invoices with complete details

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

### Prerequisites
- ERPNext v15 or v16
- Frappe Framework installed
- Bench CLI tool

### Installation Steps

```bash
# Get the app from repository
bench get-app repair_management_platform https://github.com/khechine/repair_management_platform.git

# Install on your site
bench --site [your-site] install-app repair_management_platform

# Run migrations
bench --site [your-site] migrate

# Restart bench
bench restart
```

## 🚀 Deployment to Production Server

### Method 1: Using Existing Frappe Bench (Recommended)

If you already have a Frappe/ERPNext server configured:

```bash
# SSH into your production server
ssh user@your-server-ip

# Navigate to your bench directory
cd ~/frappe-bench

# Get the app
bench get-app repair_management_platform https://github.com/khechine/repair_management_platform.git

# Install on your production site
bench --site your-site.com install-app repair_management_platform

# Run migrations
bench --site your-site.com migrate

# Clear cache and rebuild assets
bench --site your-site.com clear-cache
bench build --app repair_management_platform

# Restart services
sudo supervisorctl restart all
# OR if using systemd
sudo systemctl restart frappe-bench-frappe-web.service
sudo systemctl restart frappe-bench-frappe-worker-default.service
sudo systemctl restart frappe-bench-frappe-worker-short.service
sudo systemctl restart frappe-bench-frappe-worker-long.service
```

### Method 2: Fresh Production Setup

For a new server deployment:

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Frappe/ERPNext using the easy install script
sudo python3 <(curl -s https://raw.githubusercontent.com/frappe/bench/develop/install.py) --production

# Create a new site
cd ~/frappe-bench
bench new-site your-site.com

# Install ERPNext
bench --site your-site.com install-app erpnext

# Install Repair Management Platform
bench get-app repair_management_platform https://github.com/khechine/repair_management_platform.git
bench --site your-site.com install-app repair_management_platform
bench --site your-site.com migrate

# Setup production
sudo bench setup production [your-user]

# Enable site
bench --site your-site.com enable-scheduler

# Setup SSL (optional but recommended)
sudo bench setup lets-encrypt your-site.com
```

### Post-Deployment Configuration

1. **Create Admin User Accounts**
   - Access your site at https://your-site.com
   - Login with Administrator account
   - Create user accounts with appropriate roles

2. **Configure Repair Management Settings**
   - Go to Repair Management workspace
   - Open "Repair Management Settings"
   - Set default warehouse, service items, and terms

3. **Setup Industry Types & SLA Templates**
   - Industry Types are pre-loaded via fixtures
   - Configure Repair SLA templates for each industry and priority combination
   - Set up diagnostic checklist templates

4. **Configure Email Settings**
   - Go to Email Domain and Email Account
   - Configure SMTP settings for automated notifications
   - Test email notifications

5. **Setup Print Format**
   - The custom print format "Repair Order Print" is available by default
   - Customize letterhead and company details

### Production Optimization

```bash
# Enable production mode
bench --site your-site.com set-config --global developer_mode 0

# Optimize performance
bench --site your-site.com set-config --global limits "{'jobs': 100, 'emails': 100}"

# Setup backup
bench --site your-site.com backup --with-files
crontab -e
# Add: 0 2 * * * cd ~/frappe-bench && bench --site your-site.com backup --with-files
```

### Monitoring & Maintenance

```bash
# Check logs
tail -f ~/frappe-bench/logs/web.error.log
tail -f ~/frappe-bench/logs/worker.error.log

# Monitor services
sudo supervisorctl status all

# Update app
cd ~/frappe-bench
bench get-app repair_management_platform
bench --site your-site.com migrate
bench build --app repair_management_platform
sudo supervisorctl restart all
```

## 📄 License
MIT
