# -*- encoding: utf-8 -*-
##############################################################################
#
#    Stock Packaging Usability UL module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class StockSelectUL(models.TransientModel):
    _name = 'stock.select.ul'
    _description = 'Select UL'
    _rec_name = 'ul_id'

    ul_id = fields.Many2one('product.ul', string='Logistic Unit')
    # required=False, because we accept that it can be left empty

    @api.multi
    def validate(self):
        self.ensure_one()
        ul = self.ul_id
        assert self.env.context.get('pack_function') is not None, \
            'missing context key pack_function'
        self = self.with_context(default_ul_id=(ul and ul.id or False))
        action = False
        if self.env.context.get('pack_function') == 'put_residual_in_new_pack':
            assert self.env.context.get('active_model') == \
                'stock.transfer_details', 'Wrong underlying model'
            trf_wiz = self.env['stock.transfer_details'].browse(
                self.env.context['active_id'])
            trf_wiz.put_residual_in_new_pack()
            action = trf_wiz.wizard_view()
        elif self.env.context.get('pack_function') == 'put_in_pack':
            assert self.env.context.get('active_model') == \
                'stock.transfer_details_items', 'Wrong underlying model'
            trf_line_wiz = self.env['stock.transfer_details_items'].browse(
                self.env.context['active_id'])
            trf_line_wiz.put_in_pack()
            action = trf_line_wiz.transfer_id.wizard_view()
        return action

    @api.multi
    def cancel(self):
        """We have to re-call the wizard when the user clicks on Cancel"""
        self.ensure_one()
        if self.env.context.get('pack_function') == 'put_residual_in_new_pack':
            assert self.env.context.get('active_model') == \
                'stock.transfer_details', 'Wrong underlying model'
            trf_wiz = self.env['stock.transfer_details'].browse(
                self.env.context['active_id'])
            action = trf_wiz.wizard_view()
        elif self.env.context.get('pack_function') == 'put_in_pack':
            assert self.env.context.get('active_model') == \
                'stock.transfer_details_items', 'Wrong underlying model'
            trf_line_wiz = self.env['stock.transfer_details_items'].browse(
                self.env.context['active_id'])
            action = trf_line_wiz.transfer_id.wizard_view()
        return action
