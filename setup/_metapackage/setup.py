import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-stock-logistics-tracking",
    description="Meta package for oca-stock-logistics-tracking Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-stock_packaging_usability',
        'odoo8-addon-stock_packaging_usability_ul',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
