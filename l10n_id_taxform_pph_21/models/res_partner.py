# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


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
            bulan_akhir=False,
            tanggal_pemotongan=False,
            gaji=0.0,
            tunjangan_pph=0.0,
            tunjangan_lain=0.0,
            jumlah_penghasilan_non_rutin=0.0,
            pensiun=0.0,
            akumulasi_penghasilan=0.0,
            akumulasi_pensiun=0.0,
            pph_21_sudah_dipotong=0.0,
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
        if not bulan_akhir:
            masa_kerja = 1
            realisasi = False
        else:
            masa_kerja = bulan_akhir - bulan_bergabung + 1
            realisasi = True

        ptkp_category = self.ptkp_category_id
        indonesia = self.env.ref("base.id")

        if not ptkp_category:
            raise UserError(
                _("Partner's PTKP Category is not configured"))

        if realisasi:
            perhitungan = self._compute_pph_21_2110001_realisasi(
                bulan_bergabung,
                bulan_akhir,
                masa_kerja,
                tanggal_pemotongan,
                indonesia,
                ptkp_category,
                gaji,
                tunjangan_pph,
                tunjangan_lain,
                jumlah_penghasilan_non_rutin,
                pensiun,
                akumulasi_penghasilan,
                akumulasi_pensiun,
                pph_21_sudah_dipotong,
            )
        else:
            perhitungan = self._compute_pph_21_2110001_bulanan(
                bulan_bergabung,
                bulan_akhir,
                masa_kerja,
                tanggal_pemotongan,
                indonesia,
                ptkp_category,
                gaji,
                tunjangan_pph,
                tunjangan_lain,
                jumlah_penghasilan_non_rutin,
                pensiun,
            )

        npwp = self.vat and len(self.vat) > 0 or False
        pph = perhitungan["pph"]
        if not npwp:
            obj_multiplier = self.env["l10n_id.pph_21_npwp_rate_modifier"]
            pph = (obj_multiplier.get_rate(tanggal_pemotongan) / 100.00) * pph
        pph = float(int(pph))

        result["biaya_jabatan_rutin"] = perhitungan["biaya_jabatan_rutin"]
        result["biaya_jabatan_non_rutin"] = perhitungan[
            "biaya_jabatan_non_rutin"]
        result["biaya_jabatan"] = perhitungan["biaya_jabatan"]
        result["pengurang"] = perhitungan["pengurang"]
        result["netto"] = perhitungan["netto"]
        result["netto_setahun"] = perhitungan["netto_setahun"]
        result["ptkp"] = perhitungan["ptkp"]
        result["pkp"] = perhitungan["pkp"]
        result["pph_setahun"] = perhitungan["pph_setahun"]
        result["pph"] = pph

        return result

    @api.multi
    def _compute_pph_21_2110001_bulanan(
            self,
            bulan_bergabung=1,
            bulan_akhir=False,
            masa_kerja=1,
            tanggal_pemotongan=False,
            kewarganegaraan=False,
            ptkp_category=False,
            gaji=0.0,
            tunjangan_pph=0.0,
            tunjangan_lain=0.0,
            jumlah_penghasilan_non_rutin=0.0,
            pensiun=0.0,
            akumulasi_penghasilan=0.0,
            akumulasi_pensiun=0.0,
            pph_21_sudah_dipotong=0.0,
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
            "netto": 0.0,
            "netto_setahun": 0.0,
            "ptkp": 0.0,
            "pkp_rutin_setahun": 0.0,
            "pkp_setahun": 0.0,
            "pph_rutin_setahun": 0.0,
            "pph_non_rutin_setahun": 0.0,
            "pph_setahun": 0.0,
            "pph": 0.0,
        }
        jumlah_penghasilan_rutin = gaji + \
            tunjangan_pph + tunjangan_lain

        obj_biaya_jabatan = self.env["l10n_id.pph_21_biaya_jabatan"]
        perhitungan_biaya_jabatan = obj_biaya_jabatan.find(
            tanggal_pemotongan)
        biaya_jabatan_rutin = perhitungan_biaya_jabatan.get_biaya_jabatan(
            jumlah_penghasilan=jumlah_penghasilan_rutin,
            penambahan=0.0,
            tanggal_pemotongan=tanggal_pemotongan,
            masa_kerja=1,
        )
        biaya_jabatan_non_rutin = perhitungan_biaya_jabatan.get_biaya_jabatan(
            jumlah_penghasilan=jumlah_penghasilan_non_rutin,
            penambahan=biaya_jabatan_rutin,
            tanggal_pemotongan=tanggal_pemotongan,
            masa_kerja=1,
        )
        biaya_jabatan = biaya_jabatan_rutin + \
            biaya_jabatan_non_rutin
        pengurang = biaya_jabatan_rutin + \
            biaya_jabatan_non_rutin + \
            pensiun
        netto_rutin = jumlah_penghasilan_rutin - \
            biaya_jabatan_rutin - \
            pensiun
        netto_non_rutin = jumlah_penghasilan_non_rutin - \
            biaya_jabatan_non_rutin
        netto = netto_rutin + netto_non_rutin

        if self.nationality_id == kewarganegaraan:
            netto_setahun_rutin = netto_rutin * (13 - bulan_bergabung)
        else:
            netto_setahun_rutin = netto_rutin * 12

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

        if self.nationality_id == kewarganegaraan:
            pph_sebulan = pph_setahun_rutin / (13 - bulan_bergabung)
        else:
            pph_sebulan = pph_setahun_rutin / 12

        pph = pph_sebulan + pph_non_rutin

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

    @api.multi
    def _compute_pph_21_2110001_realisasi(
            self,
            bulan_bergabung=1,
            bulan_akhir=False,
            masa_kerja=1,
            tanggal_pemotongan=False,
            kewarganegaraan=False,
            ptkp_category=False,
            gaji=0.0,
            tunjangan_pph=0.0,
            tunjangan_lain=0.0,
            jumlah_penghasilan_non_rutin=0.0,
            pensiun=0.0,
            akumulasi_penghasilan=0.0,
            akumulasi_pensiun=0.0,
            pph_21_sudah_dipotong=0.0,
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
            "netto": 0.0,
            "netto_setahun": 0.0,
            "ptkp": 0.0,
            "pkp_rutin_setahun": 0.0,
            "pkp_setahun": 0.0,
            "pph_rutin_setahun": 0.0,
            "pph_non_rutin_setahun": 0.0,
            "pph_setahun": 0.0,
            "pph": 0.0,
        }
        penghasilan_bruto_setahun = gaji + \
            tunjangan_pph + \
            tunjangan_lain + \
            jumlah_penghasilan_non_rutin + \
            akumulasi_penghasilan
        obj_biaya_jabatan = self.env["l10n_id.pph_21_biaya_jabatan"]
        perhitungan_biaya_jabatan = obj_biaya_jabatan.find(
            tanggal_pemotongan)
        biaya_jabatan = perhitungan_biaya_jabatan.get_biaya_jabatan(
            jumlah_penghasilan=penghasilan_bruto_setahun,
            tanggal_pemotongan=tanggal_pemotongan,
            masa_kerja=masa_kerja,
        )
        pensiun = pensiun + akumulasi_pensiun
        pengurang = biaya_jabatan + \
            pensiun
        netto_setahun = penghasilan_bruto_setahun - \
            pengurang
        if penghasilan_bruto_setahun > 0.0:
            ptkp = ptkp_category.get_rate(tanggal_pemotongan)
        else:
            ptkp = 0.0
        pkp = netto_setahun - ptkp
        obj_pph = self.env["l10n_id.pph_21_rate"]
        pph_setahun = obj_pph.find(
            tanggal_pemotongan).compute_tax(pkp)
        pph = pph_setahun - pph_21_sudah_dipotong

        result["biaya_jabatan"] = biaya_jabatan
        result["pengurang"] = pengurang
        result["netto_setahun"] = netto_setahun
        result["ptkp"] = ptkp
        result["pkp"] = pkp
        result["pph_setahun"] = pph_setahun
        result["pph"] = pph
        return result
