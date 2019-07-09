# Copyright 2019 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    # Fixing bug https://github.com/odoo/odoo/issues/34702
    # and take into account the weight of the packaging
    @api.one
    @api.depends('quant_ids')
    def _compute_weight(self):
        print('xxxxxxxxxxxxxxx')
        weight = 0.0
        weight_uom_categ = self.env.ref('uom.product_uom_categ_kgm')
        kg_uom = self.env.ref('uom.product_uom_kgm')
        if self.env.context.get('picking_id'):
            current_picking_move_line_ids = self.env['stock.move.line'].search(
                [('result_package_id', '=', self.id),
                 ('picking_id', '=', self.env.context['picking_id'])])
            for ml in current_picking_move_line_ids:
                if ml.product_uom_id.category_id == weight_uom_categ:
                    weight += ml.product_uom_id._compute_quantity(
                        ml.qty_done, kg_uom)
                else:
                    weight += ml.product_uom_id._compute_quantity(
                        ml.qty_done, ml.product_id.uom_id) \
                        * ml.product_id.weight
        else:
            for quant in self.quant_ids:
                if quant.product_id.uom_id.category_id == weight_uom_categ:
                    weight += quant.product_id.uom_id._compute_quantity(
                        quant.quantity, kg_uom)
                else:
                    weight += quant.quantity * quant.product_id.weight
        if self.packaging_id:
            weight += self.packaging_id.weight
        self.weight = weight
