import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-l10n-indonesia",
    description="Meta package for oca-l10n-indonesia Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-l10n_id_taxform',
        'odoo8-addon-l10n_id_taxform_employee_joining_period',
        'odoo8-addon-l10n_id_taxform_period',
        'odoo8-addon-l10n_id_taxform_pph_21',
        'odoo8-addon-l10n_id_taxform_pph_21_payslip',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
