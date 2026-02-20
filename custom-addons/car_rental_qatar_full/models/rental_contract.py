# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import ValidationError


class RentalContract(models.Model):
    _name = "rental.contract"
    _description = "Car Rental Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    # Basic Information
    name = fields.Char(
        string="Contract Number",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )

    # Customer Information
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True
    )
    customer_phone = fields.Char(
        related="customer_id.phone", string="Phone", readonly=True
    )
    customer_email = fields.Char(
        related="customer_id.email", string="Email", readonly=True
    )

    # Vehicle Information
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, tracking=True
    )
    vehicle_plate = fields.Char(
        related="vehicle_id.license_plate", string="License Plate", readonly=True
    )

    # Rental Period
    pickup_date = fields.Datetime(
        string="Pickup Date", required=True, default=fields.Datetime.now, tracking=True
    )
    return_date = fields.Datetime(string="Return Date", required=True, tracking=True)
    actual_return_date = fields.Datetime(string="Actual Return Date", readonly=True)

    # Locations
    pickup_location = fields.Selection(
        [
            ("doha_airport", "Hamad International Airport"),
            ("city_center", "City Center"),
            ("al_wakrah", "Al Wakrah"),
            ("al_khor", "Al Khor"),
            ("other", "Other Location"),
        ],
        string="Pickup Location",
        default="doha_airport",
        required=True,
    )

    return_location = fields.Selection(
        [
            ("doha_airport", "Hamad International Airport"),
            ("city_center", "City Center"),
            ("al_wakrah", "Al Wakrah"),
            ("al_khor", "Al Khor"),
            ("other", "Other Location"),
        ],
        string="Return Location",
        default="doha_airport",
        required=True,
    )

    # Pricing
    daily_rate = fields.Float(string="Daily Rate (QAR)", required=True, default=100.0)
    total_days = fields.Integer(
        string="Total Days", compute="_compute_total_days", store=True
    )
    rental_amount = fields.Float(
        string="Rental Amount (QAR)", compute="_compute_rental_amount", store=True
    )

    # Mileage
    odometer_start = fields.Integer(string="Odometer Start (km)")
    odometer_end = fields.Integer(string="Odometer End (km)")
    total_km = fields.Integer(
        string="Total KM", compute="_compute_total_km", store=True
    )

    # Deposits & Payments
    security_deposit = fields.Float(string="Security Deposit (QAR)", default=1000.0)
    deposit_paid = fields.Boolean(string="Deposit Paid", default=False)

    # State
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("ongoing", "Ongoing"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    # Notes
    notes = fields.Text(string="Notes")

    # Computed Methods
    @api.depends("pickup_date", "return_date")
    def _compute_total_days(self):
        for record in self:
            if record.pickup_date and record.return_date:
                delta = record.return_date - record.pickup_date
                record.total_days = max(1, delta.days)
            else:
                record.total_days = 0

    @api.depends("daily_rate", "total_days")
    def _compute_rental_amount(self):
        for record in self:
            record.rental_amount = record.daily_rate * record.total_days

    @api.depends("odometer_start", "odometer_end")
    def _compute_total_km(self):
        for record in self:
            if record.odometer_end and record.odometer_start:
                record.total_km = record.odometer_end - record.odometer_start
            else:
                record.total_km = 0

    # Constraints
    @api.constrains("pickup_date", "return_date")
    def _check_dates(self):
        for record in self:
            if record.pickup_date and record.return_date:
                if record.return_date <= record.pickup_date:
                    raise ValidationError("Return date must be after pickup date!")

    @api.constrains("vehicle_id", "pickup_date", "return_date", "state")
    def _check_vehicle_no_double_booking(self):
        """Prevent the same vehicle from being rented in overlapping periods."""
        for record in self:
            if (
                not record.vehicle_id
                or not record.pickup_date
                or not record.return_date
            ):
                continue
            # Only check when contract is or will be active (draft can be confirmed later)
            if record.state == "cancelled":
                continue
            # Find other contracts for same vehicle that are not cancelled/completed
            # and overlap with this period: overlap <=> pickup < other.return AND return > other.pickup
            overlapping = self.search(
                [
                    ("vehicle_id", "=", record.vehicle_id.id),
                    ("id", "!=", record.id),
                    ("state", "not in", ("cancelled", "completed")),
                    ("pickup_date", "<", record.return_date),
                    ("return_date", ">", record.pickup_date),
                ],
                limit=1,
            )
            if overlapping:
                other = overlapping[0]
                raise ValidationError(
                    _(
                        "This vehicle (%s) is already rented in this period. "
                        "Conflict with contract %s (Pickup: %s, Return: %s). "
                        "Please choose another vehicle or different dates."
                    )
                    % (
                        record.vehicle_id.license_plate or record.vehicle_id.name,
                        other.name,
                        other.pickup_date,
                        other.return_date,
                    )
                )

    @api.constrains("odometer_start", "odometer_end")
    def _check_odometer(self):
        for record in self:
            if record.odometer_end and record.odometer_start:
                if record.odometer_end < record.odometer_start:
                    raise ValidationError(
                        "End odometer reading cannot be less than start reading!"
                    )

    # CRUD Methods
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("rental.contract") or "New"
                )
        return super(RentalContract, self).create(vals_list)

    # Action Methods
    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_start_rental(self):
        self.write({"state": "ongoing"})

    def action_complete_rental(self):
        self.write({"state": "completed", "actual_return_date": fields.Datetime.now()})

    def action_cancel(self):
        self.write({"state": "cancelled"})
