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

from osv import fields, osv
from tools.translate import _
import time
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class stock_prodlot_swap(osv.osv_memory):
    _name = "stock.prodlot.swap"

    _columns = {
        'location_id': fields.many2one('stock.location', 'Location'),
        'parent_pack_id': fields.many2one('stock.tracking', 'Parent Pack'),
        'previous_prodlot_id': fields.many2one('stock.production.lot', 'Previous Production Lot'),
        'new_prodlot_id': fields.many2one('stock.production.lot', 'New Production Lot'),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        res=super(stock_prodlot_swap, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}                                                                      
        res.update({
            'parent_pack_id': context.get('active_id') or False,
        })
        return res
    
    def onchange_location(self, cr , uid, ids, location_id, parent_pack_id):
        tracking_obj = self.pool.get('stock.tracking')            
        prodlot_ids = []
        domain_prodlot_id = []
        if parent_pack_id:
            move_ids = tracking_obj.browse(cr, uid, parent_pack_id).current_move_ids
            for move_id in move_ids:
                if move_id.prodlot_id.id not in prodlot_ids:
                    prodlot_ids.append(move_id.prodlot_id.id)
        var = ('id','in', tuple(prodlot_ids))
        domain_prodlot_id.append(var)
        return {
            'domain': {
                'previous_prodlot_id': str(domain_prodlot_id)
            }
        }
    
    def swap_object(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        tracking_obj = self.pool.get('stock.tracking')
        history_obj = self.pool.get('stock.tracking.history')
        if context == None:
            context = {}
        for current in self.browse(cr, uid, ids, context=context):
            if not context.get('active_id'):
                raise osv.except_osv(_('Warning!'),_('Should Not Happen !'))
            parent_pack = tracking_obj.browse(cr, uid, context.get('active_id'), context=context)
            origin_id = parent_pack.location_id.id
            destination_id = current.location_id.id
            date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            pick_id = picking_obj.create(cr, uid, {
                'type': 'internal',
                'auto_picking': 'draft',
                'company_id': self.pool.get('res.company')._company_default_get(cr, uid, 'stock.company', context=context),
                'address_id': current.location_id.address_id and current.location_id.address_id.id or False,
                'invoice_state': 'none',
                'date': date,
                'state': 'done',
            }, context=context)
            hist_id = history_obj.create(cr, uid, {
               'tracking_id': parent_pack.id,
               'type': 'move',
               'location_id': destination_id,
               'location_dest_id': origin_id,
            }, context=context)
            # Previous prodlot
            move_ids = [x.id for x in parent_pack.current_move_ids]
            move_ids = move_obj.search(cr, uid, [('id','in',move_ids),('prodlot_id','=',current.previous_prodlot_id.id)], limit=1, context=context)
            if not move_ids:
                raise osv.except_osv(_('Warning!'),_('Production Lot Not Found !'))
            move_id = move_ids[0]
            defaults = {
                'location_id': origin_id,
                'location_dest_id': destination_id,
                'picking_id': pick_id,
                'date': date,
                'date_expected': date,
                'tracking_id': False,
                'state': 'done',
            }
            new_id = move_obj.copy(cr, uid, move_id, default=defaults, context=context)
            # New prodlot
            defaults = {
                'location_id': destination_id,
                'location_dest_id': origin_id,
                'picking_id': pick_id,
                'date': date,
                'date_expected': date,
                'tracking_id': parent_pack.id,
                'prodlot_id': current.new_prodlot_id.id,
                'product_id': current.new_prodlot_id.product_id.id,
                'product_qty': 1.0,
                'state': 'done',
            }
            new_id = move_obj.copy(cr, uid, move_id, default=defaults, context=context)
            move_obj.write(cr, uid, [move_id], {'pack_history_id': hist_id}, context=context)
        tracking_obj.get_serials(cr, uid, [parent_pack.id], context=context)
        return {'type': 'ir.actions.act_window_close'}
       
stock_prodlot_swap()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: