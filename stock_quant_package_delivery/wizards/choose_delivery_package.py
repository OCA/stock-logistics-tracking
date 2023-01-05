# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ChooseDeliveryPackage(models.TransientModel):
    _inherit = "choose.delivery.package"

    number_packages = fields.Integer("Number of packages", default=1)

    def action_put_in_pack(self):
        ctx_self = self.with_context(set_number_packages=self.number_packages)
        return super(ChooseDeliveryPackage, ctx_self).action_put_in_pack()
