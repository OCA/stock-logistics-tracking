# Copyright 2025 Camptocamp SA
# @author: Italo LOPES <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    package_number = fields.Char(compute="_compute_package_number", store=True)
    order_number = fields.Char()
    sheet_number = fields.Integer()

    @api.depends("order_number", "sheet_number")
    def _compute_package_number(self):
        for package in self:
            if package.order_number and package.sheet_number:
                package.package_number = (
                    f"{package.order_number}_{package.sheet_number}"
                )
            else:
                package.package_number = ""
