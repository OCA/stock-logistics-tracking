# Copyright 2019 Camptocamp SA
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    product_packaging_id = fields.Many2one(
        "product.packaging",
        "Product Packaging",
        index=True,
        help="Packaging of the product, used for internal logistics"
        "transfers, put-away rules, ...",
    )
    single_product_id = fields.Many2one(
        "product.product", compute="_compute_single_product"
    )
    single_product_qty = fields.Float(compute="_compute_single_product")

    @api.model_create_multi
    def create(self, vals):
        records = super().create(vals)
        for rec in records:
            rec._sync_package_type_from_packaging(rec.product_packaging_id)
        return records

    def write(self, vals):
        result = super().write(vals)
        if vals.get("product_packaging_id"):
            self._sync_package_type_from_packaging(self.product_packaging_id)
        return result

    @api.depends("quant_ids", "quant_ids.product_id")
    def _compute_single_product(self):
        for pack in self:
            pack_products = pack.quant_ids.mapped("product_id")
            if len(pack_products) == 1:
                pack.single_product_id = pack_products.id
                # TODO handle uom
                pack.single_product_qty = sum(pack.quant_ids.mapped("quantity"))
            else:
                pack.single_product_id = False
                pack.single_product_qty = 0

    def auto_assign_packaging(self):
        for pack in self:
            if pack.single_product_id and pack.single_product_qty:
                pack._assign_packaging(pack.single_product_id, pack.single_product_qty)
            elif pack.product_packaging_id and not pack.single_product_id:
                pack.product_packaging_id = False

    def _assign_packaging(self, product, quantity):
        self.ensure_one()
        packaging = product._find_best_packaging(quantity)
        if packaging and packaging.qty == quantity:
            # the call to write will trigger a call to _sync_package_type_from_packaging
            self.product_packaging_id = packaging
        elif self.product_packaging_id:
            self.product_packaging_id = False
        if packaging:
            self._sync_package_type_from_packaging(packaging)
        else:
            self._sync_package_type_from_single_product(product, quantity)

        if not self.package_type_id and product.package_type_id:
            self.package_type_id = product.package_type_id

    def _sync_package_type_from_packaging(self, packaging):
        for package in self:
            if package.package_type_id:
                # Do not set package type for delivery packages
                # to not trigger constraint like height requirement
                # (we are delivering them, not storing them)
                continue
            package_type = packaging.package_type_id
            if not package_type:
                continue
            package.package_type_id = package_type

    def _sync_package_type_from_single_product(self, product, quantity):
        for package in self:
            if package.package_type_id:
                # Do not set package type for delivery packages
                # to not trigger constraint like height requirement
                # (we are delivering them, not storing them)
                continue
            if product.package_type_id:
                package.package_type_id = product.package_type_id

    def _reset_empty_package_package_type(self):
        empty_packages = self.filtered(lambda rec: not rec.quant_ids)
        empty_packages.package_type_id = False
