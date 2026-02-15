from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    rental_line_ids = fields.Many2many(
        'sale.rental.line',
        compute='_compute_rental_line_ids',
        string='Rental Lines'
    )

    @api.depends('invoice_origin')
    def _compute_rental_line_ids(self):
        for move in self:
            rental_lines = self.env['sale.rental.line']
            if move.invoice_origin:
                sale_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
                if sale_order:
                    rental_lines = sale_order.rental_line_ids
            move.rental_line_ids = rental_lines
