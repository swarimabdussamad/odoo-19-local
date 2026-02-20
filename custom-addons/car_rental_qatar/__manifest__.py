# -*- coding: utf-8 -*-
{
    "name": "Fleet Vehicle Qatar Extensions",
    "version": "19.0.1.0.0",
    "category": "Fleet",
    "summary": "Qatar-specific fleet vehicle extensions for car rental",
    "description": """
        Car Rental Qatar - Fleet Extensions
        ====================================
        * Adds rental-specific fields to fleet vehicles
        * Vehicle rental categories with pricing
        * Qatar-specific fields (Mulkiya, Insurance)
        * Maintenance tracking
        * Rental status management
    """,
    "author": "Your Company",
    "website": "https://www.yourcompany.com",
    "depends": [
        "base",
        "fleet",
        "car_rent",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/demo_data.xml",
        "views/fleet_vehicle_view.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
