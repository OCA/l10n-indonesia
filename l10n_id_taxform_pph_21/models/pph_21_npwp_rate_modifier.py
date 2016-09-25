# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.tools.translate import _
from datetime import datetime


class Pph21NpwpRateModifier(models.Model):
    _name = "l10n_id.pph_21_npwp_rate_modifier"
    _description = "PPh 21 NPWP Rate Modifier"
    _order = "date_start desc, id"

    name = fields.Char(
        string="Dasar Hukum",
        required=True,
    )
    date_start = fields.Date(
        string="Tanggal Mulai Berlaku",
        required=True,
    )
    pph_rate_modifier = fields.Float(
        string="PPh Rate Modifier",
        required=True,
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
                "No NPWP rate modifier configuration for %s" % dt)
            raise models.ValidationError(strWarning)
        return results[0]

    @api.model
    def get_rate(self, dt=None):
        modifier = self.find(dt)
        return modifier.pph_rate_modifier
