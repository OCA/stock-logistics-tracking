# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Logistics Units',
    'version': '10.0.1.0.0',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'summary': 'Restore Logisitics Units object',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_ul.xml',
        'views/stock_quant_package.xml',
    ],
    'demo': ['demo/product_ul.xml'],
    'url': 'https://github.com/OCA/stock-logistics-tracking',
    'installable': True,
}
