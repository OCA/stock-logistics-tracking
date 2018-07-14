# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.one
    @api.depends('quant_ids', 'children_ids', 'ul_id')
    def _compute_weight(self):
        if self.ul_id:
            weight = self.ul_id.weight
            for quant in self.quant_ids:
                weight += quant.qty * quant.product_id.weight
            for pack in self.children_ids:
                pack._compute_weight()
                weight += pack.weight
            self.weight = weight
        else:
            super(StockQuantPackage, self)._compute_weight()
