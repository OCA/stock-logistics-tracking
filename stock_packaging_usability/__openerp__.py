# -*- encoding: utf-8 -*-
##############################################################################
#
#    Stock Packaging Usability module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com).
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Stock Packaging Usability',
    'version': '1.0',
    'category': 'Warehouse Management',
    'license': 'AGPL-3',
    'summary': "Faster packaging process in Odoo",
    'description': """
This module adds 2 buttons in the *Transfer* wizard of the picking:

* *Put in current pack* (this button is native in v7 but not in v8)

* *Put residual in new pack* : all the lines that are not in a package
    will be put in a new package.

So this module is a time saver when you use the packaging features of Odoo !
For example, on a picking where all the products go in the same package, you
just have to click on the button *Put residual in new pack* and you're done:
no need to click on each line !

This module has been written by Alexis de Lattre from Akretion
<alexis.delattre@akretion.com>
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['stock'],
    'data': ['wizard/stock_transfer_details.xml'],
    'installable': True,
}
