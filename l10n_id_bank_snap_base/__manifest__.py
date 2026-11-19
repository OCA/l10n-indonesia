# Copyright 2026 PT Solusi Aglis Indonesia. (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Indonesia - Bank SNAP BI Base",
    "summary": "SNAP BI (Bank Indonesia Open API) core for online bank statements",
    "version": "18.0.1.0.0",
    "category": "Localizations",
    "website": "https://github.com/OCA/l10n-indonesia",
    "author": "PT Solusi Aglis Indonesia, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["account_statement_import_online"],
    "external_dependencies": {"python": ["cryptography"]},
    "data": [
        "views/online_bank_statement_provider_views.xml",
    ],
    "installable": True,
}
