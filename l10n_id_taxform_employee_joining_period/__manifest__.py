# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Indonesia - Employee's Joining Time Based on Tax Period",
    "version": "14.0.1.0.0",
    "category": "localization",
    "website": "https://github.com/OCA/l10n-indonesia",
    "author": "OpenSynergy Indonesia," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "l10n_id_taxform_period",
        "hr_contract",
    ],
    "data": [
        "views/hr_employee_views.xml",
    ],
}