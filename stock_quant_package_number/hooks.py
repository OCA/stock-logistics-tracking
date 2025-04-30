from openupgradelib.openupgrade import logged_query


def post_init_hook(env):
    logged_query(
        env.cr,
        """
        UPDATE stock_quant_package
        SET package_number =
            CASE
                WHEN order_number IS NOT NULL AND sheet_number IS NOT NULL
                THEN order_number || '_' || sheet_number
                ELSE ''
            END
        """,
    )


def pre_init_hook(env):
    # Following query is needed when the amount of records
    # causes a MemoryError in the ORM
    logged_query(
        env.cr,
        """
        ALTER TABLE stock_quant_package ADD COLUMN IF NOT EXISTS
        package_number varchar;
        """,
    )
