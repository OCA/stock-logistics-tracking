# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPackage_level(models.Model):
    _inherit = "stock.package_level"

    @api.depends("package_id")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for level in self:
            level.display_name = level.package_id.display_name
        return res
