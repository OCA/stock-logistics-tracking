# Copyright 2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
import odoo.addons.decimal_precision as dp


class ProductUl(models.Model):
    _name = 'product.ul'
    _description = 'Logistics Unit'
    _order = 'sequence, id'

    name = fields.Char(
        string='Name', index=True, required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    type = fields.Selection(
        [
            ('unit', 'Unit'),
            ('pack', 'Pack'),
            ('box', 'Box'),
            ('pallet', 'Pallet'),
        ],
        string='Type',
        required=True,
    )
    length = fields.Float(  # pylint: disable=W8105
        string='Length', help='Length of the logistics unit in cm')
    width = fields.Float(
        string='Width', help='Width of the logistics unit in cm')
    height = fields.Float(
        string='Height', help='Height of the logistics unit in cm')
    weight = fields.Float(
        string='Empty Package Weight', digits=dp.get_precision('Weight'),
        help='Package weight in kg.')
    product_id = fields.Many2one(
        'product.product', string='Related Product', ondelete='restrict',
        domain=[('type', 'in', ('product', 'consu'))])

    _sql_constraints = [
        ('length_positive', 'CHECK(length >= 0)', 'Length must be >= 0'),
        ('width_positive', 'CHECK(width >= 0)', 'Width must be >= 0'),
        ('height_positive', 'CHECK(height >= 0)', 'Height must be >= 0'),
        ('weight_positive', 'CHECK(weight >= 0)', 'Weight must be >= 0'),
    ]
