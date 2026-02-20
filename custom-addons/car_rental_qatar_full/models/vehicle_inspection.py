# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class VehicleInspection(models.Model):
    _name = 'vehicle.inspection'
    _description = 'Vehicle Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'inspection_date desc'
    
    name = fields.Char(
        string='Inspection Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    
    # Relations
    rental_contract_id = fields.Many2one(
        'rental.contract',
        string='Rental Contract',
        required=True,
        ondelete='cascade'
    )
    
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        related='rental_contract_id.vehicle_id',
        store=True,
        readonly=True
    )
    
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='rental_contract_id.customer_id',
        store=True,
        readonly=True
    )
    
    # Inspection Details
    inspection_type = fields.Selection([
        ('pickup', 'Pickup Inspection'),
        ('return', 'Return Inspection')
    ], string='Inspection Type', required=True, default='pickup')
    
    inspection_date = fields.Datetime(
        string='Inspection Date',
        required=True,
        default=fields.Datetime.now
    )
    
    inspector_id = fields.Many2one(
        'res.users',
        string='Inspector',
        default=lambda self: self.env.user,
        required=True
    )
    
    # Vehicle Condition
    odometer_reading = fields.Integer(
        string='Odometer Reading (km)',
        required=True
    )
    
    fuel_level = fields.Selection([
        ('empty', 'Empty'),
        ('quarter', '1/4 Tank'),
        ('half', '1/2 Tank'),
        ('three_quarter', '3/4 Tank'),
        ('full', 'Full Tank')
    ], string='Fuel Level', required=True, default='full')
    
    # Exterior Condition
    exterior_condition = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string='Exterior Condition', default='good', required=True)
    
    exterior_notes = fields.Text(string='Exterior Notes')
    
    # Interior Condition
    interior_condition = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string='Interior Condition', default='good', required=True)
    
    interior_notes = fields.Text(string='Interior Notes')
    
    # Checklist Items
    spare_tire = fields.Boolean(string='Spare Tire', default=True)
    jack_tools = fields.Boolean(string='Jack & Tools', default=True)
    documents_present = fields.Boolean(string='Documents Present', default=True)
    first_aid_kit = fields.Boolean(string='First Aid Kit', default=True)
    fire_extinguisher = fields.Boolean(string='Fire Extinguisher', default=True)
    warning_triangle = fields.Boolean(string='Warning Triangle', default=True)
    
    # Functional Checks
    lights_working = fields.Boolean(string='All Lights Working', default=True)
    ac_working = fields.Boolean(string='AC Working', default=True)
    wipers_working = fields.Boolean(string='Wipers Working', default=True)
    horn_working = fields.Boolean(string='Horn Working', default=True)
    
    # Photos
    photo_front = fields.Binary(string='Front Photo', attachment=True)
    photo_back = fields.Binary(string='Back Photo', attachment=True)
    photo_left = fields.Binary(string='Left Side Photo', attachment=True)
    photo_right = fields.Binary(string='Right Side Photo', attachment=True)
    photo_interior = fields.Binary(string='Interior Photo', attachment=True)
    photo_odometer = fields.Binary(string='Odometer Photo', attachment=True)
    
    # Damage Documentation
    damage_ids = fields.One2many(
        'vehicle.damage',
        'inspection_id',
        string='Damages Found'
    )
    
    damage_count = fields.Integer(
        string='Number of Damages',
        compute='_compute_damage_count'
    )
    
    # Signatures
    customer_signature = fields.Binary(string='Customer Signature', attachment=True)
    inspector_signature = fields.Binary(string='Inspector Signature', attachment=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text(string='Additional Notes')
    
    @api.depends('damage_ids')
    def _compute_damage_count(self):
        for record in self:
            record.damage_count = len(record.damage_ids)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            inspection_type = vals.get('inspection_type', 'pickup')
            prefix = 'INS-P-' if inspection_type == 'pickup' else 'INS-R-'
            vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.inspection') or 'New'
        return super(VehicleInspection, self).create(vals)
    
    def action_complete(self):
        self.state = 'completed'
        # Update odometer in rental contract
        if self.inspection_type == 'pickup':
            self.rental_contract_id.odometer_start = self.odometer_reading
        else:
            self.rental_contract_id.odometer_end = self.odometer_reading


class VehicleDamage(models.Model):
    _name = 'vehicle.damage'
    _description = 'Vehicle Damage'
    _order = 'create_date desc'
    
    inspection_id = fields.Many2one(
        'vehicle.inspection',
        string='Inspection',
        required=True,
        ondelete='cascade'
    )
    
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        related='inspection_id.vehicle_id',
        string='Vehicle',
        store=True,
        readonly=True
    )
    
    damage_location = fields.Selection([
        ('front_bumper', 'Front Bumper'),
        ('rear_bumper', 'Rear Bumper'),
        ('left_door', 'Left Door'),
        ('right_door', 'Right Door'),
        ('hood', 'Hood'),
        ('roof', 'Roof'),
        ('left_fender', 'Left Fender'),
        ('right_fender', 'Right Fender'),
        ('windshield', 'Windshield'),
        ('left_mirror', 'Left Mirror'),
        ('right_mirror', 'Right Mirror'),
        ('interior', 'Interior'),
        ('other', 'Other')
    ], string='Damage Location', required=True)
    
    damage_type = fields.Selection([
        ('scratch', 'Scratch'),
        ('dent', 'Dent'),
        ('crack', 'Crack'),
        ('broken', 'Broken'),
        ('missing', 'Missing'),
        ('stain', 'Stain'),
        ('other', 'Other')
    ], string='Damage Type', required=True)
    
    severity = fields.Selection([
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major')
    ], string='Severity', default='minor', required=True)
    
    description = fields.Text(string='Description', required=True)
    
    damage_photo = fields.Binary(string='Damage Photo', attachment=True)
    
    estimated_cost = fields.Float(string='Estimated Repair Cost (QAR)')
    
    notes = fields.Text(string='Notes')