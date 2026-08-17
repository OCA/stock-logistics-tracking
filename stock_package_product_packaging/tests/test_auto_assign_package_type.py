# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from .common import TestPackageTypeCommon


class TestAutoAssignPackageType(TestPackageTypeCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_packaging = cls.product_pallet_product_packaging
        cls.package_type = cls.product_packaging.package_type_id

        # Create a new package type for auto assignation
        vals = {
            "name": "Auto Assigned Package Type",
        }
        cls.auto_assigned_package_type = cls.env["stock.package.type"].create(vals)

    def test_auto_assign_package_type_without_packaging_id(self):
        """Packages without `packaging_id` are internal packages and they
        are intended to be stored in the warehouse.
        On such packages, a package type is automatically defined.
        """
        package = self.env["stock.package"].create(
            {"name": "TEST", "product_packaging_id": self.product_packaging.id}
        )

        self.assertEqual(package.package_type_id, self.package_type)

    def test_unpack_package_reset_package_type(self):
        """When the quants are moved out of a package, the package type is reset"""
        package = self.env["stock.package"].create(
            {"name": "TEST", "product_packaging_id": self.product_packaging.id}
        )

        self._update_qty_in_location(
            self.warehouse.lot_stock_id, self.product, 5, package=package
        )

        quants = package.quant_ids
        quants.move_quants(location_dest_id=self.warehouse.lot_stock_id, unpack=True)
        self.assertFalse(package.package_type_id)

    def test_unpack_package_no_reset_package_type(self):
        """Check quants moved out of a package, the package type is NOT reset."""
        package = self.env["stock.package"].create(
            {
                "name": "TEST",
                "product_packaging_id": self.product_packaging.id,
                "reset_package_type": False,
            }
        )
        self._update_qty_in_location(
            self.warehouse.lot_stock_id, self.product, 5, package=package
        )
        quants = package.quant_ids
        quants.move_quants(location_dest_id=self.warehouse.lot_stock_id, unpack=True)
        self.assertTrue(package.package_type_id)

    def test_auto_assign_packaging(self):
        """
        Test the auto assignation for package type from
        the default package type on the product

        - Set the default package type on the product
        - Create a move and validate it
        - The package type should be set on package
        """

        # Set a default package on the product
        self.product.package_type_id = self.auto_assigned_package_type

        confirmed_move = self._create_single_move(self.product)
        confirmed_move.location_dest_id = self.pallet_location
        confirmed_move._assign_picking()
        self._update_qty_in_location(
            confirmed_move.location_id,
            confirmed_move.product_id,
            confirmed_move.product_qty,
        )
        confirmed_move._action_assign()
        picking = confirmed_move.picking_id
        picking.action_confirm()
        picking.move_line_ids.picked = True
        first_package = picking.action_put_in_pack()

        picking.button_validate()

        self.assertEqual(self.auto_assigned_package_type, first_package.package_type_id)

    def test_auto_assign_no_packaging(self):
        """
        Test the non auto assignation for package type from
        the default package type on the product

        - Unset the default package type on the product
        - Create a move and validate it
        - The package type should not be set on package
        """

        # Set a default package on the product
        self.product.package_type_id = False

        confirmed_move = self._create_single_move(self.product)
        confirmed_move.location_dest_id = self.stock_location
        confirmed_move._assign_picking()
        self._update_qty_in_location(
            confirmed_move.location_id,
            confirmed_move.product_id,
            confirmed_move.product_qty,
        )
        confirmed_move._action_assign()
        picking = confirmed_move.picking_id
        picking.action_confirm()
        picking.move_line_ids.picked = True
        first_package = picking.action_put_in_pack()

        picking.button_validate()

        self.assertFalse(first_package.package_type_id)

    def test_auto_assign_packaging_pallet(self):
        """
        Test the auto assignation for package type from the quantity packaged
        """

        # Set a default package on the product
        self.product.package_type_id = self.auto_assigned_package_type

        confirmed_move = self._create_single_move(self.product, quantity=48)
        confirmed_move.location_dest_id = self.pallet_location
        confirmed_move._assign_picking()
        self._update_qty_in_location(
            confirmed_move.location_id,
            confirmed_move.product_id,
            confirmed_move.product_qty,
        )
        confirmed_move._action_assign()
        picking = confirmed_move.picking_id
        picking.action_confirm()
        picking.move_line_ids.picked = True
        first_package = picking.action_put_in_pack()

        picking.button_validate()
        self.assertEqual(
            self.product_pallet_product_packaging.package_type_id,
            first_package.package_type_id,
        )

    def test_find_best_packaging_pallet(self):
        packaging = self.product._find_best_packaging(48)
        self.assertEqual(packaging, self.product_pallet_product_packaging)

    def test_find_best_packaging_cardbox(self):
        packaging = self.product._find_best_packaging(4)
        self.assertEqual(packaging, self.product_cardbox_product_packaging)

    def test_find_best_packaging_single(self):
        packaging = self.product._find_best_packaging(5)
        self.assertEqual(packaging, self.product_single_bag_product_packaging)

    def test_find_best_packaging_no_match(self):
        packaging = self.product._find_best_packaging(5.5)
        self.assertFalse(packaging)

    def test_sync_package_type_on_multi_record_write(self):
        """Writing the packaging on several packages syncs each package type."""
        packages = self.env["stock.package"].create(
            [{"name": "TEST 1"}, {"name": "TEST 2"}]
        )
        packages.write({"product_packaging_id": self.product_packaging.id})
        self.assertEqual(packages[0].package_type_id, self.package_type)
        self.assertEqual(packages[1].package_type_id, self.package_type)

    def test_allowed_product_packaging_ids(self):
        """Only the packagings matching the contained quantity are allowed."""
        package = self.env["stock.package"].create({"name": "TEST"})
        self.assertFalse(package.allowed_product_packaging_ids)
        self._update_qty_in_location(
            self.warehouse.lot_stock_id, self.product, 48, package=package
        )
        package.invalidate_recordset()
        self.assertEqual(
            package.allowed_product_packaging_ids,
            self.product_pallet_product_packaging,
        )

    def test_auto_assign_packaging_multi_product_package(self):
        """A package holding several products cannot keep a product packaging."""
        other_product = self.env["product.product"].create(
            {"name": "Other Product", "is_storable": True}
        )
        package = self.env["stock.package"].create({"name": "TEST"})
        self._update_qty_in_location(
            self.warehouse.lot_stock_id, self.product, 48, package=package
        )
        package.auto_assign_packaging()
        self.assertEqual(
            package.product_packaging_id, self.product_pallet_product_packaging
        )
        self._update_qty_in_location(
            self.warehouse.lot_stock_id, other_product, 1, package=package
        )
        package.invalidate_recordset()
        self.assertFalse(package.single_product_id)
        self.assertFalse(package.allowed_product_packaging_ids)
        package.auto_assign_packaging()
        self.assertFalse(package.product_packaging_id)

    def test_existing_package_type_is_not_overwritten(self):
        """A package type set beforehand wins over the packaging one."""
        package = self.env["stock.package"].create(
            {
                "name": "TEST",
                "package_type_id": self.auto_assigned_package_type.id,
                "product_packaging_id": self.product_packaging.id,
            }
        )
        self.assertEqual(package.package_type_id, self.auto_assigned_package_type)

    def test_reset_package_type_on_emptied_package(self):
        """Delivering the whole package content resets its package type."""
        package = self.env["stock.package"].create(
            {"name": "TEST", "product_packaging_id": self.product_packaging.id}
        )
        self._update_qty_in_location(
            self.warehouse.lot_stock_id, self.product, 5, package=package
        )
        self._take_content_out_of_package(package, self.product, 5)
        self.assertFalse(package.quant_ids)
        self.assertFalse(package.package_type_id)

    def test_skip_reset_empty_package_package_type(self):
        """The package type is kept when the reset is skipped by context."""
        package = self.env["stock.package"].create(
            {"name": "TEST", "product_packaging_id": self.product_packaging.id}
        )
        self._update_qty_in_location(
            self.warehouse.lot_stock_id, self.product, 5, package=package
        )
        self._take_content_out_of_package(
            package,
            self.product,
            5,
            context={"skip_reset_empty_package_package_type": True},
        )
        self.assertFalse(package.quant_ids)
        self.assertEqual(package.package_type_id, self.package_type)

    def test_move_quants_without_unpack_keeps_package_type(self):
        """Moving a package to another location does not reset its package type."""
        package = self.env["stock.package"].create(
            {"name": "TEST", "product_packaging_id": self.product_packaging.id}
        )
        self._update_qty_in_location(
            self.warehouse.lot_stock_id, self.product, 5, package=package
        )
        package.quant_ids.move_quants(location_dest_id=self.pallet_location)
        self.assertEqual(package.package_type_id, self.package_type)
