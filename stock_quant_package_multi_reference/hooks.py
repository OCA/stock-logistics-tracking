# © 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init_hook(cr, registry):
    cr.execute(
        """
    INSERT INTO stock_quant_package_reference
    (stock_quant_package_id, name, sequence)
    SELECT id, name, 0
    FROM stock_quant_package
    WHERE name IS NOT NULL"""
    )
