# -*- coding: utf-8 -*-
# © 2014-2018 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    def put_in_new_pack(self):
        self.ensure_one()
        pack = self.env['stock.quant.package'].create({})
        self.put_in_target_pack(pack.id)

    def put_in_last_pack(self):
        all_cur_packs_ids = [
            packop2.result_package_id.id for packop2
            in self.picking_id.pack_operation_ids if packop2.result_package_id]
        if not all_cur_packs_ids:
            raise UserError(_('There is no current package.'))
        pack_id = max(all_cur_packs_ids)
        self.put_in_target_pack(pack_id)

    def put_in_target_pack(self, pack_id):
        self.ensure_one()
        assert pack_id, 'pack_id is a required argument'
        prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        if float_is_zero(self.qty_done, precision_digits=prec):
            raise UserError(_("Qty done is 0"))
        if self.result_package_id:
            raise UserError(_("This operation is already packaged."))
        packop_to_pack = self
        if float_compare(
                self.qty_done, self.product_qty, precision_digits=prec) < 0:
            new_packop = self.copy(
                {'product_qty': self.qty_done, 'qty_done': self.qty_done})
            self.write({
                'product_qty': self.product_qty - self.qty_done,
                'qty_done': 0,
                })
            if self.pack_lot_ids:
                new_packop.write({
                    'pack_lot_ids': [(6, 0, self.pack_lot_ids.ids)]})
                new_packop._copy_remaining_pack_lot_ids(self)
            packop_to_pack = new_packop

        packop_to_pack._check_serial_number()
        packop_to_pack.result_package_id = pack_id
