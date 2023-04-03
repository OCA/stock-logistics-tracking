# Copyright 2022 Sergio Teruel - Tecnativa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import config


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def put_in_pack(self):
        if (
            config["test_enable"]
            and not self.env.context.get("test_manual_package", False)
        ) or self.env.context.get("skip_manual_package", False):
            return super().put_in_pack()
        action = self.env.ref(
            "stock_picking_manual_package.action_manual_package_wiz"
        ).read()[0]
        wiz = self.env["stock.picking.manual.package.wiz"].create(
            {"picking_id": self.id}
        )
        action["res_id"] = wiz.id
        return action

    def _put_in_pack(self, move_line_ids):
        nbr_lines_into_package = self.env.context.get("nbr_lines_into_package", False)
        products = self.env.context.get("products_in_package", False)
        if products:
            move_line_ids = move_line_ids.filtered(lambda ln: ln.product_id in products)
        if nbr_lines_into_package:
            move_line_ids = move_line_ids[:nbr_lines_into_package]
        if not move_line_ids:
            raise UserError(_("There are no lines to pack."))
        return super()._put_in_pack(move_line_ids)
