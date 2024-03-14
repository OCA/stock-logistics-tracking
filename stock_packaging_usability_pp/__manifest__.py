# Copyright 2014-2019 Akretion France (http://www.akretion.com).
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Packaging Usability (Product Packaging)',
    'version': '12.0.1.0.0',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'summary': "Faster packaging process with product packaging",
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-tracking',
    'depends': [
        'stock_packaging_usability',
        'delivery',
        ],
    'data': [
        'wizard/stock_select_product_packaging_view.xml',
        'views/stock_picking.xml',
        'views/stock_move_line.xml',
        'views/stock_quant_package.xml',
        'views/product_packaging.xml',
        ],
    'installable': True,
}
