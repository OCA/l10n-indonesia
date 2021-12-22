# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Indonesia's Taxform",
    "version": "14.0.1.0.0",
    "category": "localization",
    "website": "https://github.com/OCA/l10n-indonesia",
    "author": "OpenSynergy Indonesia," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "security/taxform_groups.xml",
        "views/menu.xml",
    ],
}