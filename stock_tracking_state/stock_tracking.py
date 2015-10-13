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

class stock_tracking(orm.Model):

    _inherit = 'stock.tracking'
    
    _columns = { 
        'state': fields.selection([('open','Open'),('close','Close')], 'State', required=True, readonly=True),
        'parent_id': fields.many2one('stock.tracking', 'Parent'),
        'child_ids': fields.one2many('stock.tracking', 'parent_id', 'Children', readonly=True),
    }

    _defaults = {
        'state': 'open',
    }
    
    def reset_open(self, cr, uid, ids, context=None):
        pack_ids = self.browse(cr, uid, ids, context=context)
        for pack in pack_ids:
            allowed = True
            if pack.parent_id:
                if pack.parent_id and pack.parent_id != 'open':
                    self.write(cr, uid, [pack.parent_id.id], {'state': 'open'}, context=context)
            if allowed:
                for child in pack.child_ids:
                    if child.state == 'open':
                        allowed = False
                        raise osv.except_osv(_('Not allowed !'),_('You can\'t re-open this pack because there is at least one not closed child'))
                        break
            if allowed:
                self.write(cr, uid, [pack.id], {'state': 'open'}, context=context)
        return True

    def set_close(self, cr, uid, ids, context=None):
        pack_ids = self.browse(cr, uid, ids, context=context)
        for pack in pack_ids:
            allowed = True
            for child in pack.child_ids:
                if child.state == 'open':
                    allowed = False
                    raise osv.except_osv(_('Not allowed !'),_('You can\'t close this pack because there is at least one not closed child'))
                    break
            if allowed:
                self.write(cr, uid, [pack.id], {'state': 'close'}, context=context)
        return True

class stock_move(orm.Model):
    _inherit = 'stock.move'
    
    def _check_tracking_state(self, cr, uid, ids, context=None):
        lines = self.browse(cr, uid, ids, context=context)
        for l in lines:
            if l.tracking_id.state == 'close':
                return False
        return True
    
    _constraints = [
        (_check_tracking_state, 'You cannot choose this pack because it\'s closed.', ['tracking_id']),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
