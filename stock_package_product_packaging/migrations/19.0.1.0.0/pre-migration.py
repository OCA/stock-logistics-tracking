# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_module(
        env.cr,
        "stock_quant_package_product_packaging",
        "stock_package_product_packaging",
    )
