from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError




class SaleRentalLine(models.Model):
    _name = 'sale.rental.line'
    _description = 'Vehicle Rental Line'

    order_id = fields.Many2one('sale.order', ondelete='cascade')

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    pickup_location = fields.Selection([
        ('doha', 'Doha'),
        ('wakra', 'Al Wakra'),
        ('alkhor', 'Al Khor')
    ], string="Pickup Location", required=True)

    rent_price = fields.Float(string="Rent Price", required=True)
    days = fields.Integer(compute="_compute_days", store=True)
    subtotal = fields.Float(compute="_compute_total", store=True)

    @api.depends('start_date','end_date')
    def _compute_days(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.days = (rec.end_date - rec.start_date).days + 1
            else:
                rec.days = 0

    @api.depends('days','rent_price')
    def _compute_total(self):
        for rec in self:
            rec.subtotal = rec.days * rec.rent_price



    @api.constrains('start_date','end_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.end_date < rec.start_date:
                    raise ValidationError("End date must be after start date.")











class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rental_line_ids = fields.One2many(
        'sale.rental.line',
        'order_id',
        string="Vehicle Rental Lines"
    )
    rental_total = fields.Float(
        string="Rental Total",
        compute="_compute_rental_total",
        store=True
    )

    @api.depends('rental_line_ids.subtotal')
    def _compute_rental_total(self):
        for order in self:
            order.rental_total = sum(order.rental_line_ids.mapped('subtotal'))

    def create_rental_order_lines(self):
        """Sync rental lines to sale order lines for proper invoicing"""
        self.ensure_one()
        
        # Remove existing rental-related order lines
        self.order_line.filtered(lambda l: l.rental_line_id).unlink()
        
        # Create order lines from rental lines
        for rental in self.rental_line_ids:
            product = self.env.ref('car_rent.product_vehicle_rental', raise_if_not_found=False)
            if not product:
                # Fallback: try to find any service product
                product = self.env['product.product'].search([('type', '=', 'service')], limit=1)
            
            if product:
                # Format pickup location
                location_dict = dict(rental._fields['pickup_location'].selection)
                pickup_text = location_dict.get(rental.pickup_location, rental.pickup_location)
                
                # Create detailed description
                description = f"🚗 {rental.vehicle_id.name}\n"
                description += f"📍 Pickup: {pickup_text}\n"
                description += f"📅 From: {rental.start_date.strftime('%d/%m/%Y')} To: {rental.end_date.strftime('%d/%m/%Y')}\n"
                description += f"⏱️ Duration: {rental.days} day(s)"
                
                self.env['sale.order.line'].create({
                    'order_id': self.id,
                    'product_id': product.id,
                    'name': description,
                    'product_uom_qty': rental.days,
                    'price_unit': rental.rent_price,
                    'rental_line_id': rental.id,
                })

    def action_confirm(self):
        """Override to sync rental lines before confirmation"""
        for order in self:
            if order.rental_line_ids:
                order.create_rental_order_lines()
        return super(SaleOrder, self).action_confirm()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rental_line_id = fields.Many2one('sale.rental.line', string="Rental Line", readonly=True)
