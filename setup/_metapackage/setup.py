import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-stock-logistics-tracking",
    description="Meta package for oca-stock-logistics-tracking Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-stock_picking_manual_package',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
