# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class HrContract(models.Model):
    _inherit = "hr.contract"

    penghasilan_netto_sebelumnya = fields.Float(
        string="Penghasilan Netto Sebelumnya",
    )
    pph_21_yang_telah_dipotong = fields.Float(
        string="PPh 21 Yang Telah Dipotong",
    )
