"""
Dummy financial data used for report generation.
NemoClaw passes report_type + params; we pick the matching dataset.
"""

QUARTERLY_REVENUE = {
    "Q1 2025": [
        {"month": "January", "revenue": 142500, "expenses": 98000, "profit": 44500},
        {"month": "February", "revenue": 138000, "expenses": 91000, "profit": 47000},
        {"month": "March", "revenue": 165000, "expenses": 102000, "profit": 63000},
    ],
    "Q2 2025": [
        {"month": "April", "revenue": 172000, "expenses": 108000, "profit": 64000},
        {"month": "May", "revenue": 185000, "expenses": 115000, "profit": 70000},
        {"month": "June", "revenue": 191000, "expenses": 120000, "profit": 71000},
    ],
    "Q3 2025": [
        {"month": "July", "revenue": 198000, "expenses": 122000, "profit": 76000},
        {"month": "August", "revenue": 205000, "expenses": 130000, "profit": 75000},
        {"month": "September", "revenue": 210000, "expenses": 135000, "profit": 75000},
    ],
    "Q4 2025": [
        {"month": "October", "revenue": 220000, "expenses": 140000, "profit": 80000},
        {"month": "November", "revenue": 245000, "expenses": 155000, "profit": 90000},
        {"month": "December", "revenue": 270000, "expenses": 170000, "profit": 100000},
    ],
}

DEPARTMENTS = {
    "Sales": {"budget": 500000, "spent": 423000, "headcount": 12},
    "Engineering": {"budget": 800000, "spent": 760000, "headcount": 20},
    "Marketing": {"budget": 300000, "spent": 275000, "headcount": 8},
    "Operations": {"budget": 200000, "spent": 188000, "headcount": 6},
    "HR": {"budget": 150000, "spent": 132000, "headcount": 4},
}

INVOICES = [
    {"id": "INV-001", "client": "Acme Corp", "amount": 25000, "status": "Paid", "date": "2025-01-15"},
    {"id": "INV-002", "client": "TechVentures", "amount": 42000, "status": "Paid", "date": "2025-01-28"},
    {"id": "INV-003", "client": "GlobalTrade", "amount": 18500, "status": "Pending", "date": "2025-02-05"},
    {"id": "INV-004", "client": "NexaCorp", "amount": 33000, "status": "Paid", "date": "2025-02-20"},
    {"id": "INV-005", "client": "AlphaMedia", "amount": 12000, "status": "Overdue", "date": "2025-03-01"},
    {"id": "INV-006", "client": "BetaLogistics", "amount": 55000, "status": "Paid", "date": "2025-03-18"},
]

SUMMARY_STATS = {
    "total_revenue": 2_341_500,
    "total_expenses": 1_521_000,
    "net_profit": 820_500,
    "profit_margin": 35.04,
    "yoy_growth": 18.7,
    "active_clients": 47,
    "new_clients": 12,
}

SUPPORT_TICKETS = {
    "stats": {
        "total": 348,
        "open": 42,
        "in_progress": 31,
        "resolved": 251,
        "closed": 24,
        "avg_resolution_hours": 6.4,
        "sla_breach_rate": 4.2,
        "csat_score": 4.3,
    },
    "by_priority": [
        {"priority": "Critical", "count": 18,  "resolved": 15, "avg_hours": 2.1},
        {"priority": "High",     "count": 67,  "resolved": 58, "avg_hours": 4.8},
        {"priority": "Medium",   "count": 153, "resolved": 112, "avg_hours": 7.2},
        {"priority": "Low",      "count": 110, "resolved": 66, "avg_hours": 11.5},
    ],
    "by_category": [
        {"category": "Billing",          "count": 82,  "resolved": 76},
        {"category": "Technical Issue",  "count": 115, "resolved": 89},
        {"category": "Account Access",   "count": 63,  "resolved": 55},
        {"category": "Feature Request",  "count": 48,  "resolved": 12},
        {"category": "General Inquiry",  "count": 40,  "resolved": 19},
    ],
    "recent": [
        {"id": "TKT-1041", "subject": "Login failure after password reset",    "priority": "High",     "status": "Resolved", "agent": "Alice M.", "hours": 3.2},
        {"id": "TKT-1040", "subject": "Invoice amount mismatch",               "priority": "Critical", "status": "Resolved", "agent": "Bob K.",   "hours": 1.8},
        {"id": "TKT-1039", "subject": "API rate limit exceeded",               "priority": "High",     "status": "In Progress", "agent": "Carol T.", "hours": 5.1},
        {"id": "TKT-1038", "subject": "Dashboard not loading on Safari",       "priority": "Medium",   "status": "Open",     "agent": "—",        "hours": 0},
        {"id": "TKT-1037", "subject": "Request for bulk export feature",       "priority": "Low",      "status": "Open",     "agent": "—",        "hours": 0},
        {"id": "TKT-1036", "subject": "Wrong tax applied on renewal",          "priority": "High",     "status": "Resolved", "agent": "Alice M.", "hours": 4.5},
        {"id": "TKT-1035", "subject": "2FA setup not working on mobile",       "priority": "Medium",   "status": "Resolved", "agent": "Bob K.",   "hours": 6.0},
        {"id": "TKT-1034", "subject": "Data export CSV encoding issue",        "priority": "Medium",   "status": "Closed",   "agent": "Carol T.", "hours": 8.3},
    ],
}

# Flowchart node/edge definitions for diagrams
PROCESS_FLOWS = {
    "order_processing": {
        "nodes": ["Customer Order", "Validate Payment", "Check Inventory", "Pick & Pack", "Ship Order", "Delivered"],
        "edges": [
            ("Customer Order", "Validate Payment"),
            ("Validate Payment", "Check Inventory"),
            ("Check Inventory", "Pick & Pack"),
            ("Pick & Pack", "Ship Order"),
            ("Ship Order", "Delivered"),
        ],
        "conditionals": {
            "Validate Payment": {"fail": "Payment Failed"},
            "Check Inventory": {"fail": "Backorder"},
        },
    },
    "onboarding": {
        "nodes": ["Sign Up", "Verify Email", "Profile Setup", "KYC Check", "Approved", "Active Account"],
        "edges": [
            ("Sign Up", "Verify Email"),
            ("Verify Email", "Profile Setup"),
            ("Profile Setup", "KYC Check"),
            ("KYC Check", "Approved"),
            ("Approved", "Active Account"),
        ],
        "conditionals": {
            "KYC Check": {"fail": "Manual Review"},
        },
    },
    "support_ticket": {
        "nodes": ["Ticket Created", "Auto-Triage", "Assign Agent", "In Progress", "Resolved", "Closed"],
        "edges": [
            ("Ticket Created", "Auto-Triage"),
            ("Auto-Triage", "Assign Agent"),
            ("Assign Agent", "In Progress"),
            ("In Progress", "Resolved"),
            ("Resolved", "Closed"),
        ],
        "conditionals": {
            "In Progress": {"escalate": "Escalated"},
        },
    },
}
