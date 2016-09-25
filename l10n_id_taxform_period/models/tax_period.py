# -*- coding: utf-8 -*-
# Copyright 2016 Prime Force Indonesia
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class TaxYear(models.Model):
    _name = "l10n_id.tax_year"
    _description = "Tax Year"
    _order = "date_start asc, id"

    name = fields.Char(
        string="Tax Year",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    date_start = fields.Date(
        string="Date Start",
        required=True,
    )
    date_end = fields.Date(
        string="Date End",
        required=True,
    )
    period_ids = fields.One2many(
        string="Periods",
        comodel_name="l10n_id.tax_period",
        inverse_name="year_id",
    )

    @api.constrains("date_start", "date_end")
    def _check_range(self):
        if self.date_end <= self.date_start:
            strWarning = _("The start date must precede it's end date")
            raise models.ValidationError(strWarning)

    @api.multi
    def action_create_period(self):
        for year in self:
            year._create_period()

    @api.multi
    def _create_period(self):
        self.ensure_one()
        obj_period = self.env["l10n_id.tax_period"]
        date_start = datetime.strptime(self.date_start, "%Y-%m-%d")
        while date_start.strftime("%Y-%m-%d") < self.date_end:
            date_end = date_start + relativedelta(months=+1, days=-1)

            if date_end.strftime("%Y-%m-%d") > self.date_end:
                date_end = datetime.strptime(self.date_end, "%Y-%m-%d")

            obj_period.create({
                "name": date_start.strftime("%m/%Y"),
                "code": date_start.strftime("%m/%Y"),
                "date_start": date_start.strftime("%Y-%m-%d"),
                "date_end": date_end.strftime("%Y-%m-%d"),
                "year_id": self.id,
            })
            date_start = date_start + relativedelta(months=+1)

    @api.model
    def _find_year(self, dt=None):
        if not dt:
            dt = datetime.now().strftime("%Y-%m-%d")
        criteria = [
            ("date_start", "<=", dt),
            ("date_end", ">=", dt),
        ]
        results = self.search(criteria)
        if not results:
            strWarning = _("No tax year configured for %s" % dt)
            raise models.ValidationError(strWarning)
        result = results[0]
        return result


class TaxPeriod(models.Model):
    _name = "l10n_id.tax_period"
    _description = "Tax Period"
    _order = "date_start asc, id"

    name = fields.Char(
        string="Tax Period",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    date_start = fields.Date(
        string="Date Start",
        required=True,
    )
    date_end = fields.Date(
        string="Date End",
        required=True,
    )
    year_id = fields.Many2one(
        string="Tax Year",
        comodel_name="l10n_id.tax_year",
        ondelete="cascade",
    )

    @api.constrains("date_start", "date_end")
    def _check_range(self):
        if self.date_end <= self.date_start:
            strWarning = _("The start date must precede it's end date")
            raise models.ValidationError(strWarning)

    @api.multi
    def _next_period(self, step):
        self.ensure_one()
        criteria = [
            ("date_start", ">", self.date_start)
        ]
        results = self.search(criteria)
        if results:
            return results[step - 1]
        return False

    @api.multi
    def _previous_period(self, step):
        self.ensure_one()
        criteria = [
            ("date_start", "<", self.date_start)
        ]
        results = self.search(criteria, order="date_start desc")
        if results:
            return results[step - 1]
        return False

    @api.model
    def _find_period(self, dt=None):
        if not dt:
            dt = datetime.now().strftime("%Y-%m-%d")
        criteria = [
            ("date_start", "<=", dt),
            ("date_end", ">=", dt),
        ]
        results = self.search(criteria)
        if not results:
            strWarning = _("No tax period configured for %s" % dt)
            raise models.ValidationError(strWarning)
        result = results[0]
        return result
