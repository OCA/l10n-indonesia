# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.multi
    def compute_akumulasi(
            self,
            tax_period):
        self.ensure_one()
        result = {
            "akumulasi_pendapatan": 0.0,
            "akumulasi_pensiun": 0.0,
            "pph_21_telah_dipotong": 0.0,
        }
        categ_gaji_id = self.env.ref(
            "l10n_id_taxform_pph_21_payslip.rule_categ_gapok").id
        categ_tunj_pph_id = self.env.ref(
            "l10n_id_taxform_pph_21_payslip.rule_categ_tunjangan_pph").id
        categ_tunj_lain_id = self.env.ref(
            "l10n_id_taxform_pph_21_payslip.rule_categ_tunjangan_lain").id
        categ_non_rutin_id = self.env.ref(
            "l10n_id_taxform_pph_21_payslip.rule_categ_non_rutin").id
        categ_ids = [
            categ_gaji_id,
            categ_tunj_pph_id,
            categ_tunj_lain_id,
            categ_non_rutin_id,
        ]
        categ_pensiun_id = self.env.ref(
            "l10n_id_taxform_pph_21_payslip.rule_categ_pensiun").id
        categ_pph_id = self.env.ref(
            "l10n_id_taxform_pph_21_payslip.rule_categ_pph").id
        obj_line = self.env["hr.payslip.line"]

        period_criteria = [
            ("date_start", "<", tax_period.date_start),
            ("year_id.id", "=", tax_period.year_id.id),
        ]

        tax_period_ids = self.env["l10n_id.tax_period"].search(
            period_criteria).ids

        criteria = [
            ("slip_id.employee_id.id", "=", self.id),
            ("slip_id.state", "=", "done"),
            ("slip_id.tax_period_id", "in", tax_period_ids),
            ("slip_id.tax_year_id", "=", tax_period.year_id.id),
        ]

        criteria_1 = [
            ("salary_rule_id.category_id.id", "in", categ_ids),
        ] + criteria
        lines = obj_line.search(criteria_1)
        for line in lines:
            result["akumulasi_pendapatan"] += line.total

        criteria_2 = [
            ("salary_rule_id.category_id.id", "=", categ_pensiun_id),
        ] + criteria
        lines = obj_line.search(criteria_2)
        for line in lines:
            result["akumulasi_pensiun"] += abs(line.total)

        criteria_3 = [
            ("salary_rule_id.category_id.id", "=", categ_pph_id),
        ] + criteria
        lines = obj_line.search(criteria_3)
        for line in lines:
            result["pph_21_telah_dipotong"] += abs(line.total)
        return result
