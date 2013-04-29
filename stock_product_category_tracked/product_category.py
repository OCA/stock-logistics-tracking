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

class product_category(orm.Model):
    _inherit = 'product.category'
    _columns = {
        'track_incoming': fields.boolean('Track Incoming Lots',
            help="Forces to specify a Serial Number for all moves "
                "containing this product and coming from a Supplier Location"),
        'track_outgoing': fields.boolean('Track Outgoing Lots',
            help="Forces to specify a Serial Number for all moves containing "
                "this product and going to a Customer Location"),
    }

class product_category(orm.Model):
    
    _inherit = 'product.product'
    
    def onchange_category(self, cr, uid, ids, category_id, context=None):
        if category_id:
            categ = self.pool.get('product.category').browse(cr, uid, category_id, context=context)
            return {'value': {
                'track_incoming': categ and categ.track_incoming or False,
                'track_outgoing': categ and categ.track_outgoing or False,
                }
            }
        return {}
            
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
