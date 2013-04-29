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
import time

class stock_tracking(orm.Model):
    
    _inherit = 'stock.tracking'

    _columns = {
        'previous_id': fields.many2one('stock.tracking', 'Previous Pack', readonly=True),
        'modified': fields.boolean('Modified'),
    }
    
    _defaults = {
        'modified': False,
    }   
    '''Function for pack creation'''    
    def _create_pack(self, cr, uid, pack_id, context=None):        
        '''Init'''
        if context == None:
            context = {}            
        '''Location determination'''
        stock_tracking_data = self.browse(cr, uid, pack_id, context=context)
        '''Pack Creation'''
        tracking_id = self.create(cr, uid, {
            'ul_id': stock_tracking_data.ul_id.id,
            'location_id': stock_tracking_data.location_id.id
        }, context=context)        
        '''Pack name is returned'''
        return tracking_id
    
    def reset_open(self, cr, uid, ids, context=None):
        res = super(stock_tracking, self).reset_open(cr, uid, ids, context=context)
        history_obj = self.pool.get('stock.tracking.history')
        pack_ids = self.browse(cr, uid, ids, context=context)
        for pack in pack_ids:                        
            if pack.state == 'open':
                history_obj.create(cr, uid, {
                        'type': 'reopen',
                        'previous_ref': pack.name,
                        'tracking_id': pack.id
                    }, context=context)
        return True

    #TODO: check this method !!
    def set_close(self, cr, uid, ids, context=None):
        
        stock_move_obj = self.pool.get('stock.move')
        history_obj = self.pool.get('stock.tracking.history')
        res = super(stock_tracking, self).set_close(cr, uid, ids, context=context)
        if res:
            pack_ids = self.browse(cr, uid, ids, context=context)
            for pack in pack_ids:
                if pack.state == 'open':                
                    if history_obj.search(cr, uid, [
                            ('type', '=', 'reopen'),
                            ('tracking_id', '=', pack.id)
                        ], context=context) and pack.modified == True:           
                        new_pack_id = self._create_pack(cr, uid, pack.id, context=context)
                        new_pack_data = self.browse(cr, uid, new_pack_id, context=context)
                        '''loop on each move form the old pack to the new pack'''
                        for pack_move in pack.current_move_ids:
                            '''stock move creation'''
                            move_id = stock_move_obj.create(cr, uid, {
                                      'name': pack_move.name,
                                      'state': pack_move.state,
                                      'product_id': pack_move.product_id.id,
                                      'product_uom': pack_move.product_uom.id,
                                      'prodlot_id': pack_move.prodlot_id.id,
                                      'location_id': pack.location_id.id,
                                      'location_dest_id': new_pack_data.location_id.id,
                                      'tracking_id': new_pack_data.id,
                                  }, context=context)                            
                        '''end of loop''' 
                        if pack.child_ids:
                            for child_pack_data in pack.child_ids:
                                if child_pack_data.state == 'close':   
                                    self.write(cr, uid, child_pack_data.id, {'active': False}, context=context)                                                          
                                    self.write(cr, uid, [new_child_pack_id], {'parent_id': new_pack_data.id,}, context=context)
                                    history_obj.create(cr, uid, {
                                            'type': 'pack_in',
                                            'tracking_id': child_pack_data.id,
                                            'parent_id': new_pack_data.id,
                                        }, context=context)
                                    self.write(cr, uid, new_pack_data.id, {
                                            'location_id': child_pack_data.location_id and child_pack_data.location_id.id or False,
                                        }, context=context)
                        
                        self.write(cr, uid, [pack.id], {
                                'state': 'close',
                                'active': False,
                                'modified': False,
                            }, context=context)
                        '''Call for a function who will display serial code list and product list in the pack layout'''                                                
                        self.get_products(cr, uid, [new_pack_data.id], context=context)
                        self.get_serials(cr, uid, [new_pack_data.id], context=context)
                    self.write(cr, uid, [pack.id], {'state': 'close'}, context=context)
        return res

class stock_tracking_history(orm.Model):
    
    _inherit = "stock.tracking.history"
    
    def _get_types(self, cr, uid, context={}):
        res = super(stock_tracking_history, self)._get_types(cr, uid, context=context)
        if not res:
            res = []
        res = res + [('reopen',_('Re Open'))]
        return res
    
    _columns = {
        'type': fields.selection(_get_types, 'Type'),
        'previous_ref': fields.char('Previous reference', size=128),        
#        'previous_id': fields.many2one('stock.tracking', 'Previous pack'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
