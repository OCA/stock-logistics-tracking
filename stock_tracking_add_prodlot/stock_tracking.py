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
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class stock_tracking(orm.Model):
    _inherit = 'stock.tracking'
    
    def get_move_prodlot_vals(self, cr, uid, pack_id, prodlot_data, qty=False, move_data=False, context=None):
        if context == None:
            context = {}
        pack = self.browse(cr, uid, pack_id, context = context)
        vals = {
            'name': move_data and move_data.name or prodlot_data.name,
            'state': 'done',
            'product_id': move_data and move_data.prodlot_id.product_id.id or prodlot_data.product_id.id,
            'product_uom': move_data and move_data.product_uom.id or prodlot_data.product_id.uom_id.id,
            'prodlot_id': move_data and move_data.prodlot_id.id or prodlot_data.id,
            'location_id': move_data and move_data.location_dest_id.id or pack.location_id.id,
            'location_dest_id': pack.location_id.id,
            'tracking_id': pack.id,
            'product_qty': qty,
        }
        return vals
    
    def add_prodlots(self, cr, uid, pack_id, prodlot_ids, quantities=False, context=None):
        if context == None:
            context = {}
        move_obj = self.pool.get('stock.move')
        prodlot_obj =  self.pool.get('stock.production.lot')
        pack = pack_id
        modified = False
        for prodlot_data in prodlot_obj.browse(cr, uid, prodlot_ids, context = context):
            if quantities and quantities[prodlot_data.id]:
                qty = quantities[prodlot_data.id]
            move_ids = move_obj.search(cr, uid, [
                            ('state', '=', 'done'),
                            ('prodlot_id', '=', prodlot_data.id),
                        ], order='date desc', limit=1, context=context)
            vals = {}
            if move_ids:
                move_data = move_obj.browse(cr, uid, move_ids[0], context=context)
                vals = self.get_move_prodlot_vals(cr, uid, pack_id, prodlot_data, qty, move_data=move_data, context=context)
            else:
                vals = self.get_move_prodlot_vals(cr, uid, pack_id, prodlot_data, qty, move_data=False, context=context)
            if vals:
                new_move_id = move_obj.create(cr, uid, vals, context=context)
                modified = True
        if modified:
            self.write(cr, uid, pack, {'modified': True}, context=context)
        self.get_products(cr, uid, [pack], context=context)
        self.get_serials(cr, uid, [pack], context=context)
        return True
    
    
    def remove_prodlot(self, cr, uid, pack_id, prodlot_id, context=None):
        
        # Initialization #
        
        move_obj = self.pool.get('stock.move')
        history_obj = self.pool.get('stock.tracking.history')
        prodlot_obj = self.pool.get('stock.production.lot')
        product_obj = self.pool.get('product.product')
        date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if context == None:
            context = {}
            
        pack = self.browse(cr, uid, pack_id, context=context)
        prodlot = prodlot_obj.browse(cr, uid, prodlot_id, context=context)
        
        
        
        # Process #
        
        hist_id = history_obj.create(cr, uid, {
           'tracking_id': pack.id,
           'type': 'move',
           'location_id': pack.location_id.id,
           'location_dest_id': pack.location_id.id,
        }, context=context)
        move_ids = [x.id for x in pack.current_move_ids]
        move_ids = move_obj.search(cr, uid, [
                        ('id','in',move_ids),
                        ('prodlot_id','=',prodlot.id)
                ], limit=1, context=context)
        if not move_ids:
            raise osv.except_osv(_('Warning!'),_('Prodlot Not Found !'))
        move_data = move_obj.browse(cr, uid, move_ids[0], context=context)
        move_qty = move_data.product_qty
        if move_qty != 1.0:
            defaults = {
                'location_id': pack.location_id.id,
                'location_dest_id': pack.location_id.id,
                'date': date,
                'date_expected': date,
                'tracking_id': pack.id,
                'product_id': prodlot.product_id.id,
                'product_qty': move_qty - 1.0,
                'state': 'done',
            }
            new_id = move_obj.copy(cr, uid, move_data.id, default=defaults, context=context)
        defaults = {
            'location_id': pack.location_id.id,
            'location_dest_id': pack.location_id.id,
            'date': date,
            'date_expected': date,
            'tracking_id': False,
            'product_qty': 1.0,
            'state': 'done',
        }
        move_obj.copy(cr, uid, move_data.id, default=defaults, context=context)
        move_obj.write(cr, uid, [move_data.id], {'pack_history_id': hist_id}, context=context)
        prodlot_obj.write(cr, uid, prodlot.id, {'tracking_id': False}, context=context)
        
        self.get_serials(cr, uid, [pack.id], context=context)
        self.get_products(cr, uid, [pack.id], context=context)
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
