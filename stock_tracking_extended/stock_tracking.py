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

class one2many_special(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if context is None:
            context = {}
        if self._context:
            context = context.copy()
        context.update(self._context)
        if values is None:
            values = {}

        res = {}
        location_ids = []
        for id in ids:
            res[id] = []
            location_id = obj.read(cr, user, id, ['location_id'], context=context)['location_id']
            if isinstance(location_id, (list,tuple)):
                location_id = location_id and location_id[0] or False
            if location_id and (location_id not in location_ids):
                location_ids.append(location_id)
        domain = self._domain(obj) if callable(self._domain) else self._domain
        domain2 = [(self._fields_id, 'in', ids)]
        if location_ids:
            domain2 += [('location_dest_id', 'in', location_ids)]
        ids2 = obj.pool.get(self._obj).search(cr, user, domain + domain2, limit=self._limit, context=context)
        for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
            if r[self._fields_id] in res:
                res[r[self._fields_id]].append(r['id'])
        return res

class stock_tracking(orm.Model):
    _inherit = 'stock.tracking'
    
    def _get_default_location(self, cr, uid, context=None):
        """ By default we get the location defined on the main warehouse of the user's company """
        # Initialization #
        if context is None:
            context = {}
        if context.get('location_id'):
            return context.get('location_id')
        location_id = False
        warehouse_obj = self.pool.get('stock.warehouse')
        user_obj = self.pool.get('res.users')
        # Process #
        user_data = user_obj.browse(cr, uid, uid, context=context)
        warehouse_ids = warehouse_obj.search(cr, uid, [
                ('company_id', '=', user_data.company_id.id),
            ], limit=1, context=context)
        if warehouse_ids:
            warehouse = warehouse_obj.browse(cr, uid, warehouse_ids[0], context=context)
            location_id = warehouse.lot_stock_id and warehouse.lot_stock_id.id or False
        return location_id 

    _columns = {
        'location_id': fields.many2one('stock.location', 'Location', readonly=True),
        'product_ids': fields.one2many('product.stock.tracking', 'tracking_id', 'Products', readonly=True),
        'history_ids': fields.one2many('stock.tracking.history', 'tracking_id', 'History', readonly=True),
        'current_move_ids': one2many_special('stock.move', 'tracking_id', 'Current moves', domain=[('pack_history_id', '=', False)], readonly=True),
        'date': fields.datetime('Creation Date', required=True, readonly=True),
        'serial_ids': fields.one2many('serial.stock.tracking', 'tracking_id', 'Products', readonly=True),
    }
    
    _defaults = {
        'location_id': lambda self, cr, uid, context: self._get_default_location(cr, uid, context),
    }
    
    def get_products_process(self, cr, uid, pack_ids, context=None):
        stock_track = self.pool.get('product.stock.tracking')
        for pack in pack_ids:
            product_ids = [x.id for x in pack.product_ids]
            stock_track.unlink(cr, uid, product_ids, context=context)
            product_list = {}
            for x in pack.current_move_ids:
                if x.location_dest_id.id == pack.location_id.id:
                    product_list.setdefault(x.product_id.id, 0)
                    product_list[x.product_id.id] += x.product_qty
            for product in product_list.iterkeys():
                stock_track.create(cr, uid, {
                        'product_id': product,
                        'quantity': product_list[product],
                        'tracking_id': pack.id
                    }, context=context)
        return True

    def get_serial_process(self, cr, uid, pack_ids, context=None):
        serial_track = self.pool.get('serial.stock.tracking')
        serial_obj = self.pool.get('stock.production.lot')
        for pack in pack_ids:
            serial_ids = [x.id for x in child.serial_ids]
            serial_track.unlink(cr, uid, serial_ids)
            serial_list = {}
            for x in child.current_move_ids:
                if x.location_dest_id.id == pack.location_id.id:
                    serial_list.setdefault(x.prodlot_id.id, 0)
                    serial_list[x.prodlot_id.id] += x.product_qty
            for serial in serial_list.keys():
                if serial:
                    serial_track.create(cr, uid, {
                            'serial_id': serial,
                            'quantity': serial_list[serial],
                            'tracking_id': pack.id
                        }, context=context)
                    serial_obj.write(cr, uid, [serial], {'tracking_id': pack.id}, context=context)
        return True

    def get_products(self, cr, uid, ids, context=None):
        pack_ids = self.browse(cr, uid, ids, context)
        return self.get_products_process(cr, uid, pack_ids, context=context)

    def get_serial(self, cr, uid, ids, context=None):
        pack_ids = self.browse(cr, uid, ids, context)
        return self.get_serial(cr, uid, pack_ids, context=context)

class product_stock_tracking(orm.Model):

    _name = 'product.stock.tracking'
    _description = 'Products in Packs'

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'quantity': fields.float('Quantity'),
        'tracking_id': fields.many2one('stock.tracking', 'Tracking'),
    }

class serial_stock_tracking(orm.Model):

    _name = 'serial.stock.tracking'
    _description = 'Serials in Packs'

    _order = 'tracking_id,serial_id'

    _columns = {
        'serial_id': fields.many2one('stock.production.lot', 'Serial'),
        'product_id': fields.related('serial_id', 'product_id', type='many2one', relation='product.product', string='Product'),
        'quantity': fields.float('Quantity'),
        'tracking_id': fields.many2one('stock.tracking', 'Tracking'),
    }

class stock_tracking_history(orm.Model):

    _name = "stock.tracking.history"
    _description = 'Packs history'

    def _get_types(self, cr, uid, context=None):
        res = []
        return res

    _columns = {
        'tracking_id': fields.many2one('stock.tracking', 'Pack', required=True),
        'type': fields.selection(_get_types, 'Type'),
        'date': fields.datetime('Creation Date', readonly=True),
    }

    _rec_name = "tracking_id"

class stock_move(orm.Model):
    _inherit = 'stock.move'
    _columns = {
        'pack_history_id': fields.many2one('stock.tracking.history', 'Pack history'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
