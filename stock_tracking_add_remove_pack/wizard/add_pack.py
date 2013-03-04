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

class stock_packaging_add(orm.TransientModel):

    _inherit = "stock.packaging.add"

    _columns = {
        'location_id': fields.many2one('stock.location', 'Location'),
        'pack_ids': fields.many2many('stock.tracking', 'add_pack_child_rel', 'wizard_id', 'pack_id', 'Packs', domain=[('parent_id', '=', False),('state', '=', 'close')]),
    }
    
    def _get_location_id(self, cr, uid, context):
        if context==None:
            context={}
        location_id = False
        active_id = context.get('active_id')
        if active_id:
            tracking_obj = self.pool.get('stock.tracking')
            tracking = tracking_obj.browse(cr, uid, active_id, context=context)
            location_id = tracking.location_id and tracking.location_id.id or False
        return location_id
    
    _defaults = {
        'location_id': lambda self, cr, uid, context: self._get_location_id(cr, uid, context),
    }
    
    def add_object(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        tracking_obj = self.pool.get('stock.tracking')
        res = super(stock_packaging_add, self).add_object(cr, uid, ids, context=context)
        for current in self.browse(cr, uid, ids, context=context):
            code_type = current.type_id.code
            pack_id = current.pack_id.id
            child_ids = [x.id for x in current.pack_ids]
            if code_type == 'pack':
                tracking_obj._add_pack(cr, uid, pack_id, child_ids, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: