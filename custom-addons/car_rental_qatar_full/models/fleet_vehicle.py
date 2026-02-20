# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    # Rental-specific fields
    rental_state = fields.Selection(
        [
            ("available", "Available"),
            ("rented", "Rented"),
            ("maintenance", "Under Maintenance"),
            ("unavailable", "Unavailable"),
        ],
        string="Rental Status",
        default="available",
        tracking=True,
    )

    rental_category_id = fields.Many2one(
        "fleet.vehicle.category",
        string="Rental Category",
        help="Category for rental pricing (Economy, SUV, Luxury, etc.)",
    )

    rental_daily_rate = fields.Float(
        string="Daily Rate (QAR)",
        related="rental_category_id.daily_rate",
        store=True,
        readonly=True,
    )

    # Qatar-specific fields
    mulkiya_expiry = fields.Date(
        string="Mulkiya Expiry Date", help="Qatar vehicle registration expiry date"
    )

    insurance_expiry = fields.Date(string="Insurance Expiry Date")

    last_service_date = fields.Date(string="Last Service Date")

    next_service_date = fields.Date(
        string="Next Service Due", compute="_compute_next_service", store=True
    )

    # Mileage tracking
    current_odometer = fields.Float(
        string="Current Odometer (km)", related="odometer", readonly=True
    )

    # Compute next service date (every 10,000 km or 6 months)
    @api.depends("last_service_date")
    def _compute_next_service(self):
        from datetime import timedelta

        for record in self:
            if record.last_service_date:
                record.next_service_date = record.last_service_date + timedelta(
                    days=180
                )
            else:
                record.next_service_date = False

    # Count active rentals
    rental_count = fields.Integer(
        string="Rental Count", compute="_compute_rental_count"
    )

    def _compute_rental_count(self):
        for record in self:
            record.rental_count = self.env["rental.contract"].search_count(
                [("vehicle_id", "=", record.id)]
            )

    # Smart button action
    def action_view_rentals(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Vehicle Rentals",
            "res_model": "rental.contract",
            "view_mode": "list,form",
            "domain": [("vehicle_id", "=", self.id)],
            "context": {"default_vehicle_id": self.id},
        }


class FleetVehicleCategory(models.Model):
    _name = "fleet.vehicle.category"
    _description = "Vehicle Rental Category"
    _order = "sequence, name"

    name = fields.Char(string="Category Name", required=True, translate=True)

    sequence = fields.Integer(string="Sequence", default=10)

    daily_rate = fields.Float(string="Daily Rate (QAR)", required=True, default=100.0)

    weekly_rate = fields.Float(
        string="Weekly Rate (QAR)", compute="_compute_weekly_rate", store=True
    )

    monthly_rate = fields.Float(
        string="Monthly Rate (QAR)", compute="_compute_monthly_rate", store=True
    )

    description = fields.Text(string="Description")

    vehicle_count = fields.Integer(
        string="Number of Vehicles", compute="_compute_vehicle_count"
    )

    active = fields.Boolean(string="Active", default=True)

    @api.depends("daily_rate")
    def _compute_weekly_rate(self):
        for record in self:
            # 7 days with 15% discount
            record.weekly_rate = record.daily_rate * 7 * 0.85

    @api.depends("daily_rate")
    def _compute_monthly_rate(self):
        for record in self:
            # 30 days with 40% discount
            record.monthly_rate = record.daily_rate * 30 * 0.60

    def _compute_vehicle_count(self):
        for record in self:
            record.vehicle_count = self.env["fleet.vehicle"].search_count(
                [("rental_category_id", "=", record.id)]
            )
