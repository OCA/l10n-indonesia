# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Indonesia's Taxform - PPh 21 Computation On Payslip",
    "version": "14.0.1.0.0",
    "category": "localization",
    "website": "https://github.com/OCA/l10n-indonesia",
    "author": "OpenSynergy Indonesia," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "l10n_id_taxform_pph_21",
        "l10n_id_taxform_employee_joining_period",
        "payroll",
    ],
    "data": [
        "views/hr_payslip_views.xml",
        "data/hr_salary_rule_category_data.xml",
        "data/hr_salary_rule_data.xml",
    ],
}
