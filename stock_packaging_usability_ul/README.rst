.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

============================
Stock Packaging Usability UL
============================

This module allows to select the logistics unit (e.g. EUR-pallet, box 50x40x30, package 30x20x17, ...) on the fly when you define a new pack.

Configuration
=============

Go to the Settings page of the Inventory menu and enable the option
*Record packages used on packing: pallets, boxes, ...*: it will add all
users to the group *Manage Packages*.

Usage
=====

This module modifies the behavior of the buttons *Put in new
pack* of stock operations (button provided by the module
*stock_packing_usability*) and *Put in pack* of pickings (native button):
when you click on those buttons, it will ask you to select the
logistics unit (object *product.ul*) of the package.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/152/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-tracking/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
