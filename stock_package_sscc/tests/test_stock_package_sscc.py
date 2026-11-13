# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestStockPackageSSCC(TransactionCase):
    def test_sscc_not_copied(self):
        """The SSCC identifies one logistic unit: a copied package has none."""
        package = self.env["stock.package"].create(
            {"name": "PAL-1", "sscc": "376123450000000017"}
        )
        self.assertEqual(package.sscc, "376123450000000017")
        self.assertFalse(package.copy().sscc)
