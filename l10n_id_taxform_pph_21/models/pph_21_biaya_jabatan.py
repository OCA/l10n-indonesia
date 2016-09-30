# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.tools.translate import _
from datetime import datetime


class Pph21TunjanganJabatan(models.Model):
    _name = "l10n_id.pph_21_biaya_jabatan"
    _description = "Biaya Jabatan"
    _order = "date_start desc, id"

    name = fields.Char(
        string="Dasar Hukum",
        required=True,
    )
    date_start = fields.Date(
        string="Tanggal Mulai Berlaku",
        required=True,
    )
    rate_biaya_jabatan = fields.Float(
        string="Rate Biaya Jabatan",
        required=True,
    )
    max_biaya_jabatan = fields.Float(
        string="Max. Biaya Jabatan",
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
        result = self.search(criteria, limit=1)
        if not result:
            strWarning = _(
                "No biaya jabatan configuration for %s" % dt)
            raise models.ValidationError(strWarning)
        return result

    @api.multi
    def get_biaya_jabatan(
            self,
            jumlah_penghasilan=0.0,
            penambahan=0.0,
            tanggal_pemotongan=False,
            masa_kerja=12,
    ):
        self.ensure_one()
        multiply = (self.rate_biaya_jabatan / 100.00) * \
            jumlah_penghasilan
        if multiply + penambahan >= (self.max_biaya_jabatan * masa_kerja):
            result = (self.max_biaya_jabatan * masa_kerja) - penambahan
        else:
            result = multiply
        return result
