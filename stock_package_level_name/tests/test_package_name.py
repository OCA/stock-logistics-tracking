# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestPackageName(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package = cls.env["stock.quant.package"].create(
            {
                "name": "TEST PACK 1",
            }
        )

    def test_package_name(self):
        level = self.env["stock.package_level"].create(
            {"package_id": self.package.id, "company_id": self.env.company.id}
        )

        self.assertEqual("TEST PACK 1", level.display_name)
