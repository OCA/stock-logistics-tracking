# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def move_quants(
        self, location_dest_id=False, package_dest_id=False, message=False, unpack=False
    ):
        packages = self.package_id
        res = super().move_quants(location_dest_id, package_dest_id, message, unpack)
        if unpack:
            packages._reset_empty_package_package_type()
        return res
