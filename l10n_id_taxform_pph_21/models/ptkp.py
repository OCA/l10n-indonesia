# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.tools.translate import _
from datetime import datetime


class PtkpCategory(models.Model):
    _name = "l10n_id.ptkp_category"
    _description = "Kategori PTKP"

    name = fields.Char(
        string="Category",
        required=True,
    )
    note = fields.Text(
        string="Additional Note",
    )

    @api.multi
    def get_rate(self, dt=None):
        self.ensure_one()
        obj_ptkp = self.env["l10n_id.ptkp"]
        ptkp = obj_ptkp.find(dt)
        result = ptkp.get_rate(self)
        return result


class Ptkp(models.Model):
    _name = "l10n_id.ptkp"
    _description = "Tarif PTKP"
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
        string="Detail Tarif",
        comodel_name="l10n_id.ptkp_line",
        inverse_name="ptkp_id",
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
                "No PTKP rate configuration for %s" % dt)
            raise models.ValidationError(strWarning)
        return results[0]

    @api.multi
    def get_rate(self, ptkp_category):
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda r: r.ptkp_category_id.id == ptkp_category.id)
        if not lines:
            raise models.ValidationError(_("Wes"))
        return lines[0].ptkp_rate


class PtkpLine(models.Model):
    _name = "l10n_id.ptkp_line"
    _description = "PTKP Line"

    ptkp_id = fields.Many2one(
        string="PTKP",
        comodel_name="l10n_id.ptkp",
        ondelete="cascade",
    )
    ptkp_category_id = fields.Many2one(
        string="PTKP Category",
        comodel_name="l10n_id.ptkp_category",
        required=True,
    )
    ptkp_rate = fields.Float(
        string="Tarif PTKP",
        required=True,
    )

    _sql_constraints = [
        ("pktp_category_use_only_once",
         "unique(ptkp_id, ptkp_category_id)",
         _("PTKP category can only be used once on each PTKP"))
    ]
