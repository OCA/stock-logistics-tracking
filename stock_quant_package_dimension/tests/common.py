# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import TransactionCase


class TestStockQuantPackageCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh.out_type_id.default_location_dest_id = cls.env.ref(
            "stock.stock_location_customers"
        )
        location_dest = cls.wh.out_type_id.default_location_dest_id.id
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "standard_price": 10,
                "list_price": 20,
            }
        )
        cls.product.write(
            {
                "weight": 1,
                "uom_ids": [
                    (0, 0, {"name": "Small Box"}),
                    (0, 0, {"name": "Box"}),
                ],
            }
        )
        cls.package = cls.env["stock.package"].create({})
        cls.move = cls.env["stock.move"].create(
            {
                "picking_type_id": cls.wh.out_type_id.id,
                "product_id": cls.product.id,
                "product_uom_qty": 11.0,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.wh.out_type_id.default_location_src_id.id,
                "location_dest_id": location_dest,
                "procure_method": "make_to_stock",
                "rule_id": cls.env["stock.rule"]
                .create(
                    {
                        "name": "Test",
                        "location_dest_id": location_dest,
                        "route_id": cls.env.ref("stock.route_warehouse0_mto").id,
                        "picking_type_id": cls.wh.out_type_id.id,
                    }
                )
                .id,
            }
        )
        cls.move._assign_picking()
        cls.move.picking_id.action_confirm()
