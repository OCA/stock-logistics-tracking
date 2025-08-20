# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import TransactionCase


class TestPackageTypeCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        ref = cls.env.ref
        cls.warehouse = ref("stock.warehouse0")
        # set two steps reception on warehouse
        cls.warehouse.reception_steps = "two_steps"

        cls.suppliers_location = ref("stock.stock_location_suppliers")
        cls.input_location = ref("stock.stock_location_company")
        cls.stock_location = ref("stock.stock_location_stock")
        cls.pallet_location = cls.env["stock.location"].create(
            {"name": "Pallets", "location_id": cls.stock_location.id}
        )

        cls.env["stock.location"]._parent_store_compute()

        cls.receipts_picking_type = ref("stock.picking_type_in")
        cls.internal_picking_type = ref("stock.picking_type_internal")

        cls.product = ref("product.product_product_9")
        cls.product_lot = ref("stock.product_cable_management_box")

        cls.package_type_pallets = cls.env["stock.package.type"].create(
            {"name": "Pallets"}
        )
        cls.package_type_cardboxes = cls.env["stock.package.type"].create(
            {"name": "Cardboxes"}
        )

        cls.product_cardbox_product_packaging = cls.env["product.packaging"].create(
            {
                "name": "4 units cardbox",
                "qty": 4,
                "product_id": cls.product.id,
                "package_type_id": cls.package_type_cardboxes.id,
            }
        )
        cls.product_single_bag_product_packaging = cls.env["product.packaging"].create(
            {
                "name": "Single Bag",
                "qty": 1,
                "product_id": cls.product.id,
            }
        )
        cls.product_pallet_product_packaging = cls.env["product.packaging"].create(
            {
                "name": "Pallet",
                "qty": 48,
                "product_id": cls.product.id,
                "package_type_id": cls.package_type_pallets.id,
            }
        )

        cls.internal_picking_type.write({"show_entire_packs": True})
        cls.receipts_picking_type.show_entire_packs = True

    @classmethod
    def _update_qty_in_location(
        cls, location, product, quantity, package=None, lot=None
    ):
        quants = cls.env["stock.quant"]._gather(
            product, location, lot_id=lot, package_id=package, strict=True
        )
        # this method adds the quantity to the current quantity, so remove it
        quantity -= sum(quants.mapped("quantity"))
        cls.env["stock.quant"]._update_available_quantity(
            product, location, quantity, package_id=package, lot_id=lot
        )

    @classmethod
    def _create_single_move(cls, product, quantity=2.0):
        picking_type = cls.warehouse.int_type_id
        move_vals = {
            "name": product.name,
            "picking_type_id": picking_type.id,
            "product_id": product.id,
            "product_uom_qty": quantity,
            "product_uom": product.uom_id.id,
            "location_id": cls.input_location.id,
            "location_dest_id": picking_type.default_location_dest_id.id,
            "state": "confirmed",
            "procure_method": "make_to_stock",
        }
        return cls.env["stock.move"].create(move_vals)
