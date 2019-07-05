# Copyright 2014-2019 Akretion France (http://www.akretion.com).
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'Stock Packaging Usability',
    'version': '12.0.1.0.0',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'summary': "Faster packaging process in Odoo",
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['stock'],
    'data': [
        'views/stock_picking.xml',
        'views/stock_move_line.xml',
        ],
    'installable': True,
}
