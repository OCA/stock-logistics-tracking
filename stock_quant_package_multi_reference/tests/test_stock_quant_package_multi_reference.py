# © 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged

from ..hooks import post_init_hook


@tagged("post_install", "-at_install")
class StockQuantPackageReference(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Package 1
        cls.package = cls.env["stock.quant.package"]
        cls.package_1 = cls.package.create({"name": "PACK0000001"})
        cls.valid_reference_1 = "PACK0000001-1"
        cls.valid_reference2_1 = "PACK0000001-2"
        # Package 2
        cls.package_2 = cls.package.create({"name": "PACK0000002"})
        cls.valid_reference_2 = "PACK0000002-1"
        cls.valid_reference2_2 = "PACK0000002-2"

    def test_set_main_package(self):
        self.package_1.name = self.valid_reference_1
        self.assertEqual(len(self.package_1.reference_ids), 1)
        self.assertEqual(self.package_1.reference_ids.name, self.package_1.name)

    def test_set_incorrect_package(self):
        self.package_1.name = self.valid_reference_1
        # Insert duplicated EAN13
        with self.assertRaisesRegex(
            ValidationError,
            'The Reference "%(reference)s" already exists for package "%(package)s"'
            % {"reference": self.valid_reference_1, "package": self.package_1.name},
        ):
            self.package_1.reference_ids = [(0, 0, {"name": self.valid_reference_1})]

    def test_post_init_hook(self):
        # The delete SQL statement is necessary to remove the reference
        # that was created during the test setup for the stock.quant.package (PACK0000001).
        # This reference will not exist when the module is initialized for real usage.
        self.env.cr.execute(
            """
            DELETE FROM stock_quant_package_reference
            WHERE stock_quant_package_id = %s""",
            [(self.package_1.id)],
        )
        post_init_hook(self.env.cr, self.registry)
        self.package_1.invalidate_recordset()
        self.assertEqual(len(self.package_1.reference_ids), 1)
        self.assertEqual(self.package_1.reference_ids.name, self.package_1.name)

    def test_search(self):
        self.package_1.reference_ids = [
            (0, 0, {"name": self.valid_reference_1}),
            (0, 0, {"name": self.valid_reference2_1}),
        ]
        self.package_2.reference_ids = [
            (0, 0, {"name": self.valid_reference_2}),
            (0, 0, {"name": self.valid_reference2_2}),
        ]
        packages = self.package.search([("name", "=", self.valid_reference_1)])
        self.assertEqual(len(packages), 1)
        self.assertEqual(packages, self.package_1)
        packages = self.package.search([("name", "=", self.valid_reference2_1)])
        self.assertEqual(len(packages), 1)
        self.assertEqual(packages, self.package_1)
        packages = self.package.search(
            [
                "|",
                ("name", "=", self.valid_reference2_1),
                ("name", "=", self.valid_reference2_2),
            ]
        )
        self.assertEqual(len(packages), 2)
