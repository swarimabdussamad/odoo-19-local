# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class CustomerDocument(models.Model):
    _name = 'customer.document'
    _description = 'Customer Document'
    _order = 'create_date desc'
    
    name = fields.Char(
        string='Document Number',
        required=True
    )
    
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        ondelete='cascade'
    )
    
    document_type = fields.Selection([
        ('qatar_id', 'Qatar ID'),
        ('passport', 'Passport'),
        ('gcc_id', 'GCC ID'),
        ('driving_license', 'Driving License'),
        ('idp', 'International Driving Permit')
    ], string='Document Type', required=True)
    
    issue_date = fields.Date(
        string='Issue Date'
    )
    
    expiry_date = fields.Date(
        string='Expiry Date',
        required=True
    )
    
    issuing_country = fields.Many2one(
        'res.country',
        string='Issuing Country'
    )
    
    document_file = fields.Binary(
        string='Document Copy',
        help='Scanned copy of the document'
    )
    
    document_filename = fields.Char(
        string='Filename'
    )
    
    is_expired = fields.Boolean(
        string='Expired',
        compute='_compute_is_expired',
        store=True
    )
    
    days_to_expiry = fields.Integer(
        string='Days to Expiry',
        compute='_compute_days_to_expiry',
        store=True
    )
    
    verified = fields.Boolean(
        string='Verified',
        default=False,
        help='Document has been verified by staff'
    )
    
    verified_by = fields.Many2one(
        'res.users',
        string='Verified By',
        readonly=True
    )
    
    verified_date = fields.Datetime(
        string='Verified Date',
        readonly=True
    )
    
    notes = fields.Text(
        string='Notes'
    )
    
    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = date.today()
        for record in self:
            if record.expiry_date:
                record.is_expired = record.expiry_date < today
            else:
                record.is_expired = False
    
    @api.depends('expiry_date')
    def _compute_days_to_expiry(self):
        today = date.today()
        for record in self:
            if record.expiry_date:
                delta = record.expiry_date - today
                record.days_to_expiry = delta.days
            else:
                record.days_to_expiry = 0
    
    @api.constrains('expiry_date')
    def _check_expiry_date(self):
        for record in self:
            if record.expiry_date and record.expiry_date < date.today():
                raise ValidationError('Cannot create document with past expiry date!')
    
    def action_verify(self):
        self.write({
            'verified': True,
            'verified_by': self.env.user.id,
            'verified_date': fields.Datetime.now()
        })
    
    def action_unverify(self):
        self.write({
            'verified': False,
            'verified_by': False,
            'verified_date': False
        })


# Extend res.partner to add documents
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    document_ids = fields.One2many(
        'customer.document',
        'customer_id',
        string='Documents'
    )
    
    document_count = fields.Integer(
        string='Document Count',
        compute='_compute_document_count'
    )
    
    # Qatar-specific fields
    qatar_id_number = fields.Char(
        string='Qatar ID Number'
    )
    
    passport_number = fields.Char(
        string='Passport Number'
    )
    
    driving_license_number = fields.Char(
        string='Driving License Number'
    )
    
    license_expiry_date = fields.Date(
        string='License Expiry Date'
    )
    
    nationality_id = fields.Many2one(
        'res.country',
        string='Nationality'
    )
    
    date_of_birth = fields.Date(
        string='Date of Birth'
    )
    
    age = fields.Integer(
        string='Age',
        compute='_compute_age'
    )
    
    customer_type = fields.Selection([
        ('individual', 'Individual'),
        ('corporate', 'Corporate')
    ], string='Customer Type', default='individual')
    
    @api.depends('document_ids')
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)
    
    @api.depends('date_of_birth')
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.date_of_birth:
                record.age = today.year - record.date_of_birth.year - (
                    (today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day)
                )
            else:
                record.age = 0
    
    def action_view_documents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Documents',
            'res_model': 'customer.document',
            'view_mode': 'list,form',
            'domain': [('customer_id', '=', self.id)],
            'context': {'default_customer_id': self.id}
        }