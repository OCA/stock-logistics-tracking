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

{
    "name" : "Stock tracking add or remove object",
    "version" : "1.0",
    "author" : "Julius Network Solutions,Odoo Community Association (OCA)",
    "description" : """Presentation:

This module add a wizard to fill in packaging. It will also add a wizard to remove pieces from a pack
This wizard is used to add or remove an object from a package.
Adding to the historical movements and parent objects

""",
    "website" : "http://www.julius.fr",
    "depends" : [
         "stock",
         "stock_tracking_extended",
    ],
    "category" : "Warehouse Management",
    "images" : [],
    "demo" : [],
    "data" : [
        "security/ir.model.access.csv",
        "wizard/add_object_view.xml",
        "wizard/remove_object_view.xml",
        "data/type.xml",
        'stock_view.xml',
    ],
    'test': [],
    'installable': False,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: