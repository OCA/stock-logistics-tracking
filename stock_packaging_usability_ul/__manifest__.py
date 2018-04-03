# -*- coding: utf-8 -*-
# Copyright 2014-2018 Akretion (http://www.akretion.com).
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Packaging Usability UL',
    'version': '10.0.1.0.0',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'summary': "Faster packaging process with logistics units",
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': [
        'stock_packaging_usability',
        'stock_product_ul',
        ],
    'data': [
        'wizard/stock_select_ul.xml',
        'views/stock_picking.xml',
        ],
    'installable': True,
}
