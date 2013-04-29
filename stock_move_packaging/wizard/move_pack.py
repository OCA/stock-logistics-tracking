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

class stock_move_packaging(orm.TransientModel):

    _name = "stock.move.packaging"
    
    _columns = {
        'pack_id': fields.many2one('stock.tracking', 'Pack to move', required=True),
        'location_dest_id': fields.many2one('stock.location', 'Destination location', required=True),
    }
    
    _defaults = {
        'pack_id': lambda s,cr,uid,c: c.get('active_id') or False,
    }
    
    def move_pack(self, cr, uid, ids, context=None):
        barcode_obj = self.pool.get('tr.barcode')
        tracking_obj = self.pool.get('stock.tracking')
        move_obj = self.pool.get('stock.move')
        history_obj = self.pool.get('stock.tracking.history')
        picking_obj = self.pool.get('stock.picking')
        
        if context == None:
            context = {}
            
        context.update({'from_pack':True})
        for obj in self.browse(cr, uid, ids, context=context):
            pack = obj.pack_id
            if not pack or not obj.location_dest_id:
                continue
            """
            This is related to the module stock_tracking_child
            TODO: remove this from this method to be able to install it without stock_tracking_child
            """
            if pack.parent_id:
                raise osv.except_osv(_('Warning!'),_('You cannot move this pack because it\'s inside of an other pack: %s.') % (pack.parent_id.name))
            for child in pack.child_ids:
                """
                This is related to the module stock_tracking_state
                TODO: remove this from this method to be able to install it without stock_tracking_state
                """
                if child.state != 'close':
                    raise osv.except_osv(_('Warning!'),_('You cannot move this pack because there is a none closed pack inside of it: %s.') % (child.name))
            current_type = pack.location_id.usage
            dest_type = obj.location_dest_id.usage
            
            pick_type = 'out'
            if type == 'internal':
                pick_type = 'internal'
            elif type == 'supplier':
                pick_type = 'in'
            elif type == 'customer':
                pick_type = 'out'
            date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            pick_id = picking_obj.create(cr, uid, {
                    'type': pick_type,
                    'auto_picking': 'draft',
                    'company_id': self.pool.get('res.company')._company_default_get(cr, uid, 'stock.company', context=context),
                    'address_id': obj.location_dest_id.address_id and obj.location_dest_id.address_id.id or False,
                    'invoice_state': 'none',
                    'date': date,
                    'state': 'done',
                }, context=context)
                        
            child_packs = tracking_obj.hierarchy_ids(pack)
            for child_pack in child_packs:
                hist_id = history_obj.create(cr, uid, {
                       'tracking_id': child_pack.id,
                       'type': 'move',
                       'location_id': child_pack.location_id.id,
                       'location_dest_id': obj.location_dest_id.id,
                   }, context=context)
                
                for move in child_pack.current_move_ids:
                    defaults = {
                        'location_id': move.location_dest_id.id,
                        'location_dest_id': obj.location_dest_id.id,
                        'picking_id': pick_id,
                        'state': 'done',
                        'date': date,
                        'date_expected': date,
                    }
                    new_id = move_obj.copy(cr, uid, move.id, default=defaults, context=context)
                    move_obj.write(cr, uid, [move.id], {'pack_history_id': hist_id, 'move_dest_id': new_id}, context=context)
                tracking_obj.write(cr, uid, [child_pack.id], {'location_id': obj.location_dest_id.id}, context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: