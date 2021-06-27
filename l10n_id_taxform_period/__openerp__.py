# Copyright 2021 PT. Simetri Sinergi Indonesia
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Indonesia's Taxform - Tax Period",
    "version": "8.0.1.0.0",
    "category": "Hidden",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia,"
    " Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "l10n_id_taxform",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/tax_period_views.xml",
    ],
    "demo": [
        "demo/tax_period_demo.xml",
    ],
}
