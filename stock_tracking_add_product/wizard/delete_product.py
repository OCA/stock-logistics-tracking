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
    _name = "stock.packaging.delete"
    
    _columns = {        
        'type_id': fields.many2one('stock.packaging.add.type', 'Type', required=True),
        'type': fields.char('Type', size=64),
        'pack_id': fields.many2one('stock.tracking', 'Pack'),
        'product_id': fields.many2one('product.product', 'Product'),
    }
    
    def _get_type_id(self, cr, uid, context):
        if context == None:
            context = {}
        if context.get('type_selection'):
            type = context.get('type_selection')
        else:
            type = 'product'
        type_obj = self.pool.get('stock.packaging.add.type')
        default_type = type_obj.search(cr, uid, [('code', '=', type)], limit=1, context=context)
        if not default_type:
            default_type = type_obj.search(cr, uid, [], limit=1, context=context)
        return default_type and default_type[0] or False
    
    def _get_type(self, cr, uid, context=None):
        if context == None:
            context = {}
        if context.get('type_selection'):
            type = context.get('type_selection')
        else:
            type = 'product'
        res_type = ''
        type_obj = self.pool.get('stock.packaging.add.type')
        default_type = type_obj.search(cr, uid, [('code', '=', type)], limit=1, context=context)
        if not default_type:
            default_type = type_obj.search(cr, uid, [], limit=1, context=context)
        if default_type and default_type[0]:
            read_type = type_obj.read(cr, uid, default_type[0], ['code'], context=context)
            if read_type['code']:
                res_type = read_type['code']
        return res_type or ''
    
    _defaults = {
        'pack_id': lambda self, cr, uid, context: context.get('active_id') or False,
        'type_id': lambda self, cr, uid, context: self._get_type_id(cr, uid, context),
        'type': lambda self, cr, uid, context: self._get_type(cr, uid, context),
    }
    
    def onchange_type_id(self, cr, uid, ids, type_id, pack_id):
        product_ids = []
        domain_product_id = []
        res = {'value': {'type': ''}}
        if type_id:
            type_obj = self.pool.get('stock.packaging.add.type')
            type = type_obj.read(cr, uid, type_id, ['code'])
            if type['code']:
                res = {'value': {'type': type['code']}}
        if pack_id:
            move_ids = self.pool.get('stock.tracking').browse(cr, uid, pack_id).current_move_ids
            for move_id in move_ids:
                if (move_id.product_id.id not in product_ids) and not move_id.prodlot_id:
                    product_ids.append(move_id.product_id.id)  
                    
        var = ('id','in', tuple(product_ids))
        domain_product_id.append(var)
        res.update({
            'domain': {
                'product_id': str(domain_product_id)
            }
        })
        return res
        
    def _delete_products(self, cr, uid, current, context=None):
        move_obj = self.pool.get('stock.move')
        tracking_obj = self.pool.get('stock.tracking')
        history_obj = self.pool.get('stock.tracking.history')
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
                    ('product_id','=',current.product_id.id),
                    ('prodlot_id','=',False)
                ], limit=1, context=context)
        if not move_ids:
            raise osv.except_osv(_('Warning!'),_('Product Not Found !'))
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
        tracking_obj.get_products(cr, uid, [current.pack_id.id], context=context)
        return True
    
    def delete_object(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        for current in self.browse(cr, uid, ids, context=context):
            type = current.type_id.code
            if type == 'product':
                self._delete_products(cr, uid, current, context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: