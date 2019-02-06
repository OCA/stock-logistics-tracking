# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

try:
    from openupgradelib import openupgrade
    OPENUPGRADE_LIB = True
except ImportError:
    OPENUPGRADE_LIB = False


def post_init_hook(cr, registry):
    # If model data is the former one
    cr.execute("select 1 from ir_model_data imd"
               " join ir_model_fields imf on imf.id = imd.res_id AND"
               " imd.model = 'product.ul'"
               " WHERE imd.module = 'product'")
    if cr.fetchall():
        model = 'product.ul'
        moved_fields = [
            'name',
            'type',
            'length',
            'width',
            'height',
            'weight',
        ]
        old_module = 'product'
        new_module = 'stock_product_ul'
        if OPENUPGRADE_LIB:
            openupgrade.update_module_moved_fields(
                cr=cr,
                model=model,
                moved_fields=moved_fields,
                old_module=old_module,
                new_module=new_module,
            )
        else:
            # Raw copy of update_module_moved_fields()
            vals = {
                'new_module': new_module,
                'old_module': old_module,
                'model': model,
                'fields': tuple(moved_fields),
            }

            # update xml-id entries
            cr.execute(
                """
                UPDATE ir_model_data imd
                SET module = %(new_module)s
                FROM ir_model_fields imf
                WHERE
                    imf.model = %(model)s AND
                    imf.name IN %(fields)s AND
                    imd.module = %(old_module)s AND
                    imd.res_id = imf.id AND
                    imd.id NOT IN (
                    SELECT id FROM ir_model_data WHERE module = %(new_module)s
                    )
                """,
                vals,
            )

            # update ir_translation - it covers both <=v8 through type='field' and
            # >=v9 through type='model' + name
            cr.execute(
                """
                UPDATE ir_translation it
                SET module = %(new_module)s
                FROM ir_model_fields imf
                WHERE
                    imf.model = %(model)s AND
                    imf.name IN %(fields)s AND
                    it.res_id = imf.id AND
                    it.module = %(old_module)s AND ((
                        it.name LIKE 'ir.model.fields,field_%%' AND
                        it.type = 'model'
                    ) OR (
                        it.type = 'field'
                    ))
                """,
                vals,
            )
