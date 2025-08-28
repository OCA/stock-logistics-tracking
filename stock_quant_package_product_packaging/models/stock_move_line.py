# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        source_packages = self.package_id
        res = super()._action_done()
        # _action_done in stock module sometimes delete a move line, we
        # have to check if it still exists before reading/writing on it
        for line in self.exists().filtered(lambda ml: ml.result_package_id):
            line.result_package_id.auto_assign_packaging()
        source_packages._reset_empty_package_package_type()
        return res
