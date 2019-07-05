# Copyright 2014-2019 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class StockSelectProductPackaging(models.TransientModel):
    _name = 'stock.select.product.packaging'
    _description = 'Select Product Packaging'

    packaging_id = fields.Many2one('product.packaging', string='Packaging')
    # required=False, because we accept that it can be left empty

    def validate(self):
        self.ensure_one()
        packaging = self.packaging_id
        assert self.env.context.get('pack_function') is not None, \
            'missing context key pack_function'
        self = self.with_context(
            default_packaging_id=(packaging and packaging.id or False))
        action = {}
        if self._context.get('pack_function') == 'put_selection_in_new_pack':
            assert self.env.context.get('active_model') == \
                'stock.picking', 'Wrong underlying model'
            pick = self.env['stock.picking'].browse(
                self.env.context['active_id'])
            pick.put_in_pack()
        elif self._context.get('pack_function') == 'put_in_new_pack':
            assert self.env.context.get('active_model') == \
                'stock.move.line', 'Wrong underlying model'
            ml = self.env['stock.move.line'].browse(
                self.env.context['active_id'])
            action = ml.put_in_new_pack()
        return action
