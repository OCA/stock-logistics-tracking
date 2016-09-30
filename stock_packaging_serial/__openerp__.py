# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE S.A.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Packaging Serial',
    'summary': """
        Allows to generate serial numbers on packages through
        logistical units""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE S.A.,Odoo Community Association (OCA)',
    'website': 'http://acsone.eu',
    'depends': ['stock', 'base_gs1_barcode'],
    'data': [
        'security/stock_packaging_serial.xml',
        'views/stock_packaging_serial.xml',
    ],
    'demo': [
    ],
    'test':[],
    'installable': True
}
