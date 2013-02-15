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
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class stock_packaging_add(osv.osv_memory):

    _inherit = "stock.packaging.add"
    
    _columns = {
        'prodlot_ids': fields.one2many('stock.packaging.add.line', 'parent_id', 'Lines'),
    }
    
    def _get_move_prodlot_vals(self, cr, uid, current, prodlot_line, move_data=False, context=None):
        if context == None:
            context = {}
        pack = current.pack_id
        vals = {
            'name': move_data and move_data.name or prodlot_line.prodlot_id.name,
            'state': 'done',
            'product_id': move_data and move_data.prodlot_id.product_id.id or prodlot_line.prodlot_id.product_id.id,
            'product_uom': move_data and move_data.product_uom.id or prodlot_line.prodlot_id.product_id.uom_id.id,
            'prodlot_id': move_data and move_data.prodlot_id.id or prodlot_line.prodlot_id.id,
            'location_id': move_data and move_data.location_dest_id.id or pack.location_id.id,
            'location_dest_id': pack.location_id.id,
            'tracking_id': pack.id,
            'product_qty': prodlot_line.quantity,
        }
        return vals
    
    def _add_prodlots(self, cr, uid, current, context=None):
        if context == None:
            context = {}
        tracking_obj = self.pool.get('stock.tracking')
        move_obj = self.pool.get('stock.move')
        pack = current.pack_id
        modified = False
        for prodlot_line in current.prodlot_ids:
            move_ids = move_obj.search(cr, uid, [
                            ('state', '=', 'done'),
                            ('prodlot_id', '=', prodlot_line.prodlot_id.id),
                        ], order='date desc', limit=1, context=context)
            vals = {}
            if move_ids:
                move_data = move_obj.browse(cr, uid, move_ids[0], context=context)
                vals = self._get_move_prodlot_vals(cr, uid, current, prodlot_line, move_data=move_data, context=context)
            else:
                vals = self._get_move_prodlot_vals(cr, uid, current, prodlot_line, move_data=False, context=context)
            if vals:
                new_move_id = move_obj.create(cr, uid, vals, context=context)
                modified = True
        if modified:
            tracking_obj.write(cr, uid, pack.id, {'modified': True}, context=context)
        tracking_obj.get_products(cr, uid, [pack.id], context=context)
        tracking_obj.get_serials(cr, uid, [pack.id], context=context)
        return True
    
    def add_object(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        obj_model = self.pool.get('ir.model.data')
        move_obj = self.pool.get('stock.move')
        res = super(stock_packaging_add, self).add_object(cr, uid, ids, context=context)
        for current in self.browse(cr, uid, ids, context=context):
            type = current.type_id.code
            if type == 'prodlots':
                self._add_prodlots(cr, uid, current, context=context)
        return res
       
stock_packaging_add()

class stock_packaging_add_line(osv.osv_memory):

    _inherit = "stock.packaging.add.line"
    
    _columns = {
        'prodlot_id': fields.many2one('stock.production.lot', 'Production lot', domain="[('tracking_id','=',False)]"),
    }

stock_packaging_add_line()

#class stock_prodlot_validate(osv.osv_memory):
#    _name = "stock.prodlot.validate"
#    
#    def validate(self, cr, uid, ids, context=None):
#        move_obj = self.pool.get('stock.move')
#        tracking_obj = self.pool.get('stock.tracking')
#        add_obj = self.pool.get('stock.packaging.add')
#        line_obj = self.pool.get('stock.packaging.add.line')
#        if context is None:
#            context = {}
#            
#        current = add_obj.browse(cr, uid, context.get('current_id'), context=context)
#        move_data = move_obj.browse(cr, uid, context.get('move_id'), context=context)
#        prodlot_line = line_obj.browse(cr, uid, context.get('prodlot_line_id'), context=context)
#        vals = add_obj._get_move_prodlot_vals(cr, uid, current=current, prodlot_line=prodlot_line, move_data=move_data, context=context)
#        
#        move_obj.write(cr, uid, move_data.id, {'tracking_id':False}, context=context)
#        new_move_id = move_obj.create(cr, uid, vals, context=context)
#        
#        tracking_obj.write(cr, uid, current.pack_id.id, {'modified': True}, context=context)
#        tracking_obj.get_products(cr, uid, [current.pack_id.id], context=context)
#        tracking_obj.get_serials(cr, uid, [current.pack_id.id], context=context)
#        return {'type': 'ir.actions.act_window_close'}
#    
#stock_prodlot_validate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: