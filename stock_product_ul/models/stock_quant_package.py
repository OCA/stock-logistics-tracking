# Copyright 2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    ul_id = fields.Many2one(
        'product.ul', string='Logistics Unit', ondelete='restrict')
