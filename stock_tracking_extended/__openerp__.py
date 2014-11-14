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
    "name": "Stock Tracking extended",
    "version": "1.1",
    "author": "Julius Network Solutions",
    "description" : """

Presentation:

This module adds some info into packs to get a better tracking of products and serial lots inside of these packs

""",
    "website": "http://www.julius.fr",
    "depends": [
        "stock",
    ],
    "category": "Warehouse Management",
    #    "images" : ['images/Tracking_extended.png'],
    "demo": [],
    "data": [
        'stock_tracking_view.xml',
        "security/ir.model.access.csv",
    ],
    'test': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
