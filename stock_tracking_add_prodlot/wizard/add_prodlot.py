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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class stock_packaging_add(orm.TransientModel):

    _inherit = "stock.packaging.add"
    
    _columns = {
        'prodlot_ids': fields.one2many('stock.packaging.add.line', 'parent_id', 'Lines'),
    }
    
    
    def add_object(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        tracking_obj = self.pool.get('stock.tracking')    
        obj_model = self.pool.get('ir.model.data')
        move_obj = self.pool.get('stock.move')
        res = super(stock_packaging_add, self).add_object(cr, uid, ids, context=context)
        for current in self.browse(cr, uid, ids, context=context):
            type = current.type_id.code
            pack_id = current.pack_id.id
            quantities = {}
            prodlot_ids = []
            if type == 'prodlot':
                for line_data in current.prodlot_ids:
                    # For each product added, we appends at the product_ids list the quantity added #
                    prodlot_ids.append(line_data.prodlot_id.id)
                    quantities[line_data.prodlot_id.id]=line_data.quantity
                tracking_obj.add_prodlots(cr, uid, pack_id, prodlot_ids, quantities, context=context)
        return res

class stock_packaging_add_line(orm.TransientModel):

    _inherit = "stock.packaging.add.line"
    
    _columns = {
        'prodlot_id': fields.many2one('stock.production.lot', 'Production lot', domain="[('tracking_id','=',False)]"),
    }

#class stock_prodlot_validate(orm.TransientModel):
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: