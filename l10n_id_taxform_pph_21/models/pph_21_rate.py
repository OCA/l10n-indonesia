# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.tools.translate import _
from datetime import datetime


class Pph21Rate(models.Model):
    _name = "l10n_id.pph_21_rate"
    _description = "PPh 21 Rate"
    _order = "date_start desc, id"

    name = fields.Char(
        string="Dasar Hukum",
        required=True,
    )
    date_start = fields.Date(
        string="Tanggal Mulai Berlaku",
        required=True,
    )
    line_ids = fields.One2many(
        string="PPh 21 Rate Detail",
        comodel_name="l10n_id.pph_21_rate_line",
        inverse_name="rate_id",
    )

    _sql_constraints = [
        ("date_start_unique",
         "unique(date_start)",
         _("Date start has to be unique"))
    ]

    @api.model
    def find(self, dt=None):
        if not dt:
            dt = datetime.now().strftime("%Y-%m-%d")
        criteria = [("date_start", "<=", dt)]
        results = self.search(criteria, limit=1)
        if not results:
            strWarning = _(
                "No PPh 21 rate configuration for %s" % dt)
            raise models.ValidationError(strWarning)
        return results[0]

    @api.multi
    def compute_tax(self, penghasilan_kena_pajak):
        result = 0.0
        self.ensure_one()
        for line in range(0, len(self.line_ids) - 1):
            if line < len(self.line_ids) - 1:
                next_line = self.line_ids[line + 1]
            else:
                next_line = False

            result += self.line_ids[line].compute_tax(
                penghasilan_kena_pajak,
                next_line)
        return result


class Pph21RateLine(models.Model):
    _name = "l10n_id.pph_21_rate_line"
    _description = "PPh 21 Rate Line"
    _order = "min_income asc"

    rate_id = fields.Many2one(
        string="PPh 21 Rate",
        comodel_name="l10n_id.pph_21_rate",
        ondelete="cascade",
    )
    min_income = fields.Float(
        string="Min. Income",
        required=True,
    )
    pph_rate = fields.Float(
        string="PPh 21 Rate",
    )

    @api.multi
    def compute_tax(self, penghasilan_kena_pajak, next_line):
        self.ensure_one()
        result = 0.0
        pph_rate = self.pph_rate / 100.00
        if penghasilan_kena_pajak > self.min_income:
            if not next_line:
                result = pph_rate * (penghasilan_kena_pajak - self.min_income)
            else:
                if penghasilan_kena_pajak >= next_line.min_income:
                    result = pph_rate * next_line.min_income
                else:
                    result = pph_rate * \
                        (penghasilan_kena_pajak - self.min_income)
        return result
