# Copyright 2019 Camptocamp SA
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        source_packages = self.package_id
        res = super()._action_done()
        # _action_done in stock module sometimes delete a move line, we
        # have to check if it still exists before reading/writing on it
        dest_packages = self.exists().result_package_id
        (dest_packages | source_packages).auto_assign_packaging()
        source_packages._reset_empty_package_package_type()
        return res
