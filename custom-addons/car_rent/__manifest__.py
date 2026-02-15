# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'CAR RENT',
    'version': '1.5',
    'summary': 'CAR FOR RENT',
    'sequence': 10,

    'depends': ['base_setup','fleet','sale','account','portal'],
    'data': [
        'data/product_data.xml',
        'security/ir.model.access.csv',
        'views/sale_order_line.xml',
        'views/vehicle_rent.xml',
        'views/account_move_views.xml',
        'views/portal_templates.xml',
        'report/sale_report_templates.xml',
    ],

    'installable': True,
    'application': True,


    'author': 'labeeb',
    'license': 'LGPL-3',
}
