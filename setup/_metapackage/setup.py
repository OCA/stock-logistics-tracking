import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-stock-logistics-tracking",
    description="Meta package for oca-stock-logistics-tracking Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-stock_quant_package_multi_reference>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
