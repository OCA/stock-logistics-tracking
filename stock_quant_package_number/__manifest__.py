# Copyright 2025 Camptocamp SA
# @author: Italo LOPES <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Stock Picking Package Number",
    "version": "18.0.1.1.0",
    "summary": "This module add new fields to set package number",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-tracking",
    "maintainer": ["imlopes"],
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": [
        "views/stock_quant_package_views.xml",
    ],
    "external_dependencies": {"python": ["openupgradelib"]},
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "installable": True,
}
