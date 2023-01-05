# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock.tests.test_packing import TestPackingCommon


class TestStockQuantPackageDelivery(TestPackingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_test = cls.env["product.product"].create(
            {
                "name": "Product TEST",
                "type": "product",
                "weight": 0.1,
                "uom_id": cls.uom_kg.id,
                "uom_po_id": cls.uom_kg.id,
            }
        )
        test_carrier_product = cls.env["product.product"].create(
            {
                "name": "Test carrier product",
                "type": "service",
            }
        )
        cls.test_carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test carrier",
                "delivery_type": "fixed",
                "product_id": test_carrier_product.id,
            }
        )

    def test_put_in_pack_choose_carrier_wizard(self):
        """
        Check that de number of packages is correctly correctly set on created package
        when using the 'choose.delivery.package' wizard.
        """
        self.env["stock.quant"]._update_available_quantity(
            self.product_test, self.stock_location, 20.0
        )

        picking_ship = self.env["stock.picking"].create(
            {
                "partner_id": self.env["res.partner"].create({"name": "A partner"}).id,
                "picking_type_id": self.warehouse.out_type_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "carrier_id": self.test_carrier.id,
            }
        )
        picking_ship.action_confirm()
        # create a move line for the picking
        self.env["stock.move.line"].create(
            {
                "product_id": self.product_test.id,
                "product_uom_id": self.uom_kg.id,
                "picking_id": picking_ship.id,
                "qty_done": 5,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        pack_action = picking_ship.action_put_in_pack()
        pack_action_ctx = pack_action["context"]
        pack_action_model = pack_action["res_model"]
        # We make sure the correct action was returned
        self.assertEqual(pack_action_model, "choose.delivery.package")
        # check there is no package yet for the picking
        self.assertEqual(len(picking_ship.package_ids), 0)
        # We instanciate the wizard with the context of the action
        pack_wiz = (
            self.env["choose.delivery.package"]
            .with_context(**pack_action_ctx)
            .create({"number_packages": 3})
        )
        pack_wiz.action_put_in_pack()
        # check that one package has been created with the same number of packages
        self.assertEqual(len(picking_ship.package_ids), 1)
        package1 = picking_ship.package_ids[0]
        self.assertEqual(package1.number_packages, 3)
        # create another move line and put in pack again
        self.env["stock.move.line"].create(
            {
                "product_id": self.product_test.id,
                "product_uom_id": self.uom_kg.id,
                "picking_id": picking_ship.id,
                "qty_done": 5,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        pack_action = picking_ship.action_put_in_pack()
        pack_action_ctx = pack_action["context"]
        pack_action_model = pack_action["res_model"]
        # We make sure the correct action was returned
        self.assertEqual(pack_action_model, "choose.delivery.package")
        # We instanciate the wizard again
        pack_wiz = (
            self.env["choose.delivery.package"]
            .with_context(**pack_action_ctx)
            .create({"number_packages": 5})
        )
        pack_wiz.action_put_in_pack()
        # check that a new package has been created with the new number of packages
        self.assertEqual(len(picking_ship.package_ids), 2)
        package2 = picking_ship.package_ids[-1]
        self.assertEqual(package2.number_packages, 5)
