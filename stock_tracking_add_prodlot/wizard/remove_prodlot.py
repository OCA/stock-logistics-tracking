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
    
    def _remove_prodlot(self, cr, uid, current, context=None):
        move_obj = self.pool.get('stock.move')
        tracking_obj = self.pool.get('stock.tracking')
        history_obj = self.pool.get('stock.tracking.history')
        prodlot_obj = self.pool.get('stock.production.lot')
        date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if context == None:
            context = {}
        hist_id = history_obj.create(cr, uid, {
           'tracking_id': current.pack_id.id,
           'type': 'move',
           'location_id': current.pack_id.location_id.id,
           'location_dest_id': current.pack_id.location_id.id,
        }, context=context)
        move_ids = [x.id for x in current.pack_id.current_move_ids]
        move_ids = move_obj.search(cr, uid, [
                        ('id','in',move_ids),
                        ('prodlot_id','=',current.prodlot_id.id)
                ], limit=1, context=context)
        if not move_ids:
            raise osv.except_osv(_('Warning!'),_('Prodlot Not Found !'))
        move_data = move_obj.browse(cr, uid, move_ids[0], context=context)
        move_qty = move_data.product_qty
        if move_qty != 1.0:
            defaults = {
                'location_id': current.pack_id.location_id.id,
                'location_dest_id': current.pack_id.location_id.id,
                'date': date,
                'date_expected': date,
                'tracking_id': current.pack_id.id,
                'product_id': current.product_id.id,
                'product_qty': move_qty - 1.0,
                'state': 'done',
            }
            new_id = move_obj.copy(cr, uid, move_data.id, default=defaults, context=context)
        defaults = {
            'location_id': current.pack_id.location_id.id,
            'location_dest_id': current.pack_id.location_id.id,
            'date': date,
            'date_expected': date,
            'tracking_id': False,
            'product_qty': 1.0,
            'state': 'done',
        }
        move_obj.copy(cr, uid, move_data.id, default=defaults, context=context)
        move_obj.write(cr, uid, [move_data.id], {'pack_history_id': hist_id}, context=context)
        prodlot_obj.write(cr, uid, current.prodlot_id.id, {'tracking_id': False}, context=context)
        
        tracking_obj.get_serials(cr, uid, [current.pack_id.id], context=context)
        tracking_obj.get_products(cr, uid, [current.pack_id.id], context=context)
        return True
    
    def delete_object(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        res = super(stock_packaging_delete, self).delete_object(cr, uid, ids, context=context)
        for current in self.browse(cr, uid, ids, context=context):
            type = current.type_id.code
            if type == 'prodlot':
                self._remove_prodlot(cr, uid, current, context=context)
        return res
       
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: