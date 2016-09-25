# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.tools.translate import _
from datetime import datetime


class Pph21TunjanganJabatan(models.Model):
    _name = "l10n_id.pph_21_biaya_jabatan"
    _description = "Biaya Jabatan"

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

    @api.model
    def find(self, dt=None):
        if not dt:
            dt = datetime.now().strftime("%Y-%m-%d")
        criteria = [("date_start", "<=", dt)]
        results = self.search(criteria, limit=1)
        if not results:
            raise models.ValidationError(_("Wes"))
        return results[0]

    @api.multi
    def get_biaya_jabatan_rutin(
            self,
            jumlah_penghasilan_rutin=0.0,
            tanggal_pemotongan=False):
        self.ensure_one()
        multiply = (self.rate_biaya_jabatan / 100.00) * \
            jumlah_penghasilan_rutin
        if multiply >= self.max_biaya_jabatan:
            result = self.max_biaya_jabatan
        else:
            result = multiply

        return result

    @api.multi
    def get_biaya_jabatan_non_rutin(
            self,
            jumlah_penghasilan_non_rutin=0.0,
            biaya_jabatan_rutin=0.0,
            tanggal_pemotongan=False):
        self.ensure_one()
        multiply = (self.rate_biaya_jabatan / 100.00) * \
            jumlah_penghasilan_non_rutin
        if multiply + biaya_jabatan_rutin >= self.max_biaya_jabatan:
            result = self.max_biaya_jabatan - biaya_jabatan_rutin
        else:
            result = multiply

        return result

    @api.multi
    def get_biaya_jabatan(
            self,
            jumlah_penghasilan_rutin=0.0,
            jumlah_penghasilan_non_rutin=0.0,
            tanggal_pemotongan=False):
        # TODO:
        self.ensure_one()
        result = {
            "biaya_jabatan_rutin": 0.0,
            "biaya_jabatan_non_rutin": 0.0,
            "biaya_jabatan": 0.0,
        }
        biaya_jabatan_rutin = self.get_biaya_jabatan_rutin(
            jumlah_penghasilan_rutin,
            tanggal_pemotongan)
        biaya_jabatan_non_rutin = self.get_biaya_jabatan_non_rutin(
            jumlah_penghasilan_non_rutin,
            biaya_jabatan_rutin,
            tanggal_pemotongan)
        result["biaya_jabatan_rutin"] = biaya_jabatan_rutin
        result["biaya_jabatan_non_rutin"] = biaya_jabatan_non_rutin
        result["biaya_jabatan"] = biaya_jabatan_rutin + \
            biaya_jabatan_non_rutin
        return result
