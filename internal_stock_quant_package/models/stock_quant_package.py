# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    is_internal = fields.Boolean(
        compute="_compute_is_internal", store=True, string="Internal use?"
    )

    @api.depends("package_type_id")
    def _compute_is_internal(self):
        for record in self:
            record.is_internal = (
                record.package_type_id
                and not record.package_type_id.package_carrier_type
            )
