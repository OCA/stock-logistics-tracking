# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _put_in_pack(self, move_line_ids, create_package_level=True):
        res = super()._put_in_pack(move_line_ids, create_package_level)
        number_packages = self.env.context.get("set_number_packages")
        if res and number_packages is not None:
            res.number_packages = number_packages
        return res
