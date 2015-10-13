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
        'product_ids': fields.one2many('stock.packaging.remove.line', 'parent_id', 'Lines', domain=[('product_id', '!=', False)]),
        'prodlot_ids': fields.one2many('stock.packaging.remove.line', 'parent_id', 'Lines', domain=[('prodlot_id', '!=', False)]),
    }
    
    def _get_type_id(self, cr, uid, context):
        if context is None:
            context = {}
        type = context.get('type_selection', 'product')
        type_obj = self.pool.get('stock.packaging.add.type')
        default_type = type_obj.search(cr, uid, [('code', '=', type)], limit=1, context=context)
        if not default_type:
            default_type = type_obj.search(cr, uid, [], limit=1, context=context)
        return default_type and default_type[0] or False
    
    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        type = context.get('type_selection', 'product')
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
        'pack_id': lambda self, cr, uid, context: context.get('active_id', False),
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
        return res
    
    def remove_object(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        tracking_obj = self.pool.get('stock.tracking')    
        for current in self.browse(cr, uid, ids, context=context):
            code_type = current.type_id.code
            pack_id = current.pack_id.id
            if code_type == 'product':
                product_ids = current.product_ids
                tracking_obj._remove_products(cr, uid, pack_id, product_ids, context=context)
            elif code_type == 'prodlot':
                prodlot_ids = current.prodlot_ids
                tracking_obj._remove_prodlot(cr, uid, pack_id, prodlot_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

    """
        DO NOT DELETE THIS: maybe put this part to an other module.
        This is getting automatically the products or prodlots found in the pack with the related quantities.
    """
#    def _line_data(self, cr, uid, move):
#        data = {
#            'product_id' : move.product_id and move.product_id.id or False,
#            'quantity' : move.product_qty or 0,
#            'move_id': move.id,
#            'prodlot_id': move.prodlot_id and move.prodlot_id.id or False,
#        }
#        return data
#
#    def default_get(self, cr, uid, fields, context=None):
#        if context is None: context = {}
#        code_type = context.get('type_selection') or False
#        res = super(stock_packaging_remove, self).default_get(cr, uid, fields, context=context)
#        product_ids = []
#        prodlot_ids = []
#        pack_id = context.get('active_id')
#        move_ids = context.get('active_ids', [])
#        pack_obj = self.pool.get('stock.tracking')
#        move_obj = self.pool.get('stock.move')
#        if not pack_id:
#            return res
#        if 'product_ids' in fields and code_type == 'product':
#            pack = pack_obj.browse(cr, uid, pack_id, context=context)
#            move_ids = pack.current_move_ids
#            product = [self._line_data(cr, uid, m) for m in move_ids if not m.prodlot_id]
#            res.update(product_ids=product)
#        if 'prodlot_ids' in fields and code_type == 'prodlot':
#            pack = pack_obj.browse(cr, uid, pack_id, context=context)
#            move_ids = pack.current_move_ids
#            prodlot = [self._line_data(cr, uid, m) for m in move_ids if m.prodlot_id]
#            res.update(prodlot_ids=prodlot)
#        return res

class stock_packaging_remove_line(orm.TransientModel):

    _name = "stock.packaging.remove.line"
    _description = "Remove object to a pack"
    
    _columns = {
        'parent_id': fields.many2one('stock.packaging.remove', 'Parent'),
        'pack_id': fields.many2one('stock.tracking', 'Pack'),
        'product_id': fields.many2one('product.product', 'Product'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot'),
        'move_id': fields.many2one('stock.move', 'Move'),
        'quantity': fields.float('Quantity'),
    }
    
    def onchange_pack_id(self, cr, uid, ids, pack_id, context=None):
        if context is None:
            context = {}
        res = {}
        product_ids = []
        prodlot_ids = []
        domain_product_id = []
        domain_prodlot_id = []
        code_type = context.get('code_type') or 'product'
        if pack_id:
            move_ids = self.pool.get('stock.tracking').browse(cr, uid, pack_id, context=context).current_move_ids
            for move_id in move_ids:
                if code_type == 'product' and (move_id.product_id.id not in product_ids) and not move_id.prodlot_id:
                    product_ids.append(move_id.product_id.id)  
            for move_id in move_ids:
                if code_type == 'prodlot' and move_id.prodlot_id.id not in prodlot_ids:
                    prodlot_ids.append(move_id.prodlot_id.id)
        if code_type == 'product':
            var = ('id', 'in', tuple(product_ids))
            domain_product_id.append(var)
            res.update({
                'domain': {
                    'product_id': str(domain_product_id),
                }
            })
        elif code_type == 'prodlot':
            var = ('id', 'in', tuple(prodlot_ids))
            domain_prodlot_id.append(var)
            res.update({
                'domain': {
                    'prodlot_id': str(domain_prodlot_id),
                }
            })
        return res
    
    def onchange_product_id(self, cr, uid, ids, product_id, pack_id, context=None):
        if context is None:
            context = {}
        value = {}
        if pack_id and product_id:
            tracking_obj = self.pool.get('stock.tracking')
            move_obj = self.pool.get('stock.move')
            current_moves = tracking_obj.browse(cr, uid, pack_id, context=context).current_move_ids
            current_moves_ids = [x.id for x in current_moves]
            move_ids = move_obj.search(cr, uid, [
                    ('id', 'in', current_moves_ids),
                    ('product_id', '=', product_id),
                    ('prodlot_id', '=', False)
                ], limit=1, context=context)
            if move_ids:
                move = move_obj.read(cr, uid, move_ids[0], ['product_qty'], context=context)
                value = {'quantity': move['product_qty'], 'move_id': move_ids[0]}
        return {'value': value}
    
    def onchange_prodlot_id(self, cr, uid, ids, prodlot_id, pack_id, context=None):
        if context is None:
            context = {}
        value = {}
        if pack_id and prodlot_id:
            tracking_obj = self.pool.get('stock.tracking')
            move_obj = self.pool.get('stock.move')
            current_moves = tracking_obj.browse(cr, uid, pack_id, context=context).current_move_ids
            current_moves_ids = [x.id for x in current_moves]
            move_ids = move_obj.search(cr, uid, [
                    ('id', 'in', current_moves_ids),
                    ('prodlot_id', '=', prodlot_id),
                ], limit=1, context=context)
            if move_ids:
                move = move_obj.read(cr, uid, move_ids[0], ['product_qty'], context=context)
                value = {'quantity': move['product_qty'], 'move_id': move_ids[0]}
        return {'value': value}
    
    _defaults = {
        'quantity': 1.0,
        'pack_id': lambda self, cr, uid, context: context.get('active_id', False),
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: