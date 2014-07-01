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

class stock_packaging_swap(orm.TransientModel):
    _name = "stock.packaging.swap"
    _description = "Child pack Swap"

    _columns = {
        'location_id': fields.many2one('stock.location', 'Location'),
        'parent_pack_id': fields.many2one('stock.tracking', 'Parent Pack'),
        'previous_pack_id': fields.many2one('stock.tracking', 'Previous Pack'),
        'new_pack_id': fields.many2one('stock.tracking', 'New Pack'),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        res=super(stock_packaging_swap, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context={}                                                                      
        res.update({
            'parent_pack_id': context.get('active_id', False)
        })
        return res
    
    def swap_object(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        tracking_obj = self.pool.get('stock.tracking')
        history_obj = self.pool.get('stock.tracking.history')
        sequence_obj = self.pool.get('ir.sequence')
        company_obj = self.pool.get('res.company')
        if context is None:
            context = {}
        for current in self.browse(cr, uid, ids, context=context):
            active_id = context.get('active_id')
            if not active_id:
                raise osv.except_osv(_('Warning!'),_('Should Not Happen !'))
            parent_pack = tracking_obj.browse(cr, uid, active_id, context=context)
            origin_id = parent_pack.location_id.id
            destination_id = current.location_id.id
            date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            pick_id = picking_obj.create(cr, uid, {
                'type': 'internal',
                'auto_picking': True,
                'name': sequence_obj.next_by_code(cr, uid, 'stock.picking.internal'),
                'company_id': company_obj._company_default_get(cr, uid, 'stock.company', context=context),
                'address_id': current.location_id.partner_id and current.location_id.partner_id.id or False,
                'invoice_state': 'none',
                'date': date,
                'state': 'done',
            }, context=context)
            # Previous pack
            tracking_obj.write(cr, uid, current.previous_pack_id.id, {
                    'location_id': destination_id,
                    'parent_id': False
                }, context=context)
            child_packs = tracking_obj.hierarchy_ids(current.previous_pack_id)
            for child_data in child_packs:
                hist_id = history_obj.create(cr, uid, {
                   'tracking_id': child_data.id,
                   'type': 'swap',
                   'location_id': origin_id,
                   'location_dest_id': destination_id,
                   'swap_child_pack_id': current.previous_pack_id.id,
                   'child_pack_id': current.new_pack_id.id,
               }, context=context)
                tracking_obj.write(cr, uid, child_data.id, {
                        'location_id': destination_id
                    }, context=context)
                move_ids = child_data.current_move_ids
                for move in move_ids:
                    defaults = {
                        'location_id': origin_id,
                        'location_dest_id': destination_id,
                        'picking_id': pick_id,
                        'date': date,
                        'date_expected': date,
                        'state': 'done',
                    }
                    new_id = move_obj.copy(cr, uid, move.id, default=defaults, context=context)
                    move_obj.write(cr, uid, [move.id], {
                            'pack_history_id': hist_id
                        }, context=context)
            
            # New pack
            tracking_obj.write(cr, uid, current.new_pack_id.id, {
                    'location_id': origin_id,
                    'parent_id': active_id
                }, context=context)
            child_packs = tracking_obj.hierarchy_ids(current.new_pack_id)
            for child_data in child_packs:
                hist_id = history_obj.create(cr, uid, {
                   'tracking_id': child_data.id,
                   'type': 'swap_pack',
                   'location_id': destination_id,
                   'location_dest_id': origin_id,
                   'swap_child_pack_id': current.new_pack_id.id,
                   'child_pack_id': current.previous_pack_id.id,
                   'qty' : 1,
               }, context=context)
                tracking_obj.write(cr, uid, child_data.id, {
                        'location_id': origin_id
                    }, context=context)
                move_ids = child_data.current_move_ids
                for move in move_ids:
                    defaults = {
                        'location_id': destination_id,
                        'location_dest_id': origin_id,
                        'picking_id': pick_id,
                        'date': date,
                        'date_expected': date,
                        'state': 'done',
                    }
                    new_id = move_obj.copy(cr, uid, move.id, default=defaults, context=context)
                    move_obj.write(cr, uid, [move.id], {'pack_history_id': hist_id}, context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: