# -*- coding: utf-8 -*-
##########################################################################
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
##########################################################################

{
    "name": "Move Stock Packaging",
    "version": "1.0",
    "author": "Julius Network Solutions",
    "description" : """

Presentation:

This module allows to move packing with a wizard
and adds fields for source location and destination location in History.

""",
    "website": "http://www.julius.fr",
    "depends": [
        "stock",
        "stock_tracking_extended",
    ],
    "category": "Warehouse Management",
    #    "images" : ['images/Move packaging.png'],
    "demo": [],
    "data": [
        'stock_view.xml',
        'wizard/move_pack_view.xml',
    ],
    'test': [],
    'installable': False,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
