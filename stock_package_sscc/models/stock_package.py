# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPackage(models.Model):
    _inherit = "stock.package"

    sscc = fields.Char(
        string="SSCC",
        copy=False,
        help="Serial Shipping Container Code (GS1) identifying this logistic "
        "unit, e.g. a pallet, as given by the warehouse. Left empty for units "
        "without SSCC, such as postal parcels.",
    )
