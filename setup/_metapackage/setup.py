import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-stock-logistics-tracking",
    description="Meta package for oca-stock-logistics-tracking Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-stock_packaging_usability',
        'odoo14-addon-stock_packaging_usability_pp',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
