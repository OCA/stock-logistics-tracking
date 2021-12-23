# Copyright 2019-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    name = fields.Char(translate=True)
    weight = fields.Float(
        digits="Stock Weight",
        string="Empty Package Weight",
        help="Empty package weight in kg",
    )
    active = fields.Boolean(default=True)
    # packaging_type is important, in particular for pallets for which
    # we need a special implementation to enter the height
    packaging_type = fields.Selection(
        [
            ("unit", "Unit"),
            ("pack", "Pack"),
            ("box", "Box"),
            ("pallet", "Pallet"),
        ],
        string="Type",
    )
