# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields
from openerp.tools.translate import _


class ResPartner(models.Model):
    _inherit = "res.partner"

    ptkp_category_id = fields.Many2one(
        string="PTKP Category",
        comodel_name="l10n_id.ptkp_category",
    )

    @api.multi
    def compute_pph_21_2110001(
            self,
            bulan_bergabung=1,
            tanggal_pemotongan=False,
            gaji=0.0,
            tunjangan_pph=0.0,
            tunjangan_lain=0.0,
            jumlah_penghasilan_non_rutin=0.0,
            pensiun=0.0,
    ):
        self.ensure_one()
        result = {
            "biaya_jabatan_rutin": 0.0,
            "biaya_jabatan_non_rutin": 0.0,
            "biaya_jabatan": 0.0,
            "pengurang": 0.0,
            "penghasilan_bruto_rutin_setahun": 0.0,
            "penghasilan_bruto_non_rutin_setahun": 0.0,
            "penghasilan_bruto_setahun": 0.0,
            "ptkp": 0.0,
            "pkp_rutin_setahun": 0.0,
            "pkp_setahun": 0.0,
            "pph_rutin_setahun": 0.0,
            "pph_non_rutin_setahun": 0.0,
            "pph_setahun": 0.0,
            "pph": 0.0,
        }
        ptkp_category = self.ptkp_category_id

        if not ptkp_category:
            raise models.ValidationError(
                _("Partner's PTKP Category is not configured"))

        jumlah_penghasilan_rutin = gaji + \
            tunjangan_pph + tunjangan_lain

        obj_biaya_jabatan = self.env["l10n_id.pph_21_biaya_jabatan"]
        perhitungan_biaya_jabatan = obj_biaya_jabatan.find(
            tanggal_pemotongan).get_biaya_jabatan(
            jumlah_penghasilan_rutin,
            jumlah_penghasilan_non_rutin,
            tanggal_pemotongan,
        )
        biaya_jabatan_rutin = perhitungan_biaya_jabatan["biaya_jabatan_rutin"]
        biaya_jabatan_non_rutin = perhitungan_biaya_jabatan[
            "biaya_jabatan_non_rutin"]
        biaya_jabatan = perhitungan_biaya_jabatan["biaya_jabatan"]
        pengurang = biaya_jabatan_rutin + \
            biaya_jabatan_non_rutin + \
            pensiun
        netto_rutin = jumlah_penghasilan_rutin - \
            biaya_jabatan_rutin - \
            pensiun
        netto_non_rutin = jumlah_penghasilan_non_rutin - \
            biaya_jabatan_non_rutin
        netto = netto_rutin + netto_non_rutin

        netto_setahun_rutin = netto_rutin * (13 - bulan_bergabung)
        netto_setahun = netto_setahun_rutin + netto_non_rutin

        if gaji > 0.0:
            ptkp = ptkp_category.get_rate(tanggal_pemotongan)
        else:
            ptkp = 0.0

        pkp = netto_setahun - ptkp
        pkp_rutin = netto_setahun_rutin - ptkp

        obj_pph = self.env["l10n_id.pph_21_rate"]
        pph_setahun = obj_pph.find(tanggal_pemotongan).compute_tax(pkp)
        pph_setahun_rutin = obj_pph.find(
            tanggal_pemotongan).compute_tax(pkp_rutin)
        pph_non_rutin = pph_setahun - pph_setahun_rutin

        pph_sebulan = pph_setahun_rutin / (13 - bulan_bergabung)
        pph = pph_sebulan + pph_non_rutin

        npwp = self.vat and len(self.vat) > 0 or False
        if not npwp:
            obj_multiplier = self.env["l10n_id.pph_21_npwp_rate_modifier"]
            pph = (obj_multiplier.get_rate(tanggal_pemotongan) / 100.00) * pph
        pph = float(int(pph))

        result["biaya_jabatan_rutin"] = biaya_jabatan_rutin
        result["biaya_jabatan_non_rutin"] = biaya_jabatan_non_rutin
        result["biaya_jabatan"] = biaya_jabatan
        result["pengurang"] = pengurang
        result["netto"] = netto
        result["netto_setahun"] = netto_setahun
        result["ptkp"] = ptkp
        result["pkp"] = pkp
        result["pph_setahun"] = pph_setahun
        result["pph"] = pph

        return result
