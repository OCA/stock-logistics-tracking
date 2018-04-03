# -*- coding: utf-8 -*-
# Copyright 2014-2018 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class StockSelectUL(models.TransientModel):
    _name = 'stock.select.ul'
    _description = 'Select UL'

    ul_id = fields.Many2one('product.ul', string='Logistics Unit')
    # required=False, because we accept that it can be left empty

    def validate(self):
        self.ensure_one()
        ul = self.ul_id
        assert self.env.context.get('pack_function') is not None, \
            'missing context key pack_function'
        self = self.with_context(default_ul_id=(ul and ul.id or False))
        if self._context.get('pack_function') == 'put_selection_in_new_pack':
            assert self.env.context.get('active_model') == \
                'stock.picking', 'Wrong underlying model'
            pick = self.env['stock.picking'].browse(
                self.env.context['active_id'])
            pick.put_in_pack()
        elif self._context.get('pack_function') == 'put_in_new_pack':
            assert self.env.context.get('active_model') == \
                'stock.pack.operation', 'Wrong underlying model'
            pack_op = self.env['stock.pack.operation'].browse(
                self.env.context['active_id'])
            pack_op.put_in_new_pack()
        return
