# © 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Package multi reference",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "category": "Inventory/Inventory",
    "depends": ["stock"],
    "website": "https://github.com/OCA/stock-logistics-tracking",
    "data": [
        "views/stock_quant_package_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
