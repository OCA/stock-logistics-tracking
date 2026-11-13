# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.fields import Command

from .common import TestStockPickingInternal


class TestStockPickingInternalFlow(TestStockPickingInternal):
    def test_internal_result_package_emptied_on_transfer(self):
        self.assertEqual(self.picking.state, "assigned")
        packop = self.picking.move_line_ids
        packop.write(
            dict(
                result_package_id=self.internal_package.id,
                picked=True,
            )
        )
        self.picking.button_validate()
        self.assertEqual(self.picking.state, "done")
        self.assertFalse(self.internal_package.quant_ids)

    def test_internal_result_package_not_emptied_on_transfer(self):
        self.picking_type_out.empty_internal_package_on_transfer = False
        self.assertEqual(self.picking.state, "assigned")
        packop = self.picking.move_line_ids
        packop.write(
            dict(
                result_package_id=self.internal_package.id,
                picked=True,
            )
        )
        self.picking.button_validate()
        self.assertEqual(self.picking.state, "done")
        self.assertTrue(self.internal_package.quant_ids)

    def test_external_package_not_emptied_on_transfer(self):
        self.assertEqual(self.picking.state, "assigned")
        packop = self.picking.move_line_ids
        packop.write(
            dict(
                result_package_id=self.external_package.id,
                picked=True,
            )
        )
        self.picking.button_validate()
        self.assertEqual(self.picking.state, "done")
        self.assertTrue(self.external_package.quant_ids)

    def test_internal_package_emptied_on_put_in_pack(self):
        self.assertEqual(self.picking.state, "assigned")
        packop = self.picking.move_line_ids
        packop.write(
            dict(
                result_package_id=self.internal_package.id,
                picked=True,
            )
        )
        self.picking.action_put_in_pack()
        self.assertNotEqual(packop.result_package_id, self.internal_package)
        self.picking.button_validate()
        self.assertEqual(self.picking.state, "done")
        self.assertFalse(self.internal_package.quant_ids)

    def test_internal_package_not_emptied_on_put_in_pack(self):
        self.picking_type_out.empty_internal_package_on_transfer = False
        self.assertEqual(self.picking.state, "assigned")
        packop = self.picking.move_line_ids
        packop.write(
            dict(
                result_package_id=self.internal_package.id,
                picked=True,
            )
        )
        msg = "Please add 'Done' quantities to the picking to create a new pack."
        with self.assertRaises(UserError, msg=msg):
            self.picking.action_put_in_pack()
        self.equal = self.assertEqual(packop.result_package_id, self.internal_package)
        self.picking.button_validate()
        self.assertEqual(self.picking.state, "done")
        self.assertTrue(self.internal_package.quant_ids)

    def test_internal_package_emptied_on_transfer_depend_on_carrier(self):
        carrier_product = self.env["product.product"].create(
            {"name": "Product Carrier", "sale_ok": False, "type": "service"}
        )
        carrier_1 = self.env["delivery.carrier"].create(
            {
                "name": "Carrier1",
                "product_id": carrier_product.id,
            }
        )
        self.picking.carrier_id = carrier_1
        vals_line = {"empty": False, "delivery_carrier_id": carrier_1.id}
        vals = {"stock_internal_package_config_line_ids": [Command.create(vals_line)]}
        self.picking_type_out.write(vals)

        self.assertFalse(self.picking.empty_internal_package_on_transfer)

        line = self.picking_type_out.stock_internal_package_config_line_ids
        line.empty = True

        self.assertTrue(self.picking.empty_internal_package_on_transfer)

    def test_internal_package_emptied_on_put_in_pack_of_selected_lines(self):
        """'Put in Pack' of the Detailed Operations list only packs the
        selected move lines"""
        product_b = self.env["product.product"].create(
            {"name": "Product B", "type": "consu", "is_storable": True}
        )
        self.env["stock.quant"]._update_available_quantity(
            product_b, self.stock_location, 1
        )
        self.env["stock.move"].create(
            {
                "name": product_b.name,
                "product_id": product_b.id,
                "product_uom_qty": 1,
                "product_uom": product_b.uom_id.id,
                "picking_id": self.picking.id,
                "location_dest_id": self.customer_location.id,
                "location_id": self.stock_location.id,
            }
        )
        self.picking.action_assign()
        self.picking.move_line_ids.write(
            dict(
                result_package_id=self.internal_package.id,
                picked=True,
            )
        )
        line_a = self.picking.move_line_ids.filtered(
            lambda line: line.product_id == self.product_a
        )
        line_b = self.picking.move_line_ids - line_a
        line_a.action_put_in_pack()
        self.assertTrue(line_a.result_package_id)
        self.assertNotEqual(line_a.result_package_id, self.internal_package)
        self.assertEqual(line_b.result_package_id, self.internal_package)
