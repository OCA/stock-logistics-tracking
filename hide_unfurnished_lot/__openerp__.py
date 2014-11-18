# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Hide Unfurnished Lot',
    'version': '0.1',
    'author': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'category': 'Warehouse',
    'description': """
Hide Unfurnished Lot
====================

This module hide lot number with no quantity available on Delivery Order view.

Contributors
------------

* Pierre Lamarche (pierre.lamarche@savoirfairelinux.com)
* Jordi Riera (jordi.riera@savoirfairelinux.com)
    """,
    'depends': [
        'stock',
    ],
    'data': [
        'stock_move_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'external_dependencies': {
        'python': [],
    }
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
