# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.depends(
        "contract_ids",
        "contract_ids.date_start")
    @api.multi
    def _compute_tax_period(self):
        for employee in self:
            obj_contract = self.env["hr.contract"]
            criteria = [
                ("employee_id", "=", employee.id),
            ]
            contract = obj_contract.search(
                criteria, order="date_start asc", limit=1)
            if not contract:
                employee.joining_tax_period_id = False
                employee.joining_tax_year_id = False
                continue

            try:
                obj_period = self.env["l10n_id.tax_period"]
                period = obj_period._find_period(
                    contract.date_start)
                employee.joining_tax_period_id = period
                employee.joining_tax_year_id = period.year_id
            except:
                employee.joining_tax_period_id = False
                employee.joining_tax_year_id = False

    joining_tax_period_id = fields.Many2one(
        string="Joining Tax Period",
        comodel_name="l10n_id.tax_period",
        compute="_compute_tax_period",
        store=True,
    )
    joining_tax_year_id = fields.Many2one(
        string="Joining Tax Year",
        comodel_name="l10n_id.tax_year",
        compute="_compute_tax_period",
        store=True,
    )
