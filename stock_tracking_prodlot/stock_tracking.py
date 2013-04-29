 # -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

'''Add a field in order to store the current pack in a production lot'''
class stock_production_lot(orm.Model):
    _inherit = 'stock.production.lot'
    _columns = {
        'tracking_id': fields.many2one('stock.tracking', 'pack'),
    }
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
#            'state': 'draft',
#            'shipped': False,
            'tracking_id': False,
#            'move_ids': [],
        })
        return super(stock_production_lot, self).copy(cr, uid, id, default, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
