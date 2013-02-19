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

class stock_packaging_remove(orm.TransientModel):
    _name = "stock.packaging.remove"
    
    _columns = {        
        'type_id': fields.many2one('stock.packaging.add.type', 'Type', required=True),
        'type': fields.char('Type', size=64),
        'pack_id': fields.many2one('stock.tracking', 'Pack'),
        'product_id': fields.many2one('product.product', 'Product'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number'),
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
        prodlot_ids = []
        domain_product_id = []
        domain_prodlot_id = []
        res = {'value': {'type': ''}}
        code_type = 'product'
        if type_id:
            type_obj = self.pool.get('stock.packaging.add.type')
            type = type_obj.read(cr, uid, type_id, ['code'])
            if type['code']:
                code_type = type['code']
                res = {'value': {'type': type['code']}}
        if pack_id:
            move_ids = self.pool.get('stock.tracking').browse(cr, uid, pack_id).current_move_ids
            for move_id in move_ids:
                if code_type == 'product' and (move_id.product_id.id not in product_ids) and not move_id.prodlot_id:
                    product_ids.append(move_id.product_id.id)  
            for move_id in move_ids:
                if code_type == 'prodlot' and move_id.prodlot_id.id not in prodlot_ids:
                    prodlot_ids.append(move_id.prodlot_id.id)
        if code_type == 'product':
            var = ('id','in', tuple(product_ids))
            domain_product_id.append(var)
            res.update({
                'domain': {
                    'product_id': str(domain_product_id),
                }
            })
        elif code_type == 'prodlot':
            var = ('id','in', tuple(prodlot_ids))
            domain_prodlot_id.append(var)
            res.update({
                'domain': {
                    'prodlot_id': str(domain_prodlot_id),
                }
            })
        return res
    
    def remove_object(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        tracking_obj = self.pool.get('stock.tracking')    
        for current in self.browse(cr, uid, ids, context=context):
            code_type = current.type_id.code
            pack_id = current.pack_id.id
            if code_type == 'product':
                product_id = current.product_id.id
                tracking_obj._remove_products(cr, uid, pack_id, product_id, context=context)
            elif code_type == 'prodlot':
                prodlot_id = current.prodlot_id.id
                tracking_obj._remove_prodlot(cr, uid, pack_id, prodlot_id, context=context)
        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: