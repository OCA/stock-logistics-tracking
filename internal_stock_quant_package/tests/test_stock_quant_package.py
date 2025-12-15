# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestStockPickingInternal


class TestStockQuantPackage(TestStockPickingInternal):
    def test_is_internal(self):
        self.assertTrue(self.internal_package.is_internal)
        self.assertFalse(self.external_package.is_internal)
        # changing the package_type triggers the compute method and updates is_internal
        self.internal_package.write({"package_type_id": self.external_package_type.id})
        self.assertFalse(self.internal_package.is_internal)
        self.external_package.write({"package_type_id": self.internal_package_type.id})
        self.assertTrue(self.external_package.is_internal)
