# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def put_in_new_pack(self):
        self.ensure_one()
        pack = self.env["stock.quant.package"].create({})
        picking = self.picking_id
        pack_level = self.env["stock.package_level"].create(
            {
                "package_id": pack.id,
                "picking_id": picking.id,
                "location_id": False,
                "location_dest_id": self.location_dest_id.id,
                "move_line_ids": [(6, 0, [self.id])],
                "company_id": picking.company_id.id,
            }
        )
        self._put_in_target_pack(pack, pack_level)

    def put_in_last_pack(self):
        all_cur_packs_ids = [
            moveline2.result_package_id.id
            for moveline2 in self.picking_id.move_line_ids
            if moveline2.result_package_id
        ]
        if not all_cur_packs_ids:
            raise UserError(_("There is no current package."))
        pack_id = max(all_cur_packs_ids)
        pack = self.env["stock.quant.package"].browse(pack_id)
        pack_levels = self.env["stock.package_level"].search(
            [("package_id", "=", pack_id)]
        )
        if not pack_levels:
            raise UserError(
                _("Could not find any package level linked to package '%s'.")
                % pack.display_name
            )
        if len(pack_levels) > 1:
            raise UserError(
                _("There are several package levels linked to package '%s'.")
                % pack.display_name
            )
        self._put_in_target_pack(pack, pack_levels)

    def _put_in_target_pack(self, pack, pack_level):
        self.ensure_one()
        assert pack, "pack is a required argument"
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        if float_is_zero(self.qty_done, precision_digits=prec):
            raise UserError(_("Qty done is 0"))
        if self.result_package_id:
            raise UserError(_("This operation is already packaged."))
        moveline_to_pack = self
        if (
            float_compare(self.qty_done, self.product_uom_qty, precision_digits=prec)
            < 0
        ):
            quantity_left_todo = float_round(
                self.product_uom_qty - self.qty_done,
                precision_rounding=self.product_uom_id.rounding,
            )
            done_to_keep = self.qty_done
            # IMPORTANT: we first create the new move line with product_uom_qty=0
            # and THEN we write product_uom_qty = qty_done on it.
            # We MUSTN'T create the new move line directly with
            # product_uom_qty=self.qty_done because it doesn't update
            # the reserved_qty on the quant, because on stock.move.line
            # the inherit of write() calls
            # self.env['stock.quant']._update_reserved_quantity()
            # but the inherit of create() doesn't !
            new_moveline = self.copy({"product_uom_qty": 0, "qty_done": done_to_keep})
            self.write(
                {
                    "product_uom_qty": quantity_left_todo,
                    "qty_done": 0,
                }
            )
            new_moveline.write({"product_uom_qty": done_to_keep})
            moveline_to_pack = new_moveline
        pack_level.write({"move_line_ids": [(4, moveline_to_pack.id)]})
        moveline_to_pack.write({"result_package_id": pack.id})
