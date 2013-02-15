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

class stock_packaging_add_type(osv.osv):
    _name = 'stock.packaging.add.type'
    
    _columns = {
        'code': fields.char('Code', size=64),
        'name': fields.char('Name', size=64),
    }
    
stock_packaging_add_type()

class stock_packaging_add(osv.osv_memory):

    _name = "stock.packaging.add"
    _description = "Add objects to a pack"
    
    _columns = {
        'product_ids': fields.one2many('stock.packaging.add.line', 'parent_id', 'Lines'),
        'type_id': fields.many2one('stock.packaging.add.type', 'Type', required=True),
        'type': fields.char('Type', size=64),
        'pack_id': fields.many2one('stock.tracking', 'Pack to move', required=True),
    }

    def _get_type_id(self, cr, uid, context):
        if context==None:
            context={}
        if context.get('type_selection'):
            type = context.get('type_selection')
        else:
            type = 'product'
        type_obj = self.pool.get('stock.packaging.add.type')
        default_type = type_obj.search(cr, uid, [('code', '=', type)], limit=1, context=context)
        if not default_type:
            default_type = type_obj.search(cr, uid, [], limit=1, context=context)
        return default_type and default_type[0] or False

    def _get_type(self, cr, uid, context):
        if context==None:
            context={}
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
    
    def onchange_type_id(self, cr, uid, ids, type_id):
        res = {'value': {'type': ''}}
        if type_id:
            type_obj = self.pool.get('stock.packaging.add.type')
            type = type_obj.read(cr, uid, type_id, ['code'])
            if type['code']:
                res = {'value': {'type': type['code']}}
        return res
    
    def _add_products(self, cr, uid, current, context=None):
        if context == None:
            context = {}
        tracking_obj = self.pool.get('stock.tracking')
        move_obj = self.pool.get('stock.move')
        pack = current.pack_id
        for product_line in current.product_ids:
            move_id = move_obj.create(cr, uid, {
                  'name': product_line.product_id.name,
                  'product_id': product_line.product_id.id,
                  'product_uom': product_line.product_id.uom_id.id,
                  'product_qty': product_line.quantity,
                  'location_id': pack.location_id.id,
                  'location_dest_id': pack.location_id.id,
                  'tracking_id': pack.id,
                  'state': 'done',
            }, context=context)
        tracking_obj.write(cr, uid, pack.id, {'modified': True}, context=context)
        tracking_obj.get_products(cr, uid, [pack.id], context=context)
        return True
    
    def add_object(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        for current in self.browse(cr, uid, ids, context=context):
            type = current.type_id.code
            if type == 'product':
                self._add_products(cr, uid, current, context=context)
        return {'type': 'ir.actions.act_window_close'}
       
stock_packaging_add()

class stock_packaging_add_line(osv.osv_memory):

    _name = "stock.packaging.add.line"
    _description = "Add object to a pack"
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', domain="[('type', '!=', 'service'),('track_outgoing', '=', False)]"),
        'parent_id': fields.many2one('stock.packaging.add', 'Parent'),
        'location_id': fields.many2one('stock.location', 'Location'),
        'quantity': fields.float('Quantity', required=True),
    }
    
    _defaults = {
        'quantity': 1.0,
    }
            
stock_packaging_add_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: