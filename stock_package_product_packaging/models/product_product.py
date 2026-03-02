# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, tools


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _find_best_packaging(self, quantity):
        self.ensure_one()
        base_uom = self.uom_id
        packagings = self.product_tmpl_id.uom_ids.sorted(
            key=lambda u: (-u._compute_quantity(1, base_uom, round=False), u.sequence)
        )
        for packaging in packagings:
            pkg_qty = packaging._compute_quantity(1, base_uom, round=False)
            if pkg_qty > quantity:
                continue
            nb, rem = divmod(quantity, pkg_qty)
            if tools.float_is_zero(rem, precision_digits=3):
                return packaging
        return self.env["uom.uom"]
