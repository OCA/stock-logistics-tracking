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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import time

class stock_tracking(orm.Model):
    _inherit = 'stock.tracking'
    
    def _get_move_product_vals(self, cr, uid, pack_id, product, qty=False, move_data=False, context=None):
        if context is None:
            context = {}
        pack = self.browse(cr, uid, pack_id, context=context)
        vals = {
            'name':  product.name,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_qty': qty,
            'location_id': pack.location_id.id,
            'location_dest_id': pack.location_id.id,
            'tracking_id': pack.id,
            'state': 'done',
        }
        return vals
    
    def _add_products(self, cr, uid, pack_id, product_ids, quantities=False, context=None):
        """ Method to add products into a pack """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        prod_obj = self.pool.get('product.product')
        pack_obj = self.pool.get('stock.tracking')
        history_obj = self.pool.get('stock.tracking.history')
        pack = pack_obj.browse(cr, uid, pack_id, context=context)
        date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        # Process #
        for product in prod_obj.browse(cr, uid, product_ids, context=context):
            # If quantity is not define , 1 by default #
            qty = 1.0
            if quantities and quantities[product.id]:
                qty = quantities[product.id]
            vals = {}
            vals = self._get_move_product_vals(cr, uid, pack_id, product, qty, move_data=False, context=context)
            if vals:
                new_move_id = move_obj.create(cr, uid, vals, context=context)
                hist_id = history_obj.create(cr, uid, {
                       'tracking_id': pack.id,
                       'type': 'add_product',
                       'location_id': pack.location_id.id,
                       'location_dest_id': pack.location_id.id,
                       'product_id': product.id,
                       'qty': qty,
                       'date' : date,
                    }, context=context)
        self.get_products(cr, uid, [pack.id], context=context)
        return True
    
    def _get_move_prodlot_vals(self, cr, uid, pack_id, prodlot_data, qty=False, move_data=False, context=None):
        if context is None:
            context = {}
        pack = self.browse(cr, uid, pack_id, context=context)
        vals = {
            'name': move_data.name if move_data else prodlot_data.name,
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
    
    def _add_prodlots(self, cr, uid, pack_id, prodlot_ids, quantities=False, context=None):
        """ Method to add prodlots into a pack """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        prodlot_obj = self.pool.get('stock.production.lot')
        pack_obj = self.pool.get('stock.tracking')
        history_obj = self.pool.get('stock.tracking.history')
        pack = pack_obj.browse(cr, uid, pack_id, context=context)
        date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        modified = False
        for prodlot_data in prodlot_obj.browse(cr, uid, prodlot_ids, context=context):
            if quantities and quantities[prodlot_data.id]:
                qty = quantities[prodlot_data.id]
            move_ids = move_obj.search(cr, uid, [
                            ('state', '=', 'done'),
                            ('prodlot_id', '=', prodlot_data.id),
                        ], order='date desc', limit=1, context=context)
            vals = {}
            if move_ids:
                move_data = move_obj.browse(cr, uid, move_ids[0], context=context)
                vals = self._get_move_prodlot_vals(cr, uid, pack_id,
                            prodlot_data, qty, move_data=move_data, context=context)
            else:
                vals = self._get_move_prodlot_vals(cr, uid, pack_id,
                            prodlot_data, qty, move_data=False, context=context)
            if vals:
                new_move_id = move_obj.create(cr, uid, vals, context=context)
                hist_id = history_obj.create(cr, uid, {
                       'tracking_id': pack.id,
                       'type': 'add_prodlot',
                       'location_id': pack.location_id.id,
                       'location_dest_id': pack.location_id.id,
                       'prodlot_id': prodlot_data.id,
                       'qty': qty,
                       'date' : date,
                    }, context=context)
        self.get_products(cr, uid, [pack_id], context=context)
        self.get_serials(cr, uid, [pack_id], context=context)
        return True

    
    def _remove_products(self, cr, uid, pack_id, products, context=None):
        """ Method to remove products from a pack """
        # Initialization #
        move_obj = self.pool.get('stock.move')
        history_obj = self.pool.get('stock.tracking.history')
        prod_obj = self.pool.get('product.product')
        date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if context is None:
            context = {}

        pack = self.browse(cr, uid, pack_id, context=context)
        for product in products:
            if not product.move_id:
                continue
            move_data = product.move_id
            move_qty = move_data.product_qty
            remove_qty = product.quantity
            if not remove_qty:
                continue
            
            #if the quantity to remove is bigger than the move quantity we only remove the move value
            if move_qty < remove_qty:
                remove_qty = move_qty

            # Process #
            hist_id = history_obj.create(cr, uid, {
                   'tracking_id': pack.id,
                   'type': 'remove_product',
                   'location_id': pack.location_id.id,
                   'location_dest_id': pack.location_id.id,
                   'product_id': product.product_id.id,
                   'qty': remove_qty,
                   'date' : date,
                }, context=context)
            if remove_qty != move_qty:
                defaults = {
                    'location_id': pack.location_id.id,
                    'location_dest_id': pack.location_id.id,
                    'date': date,
                    'date_expected': date,
                    'tracking_id': pack.id,
                    'product_id': product.product_id.id,
                    'product_qty': move_qty - remove_qty,
                    'state': 'done',
                }
                new_id = move_obj.copy(cr, uid, move_data.id, default=defaults, context=context)
            defaults = {
                'location_id': pack.location_id.id,
                'location_dest_id': pack.location_id.id,
                'date': date,
                'date_expected': date,
                'tracking_id': False,
                'product_qty': remove_qty,
                'state': 'done',
            }
            move_obj.copy(cr, uid, move_data.id, default=defaults, context=context)
            move_obj.write(cr, uid, [move_data.id], {'pack_history_id': hist_id}, context=context)
        self.get_products(cr, uid, [pack.id], context=context)
        return True

    def _remove_prodlot(self, cr, uid, pack_id, prodlots, context=None):
        """ Method to remove prodlots from a pack """
        # Initialization #
        move_obj = self.pool.get('stock.move')
        history_obj = self.pool.get('stock.tracking.history')
        prodlot_obj = self.pool.get('stock.production.lot')
        product_obj = self.pool.get('product.product')
        date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if context is None:
            context = {}
            
        pack = self.browse(cr, uid, pack_id, context=context)
        for prodlot in prodlots:
            if not prodlot.move_id:
                continue
            move_data = prodlot.move_id
            move_qty = move_data.product_qty
            remove_qty = prodlot.quantity
            if not remove_qty:
                continue
            
            #if the quantity to remove is bigger than the move quantity we only remove the move value
            if move_qty < remove_qty:
                remove_qty = move_qty
        
            # Process #
            hist_id = history_obj.create(cr, uid, {
               'tracking_id': pack.id,
               'type': 'remove_prodlot',
               'location_id': pack.location_id.id,
               'location_dest_id': pack.location_id.id,
               'prodlot_id': prodlot.prodlot_id.id,
               'qty': remove_qty,
               'date' : date,
            }, context=context)
            if remove_qty != move_qty:
                defaults = {
                    'location_id': pack.location_id.id,
                    'location_dest_id': pack.location_id.id,
                    'date': date,
                    'date_expected': date,
                    'tracking_id': pack.id,
                    'product_id': prodlot.prodlot_id.product_id.id,
                    'product_qty': move_qty - remove_qty,
                    'state': 'done',
                }
                new_id = move_obj.copy(cr, uid, move_data.id, default=defaults, context=context)
            defaults = {
                'location_id': pack.location_id.id,
                'location_dest_id': pack.location_id.id,
                'date': date,
                'date_expected': date,
                'tracking_id': False,
                'product_qty': remove_qty,
                'state': 'done',
            }
            move_obj.copy(cr, uid, move_data.id, default=defaults, context=context)
            move_obj.write(cr, uid, [move_data.id], {'pack_history_id': hist_id}, context=context)
        self.get_serials(cr, uid, [pack.id], context=context)
        self.get_products(cr, uid, [pack.id], context=context)
        return True

class stock_tracking_history(osv.osv):
    
    _inherit = "stock.tracking.history"
    
    def _get_types(self, cr, uid, context={}):
        res = super(stock_tracking_history, self)._get_types(cr, uid, context)
        if not res:
            res = []
        res = res + [('add_product',_('Add product')),('remove_product',_('Remove product')),
                     ('add_prodlot',_('Add prodlot')),('remove_prodlot',_('Remove prodlot'))]
        return res
    
    _columns = {
        'type': fields.selection(_get_types, 'Type'),
        'product_id': fields.many2one('product.product', 'Product'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Production lot'),
        'qty': fields.float('Quantity'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
