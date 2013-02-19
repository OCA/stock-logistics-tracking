# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class stock_packaging_delete(orm.TransientModel):
    _inherit = "stock.packaging.delete"
    
    _columns = {
        'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number'),
    }
    
    def onchange_type_id(self, cr, uid, ids, type_id, pack_id):
        result = super(stock_packaging_delete, self).onchange_type_id(cr, uid, ids, type_id, pack_id)
        prodlot_ids = []
        domain_prodlot_id = []
        if pack_id:
            move_ids = self.pool.get('stock.tracking').browse(cr, uid, pack_id).current_move_ids
            for move_id in move_ids:
                if move_id.prodlot_id.id not in prodlot_ids:
                    prodlot_ids.append(move_id.prodlot_id.id)
        var = ('id','in', tuple(prodlot_ids))
        domain_prodlot_id.append(var)
        result['domain'].update({
            'prodlot_id': str(domain_prodlot_id),
        })
        return result
    
    def delete_object(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        tracking_obj = self.pool.get('stock.tracking')
        res = super(stock_packaging_delete, self).delete_object(cr, uid, ids, context=context)
        for current in self.browse(cr, uid, ids, context=context):
            type = current.type_id.code
            pack_id = current.pack_id.id
            prodlot_id = current.prodlot_id.id
            if type == 'prodlot':
                tracking_obj.remove_prodlot(cr, uid, pack_id, prodlot_id, context=context)
        return res
       
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: