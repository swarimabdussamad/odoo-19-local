# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

class RentalDashboard(models.TransientModel):
    _name = 'rental.dashboard'
    _description = 'Rental Dashboard'
    
    # Date range for filters
    date_from = fields.Date(
        string='From Date',
        default=lambda self: fields.Date.today()
    )
    date_to = fields.Date(
        string='To Date',
        default=lambda self: fields.Date.today()
    )
    
    # KPI Fields
    total_vehicles = fields.Integer(
        string='Total Vehicles',
        compute='_compute_vehicle_stats'
    )
    available_vehicles = fields.Integer(
        string='Available Vehicles',
        compute='_compute_vehicle_stats'
    )
    rented_vehicles = fields.Integer(
        string='Rented Vehicles',
        compute='_compute_vehicle_stats'
    )
    maintenance_vehicles = fields.Integer(
        string='Under Maintenance',
        compute='_compute_vehicle_stats'
    )
    
    utilization_rate = fields.Float(
        string='Utilization Rate (%)',
        compute='_compute_vehicle_stats'
    )
    
    # Rental Statistics
    active_rentals = fields.Integer(
        string='Active Rentals',
        compute='_compute_rental_stats'
    )
    pickups_today = fields.Integer(
        string='Pickups Today',
        compute='_compute_rental_stats'
    )
    returns_today = fields.Integer(
        string='Returns Today',
        compute='_compute_rental_stats'
    )
    overdue_returns = fields.Integer(
        string='Overdue Returns',
        compute='_compute_rental_stats'
    )
    
    # Revenue Statistics
    revenue_today = fields.Float(
        string='Revenue Today (QAR)',
        compute='_compute_revenue_stats'
    )
    revenue_month = fields.Float(
        string='Revenue This Month (QAR)',
        compute='_compute_revenue_stats'
    )
    revenue_year = fields.Float(
        string='Revenue This Year (QAR)',
        compute='_compute_revenue_stats'
    )
    
    # Customer Statistics
    new_customers_month = fields.Integer(
        string='New Customers This Month',
        compute='_compute_customer_stats'
    )
    total_customers = fields.Integer(
        string='Total Customers',
        compute='_compute_customer_stats'
    )
    
    @api.depends('date_from', 'date_to')
    def _compute_vehicle_stats(self):
        for record in self:
            # Total vehicles
            record.total_vehicles = self.env['fleet.vehicle'].search_count([])
            
            # Available vehicles
            record.available_vehicles = self.env['fleet.vehicle'].search_count([
                ('rental_state', '=', 'available')
            ])
            
            # Rented vehicles
            record.rented_vehicles = self.env['fleet.vehicle'].search_count([
                ('rental_state', '=', 'rented')
            ])
            
            # Maintenance vehicles
            record.maintenance_vehicles = self.env['fleet.vehicle'].search_count([
                ('rental_state', '=', 'maintenance')
            ])
            
            # Utilization rate
            if record.total_vehicles > 0:
                record.utilization_rate = (record.rented_vehicles / record.total_vehicles) * 100
            else:
                record.utilization_rate = 0.0
    
    @api.depends('date_from', 'date_to')
    def _compute_rental_stats(self):
        for record in self:
            today = fields.Date.today()
            now = fields.Datetime.now()
            
            # Active rentals
            record.active_rentals = self.env['rental.contract'].search_count([
                ('state', '=', 'ongoing')
            ])
            
            # Pickups today
            record.pickups_today = self.env['rental.contract'].search_count([
                ('pickup_date', '>=', datetime.combine(today, datetime.min.time())),
                ('pickup_date', '<=', datetime.combine(today, datetime.max.time())),
                ('state', 'in', ['confirmed', 'draft'])
            ])
            
            # Returns today
            record.returns_today = self.env['rental.contract'].search_count([
                ('return_date', '>=', datetime.combine(today, datetime.min.time())),
                ('return_date', '<=', datetime.combine(today, datetime.max.time())),
                ('state', '=', 'ongoing')
            ])
            
            # Overdue returns
            record.overdue_returns = self.env['rental.contract'].search_count([
                ('return_date', '<', now),
                ('state', '=', 'ongoing')
            ])
    
    @api.depends('date_from', 'date_to')
    def _compute_revenue_stats(self):
        for record in self:
            today = fields.Date.today()
            
            # Revenue today
            contracts_today = self.env['rental.contract'].search([
                ('pickup_date', '>=', datetime.combine(today, datetime.min.time())),
                ('pickup_date', '<=', datetime.combine(today, datetime.max.time())),
                ('state', 'in', ['ongoing', 'returned', 'closed'])
            ])
            record.revenue_today = sum(contracts_today.mapped('rental_amount'))
            
            # Revenue this month
            month_start = today.replace(day=1)
            contracts_month = self.env['rental.contract'].search([
                ('pickup_date', '>=', datetime.combine(month_start, datetime.min.time())),
                ('pickup_date', '<=', datetime.combine(today, datetime.max.time())),
                ('state', 'in', ['ongoing', 'returned', 'closed'])
            ])
            record.revenue_month = sum(contracts_month.mapped('rental_amount'))
            
            # Revenue this year
            year_start = today.replace(month=1, day=1)
            contracts_year = self.env['rental.contract'].search([
                ('pickup_date', '>=', datetime.combine(year_start, datetime.min.time())),
                ('pickup_date', '<=', datetime.combine(today, datetime.max.time())),
                ('state', 'in', ['ongoing', 'returned', 'closed'])
            ])
            record.revenue_year = sum(contracts_year.mapped('rental_amount'))
    
    @api.depends('date_from', 'date_to')
    def _compute_customer_stats(self):
        for record in self:
            today = fields.Date.today()
            month_start = today.replace(day=1)
            
            # New customers this month
            record.new_customers_month = self.env['res.partner'].search_count([
                ('create_date', '>=', datetime.combine(month_start, datetime.min.time())),
                ('create_date', '<=', datetime.combine(today, datetime.max.time()))
            ])
            
            # Total customers
            record.total_customers = self.env['res.partner'].search_count([])
    
    # Action methods to open specific views
    def action_view_pickups_today(self):
        today = fields.Date.today()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pickups Today',
            'res_model': 'rental.contract',
            'view_mode': 'list,form',
            'domain': [
                ('pickup_date', '>=', datetime.combine(today, datetime.min.time())),
                ('pickup_date', '<=', datetime.combine(today, datetime.max.time())),
                ('state', 'in', ['confirmed', 'draft'])
            ]
        }
    
    def action_view_returns_today(self):
        today = fields.Date.today()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Returns Today',
            'res_model': 'rental.contract',
            'view_mode': 'list,form',
            'domain': [
                ('return_date', '>=', datetime.combine(today, datetime.min.time())),
                ('return_date', '<=', datetime.combine(today, datetime.max.time())),
                ('state', '=', 'ongoing')
            ]
        }
    
    def action_view_overdue_returns(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Overdue Returns',
            'res_model': 'rental.contract',
            'view_mode': 'list,form',
            'domain': [
                ('return_date', '<', fields.Datetime.now()),
                ('state', '=', 'ongoing')
            ]
        }
    
    def action_view_available_vehicles(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Available Vehicles',
            'res_model': 'fleet.vehicle',
            'view_mode': 'list,form',
            'domain': [('rental_state', '=', 'available')]
        }
    
    def action_view_active_rentals(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Active Rentals',
            'res_model': 'rental.contract',
            'view_mode': 'list,form',
            'domain': [('state', '=', 'ongoing')]
        }