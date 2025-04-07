# Copyright 2025 Camptocamp SA
# @author: Italo LOPES <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase


class TestStockQuantPackageNumber(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package = cls.env["stock.quant.package"].create({})

    def test_01_package_number_computed_with_order_and_sheet_number(self):
        self.package.write(
            {
                "order_number": "ORD123",
                "sheet_number": 456,
            }
        )
        self.assertEqual(self.package.package_number, "ORD123_456")

    def test_02_package_number_is_empty_when_no_order_number(self):
        self.package.write(
            {
                "order_number": False,
                "sheet_number": 456,
            }
        )
        self.assertEqual(self.package.package_number, "")

    def test_03_package_number_is_empty_when_no_sheet_number(self):
        self.package.write(
            {
                "order_number": "ORD123",
                "sheet_number": False,
            }
        )
        self.assertEqual(self.package.package_number, "")

    def test_04_package_number_is_empty_when_no_order_and_sheet_number(self):
        package = self.env["stock.quant.package"].create({})
        self.assertEqual(package.package_number, "")
