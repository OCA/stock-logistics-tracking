# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, tools


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _find_best_packaging(self, quantity):
        self.ensure_one()
        packagings = self.env["product.packaging"].search(
            [("product_id", "=", self.id), ("qty", "<=", quantity)],
            order="qty DESC, sequence ASC",
        )
        for packaging in packagings:
            nb, rem = divmod(quantity, packaging.qty)
            if tools.float_is_zero(rem, precision_digits=3):
                return packaging
        return self.env["product.packaging"]
