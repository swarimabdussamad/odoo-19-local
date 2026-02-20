# -*- coding: utf-8 -*-
{
    "name": "Car Rental Qatar - Full System",
    "version": "19.0.1.0.0",
    "category": "Sales/Rental",
    "summary": "Complete Car Rental Management System for Qatar",
    "description": """
        Car Rental Management System
        =============================
        * Vehicle rental management
        * Customer contracts
        * Vehicle inspection
        * Damage tracking
        * Security deposits
        * Integration with Fleet module
    """,
    "author": "Your Company",
    "website": "https://www.yourcompany.com",
    "depends": [
        "base",
        "mail",
        "fleet",
        "sale_management",
        "account",
        "stock",
    ],
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Data
        "data/sequence.xml",
        "data/vehicle_categories.xml",
        # Views
        "views/rental_contract_views.xml",
        "views/fleet_vehicle_view.xml",
        "views/vehicle_inspection_views.xml",
        "views/customer_document_views.xml",
        # Reports
        "reports/fleet_utilization_report.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
