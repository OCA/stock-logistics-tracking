# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

try:
    from openupgradelib import openupgrade
    OPENUPGRADE_LIB = True
except ImportError:
    OPENUPGRADE_LIB = False


def post_init_hook(cr, registry):
    if not OPENUPGRADE_LIB:
        return

    # If model data is the former one
    cr.execute("select 1 from ir_model_data imd"
               " join ir_model_fields imf on imf.id = imd.res_id AND"
               " imd.model = 'product.ul'"
               " WHERE imd.module = 'product'")
    if cr.fetchall():
        openupgrade.update_module_moved_fields(
            cr=cr,
            model='product.ul',
            moved_fields=[
                'name',
                'type',
                'length',
                'width',
                'height',
                'weight',
            ],
            old_module='product',
            new_module='stock_product_ul',
        )
