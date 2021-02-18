# Copyright 2016 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.tools.translate import _

# from math import floor


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
        # akumulasi data untuk akhir tahun dan karyawan keluar
        akumulasi_penghasilan_non_rutin=0.0,
        akumulasi_pensiun=0.0,
        akumulasi_tunjangan_lain=0.0,
        akumulasi_tunjangan_pph=0.0,
        akumulasi_gaji=0.0,
        akumulasi_pph_yang_disetor=0.0,
        is_keluar=False,
        is_lokal=True,
    ):
        self.ensure_one()
        result = {
            "biaya_jabatan_rutin_setahun": 0.0,
            "biaya_jabatan_non_rutin_setahun": 0.0,
            "biaya_jabatan": 0.0,
            "biaya_jabatan_setahun": 0.0,
            "pengurang": 0.0,
            "jumlah_penghasilan_non_rutin": 0.0,
            "jumlah_penghasilan_rutin": 0.0,
            "jumlah_penghasilan_rutin_setahun": 0.0,
            "netto_setahun": 0.0,
            "netto_setahun_rutin": 0.0,
            "ptkp": 0.0,
            "pkp": 0.0,
            "pkp_rutin": 0.0,
            "pph_setahun": 0.0,
            "pph_setahun_rutin": 0.0,
            "pph_non_rutin": 0.0,
            "pph": 0.0,
        }
        ptkp_category = self.ptkp_category_id

        if not ptkp_category:
            raise models.ValidationError(_("Partner's PTKP Category is not configured"))

        # cek keluar
        dt_tanggal = fields.Date.from_string(tanggal_pemotongan)
        periode_pemotongan = dt_tanggal.month
        if periode_pemotongan == 12:
            is_keluar = True

        if is_keluar:
            jumlah_penghasilan_rutin = (
                gaji
                + tunjangan_pph
                + tunjangan_lain
                + akumulasi_gaji
                + akumulasi_tunjangan_pph
                + akumulasi_tunjangan_lain
            )
            jumlah_penghasilan_rutin_setahun = jumlah_penghasilan_rutin
            jumlah_penghasilan_non_rutin = (
                jumlah_penghasilan_non_rutin + akumulasi_penghasilan_non_rutin
            )
        else:
            if is_lokal:
                jumlah_penghasilan_rutin = gaji + tunjangan_pph + tunjangan_lain
                jumlah_penghasilan_rutin_setahun = (
                    gaji + tunjangan_pph + tunjangan_lain
                ) * (13 - bulan_bergabung)
            else:
                jumlah_penghasilan_rutin = gaji + tunjangan_pph + tunjangan_lain
                jumlah_penghasilan_rutin_setahun = (
                    gaji + tunjangan_pph + tunjangan_lain
                ) * 12
            jumlah_penghasilan_non_rutin = jumlah_penghasilan_non_rutin

        obj_biaya_jabatan = self.env["l10n_id.pph_21_biaya_jabatan"]
        perhitungan_biaya_jabatan = obj_biaya_jabatan.find(
            tanggal_pemotongan
        ).get_biaya_jabatan(
            jumlah_penghasilan_rutin,
            jumlah_penghasilan_rutin_setahun,
            jumlah_penghasilan_non_rutin,
            is_keluar,
        )
        biaya_jabatan_rutin_setahun = perhitungan_biaya_jabatan[
            "biaya_jabatan_rutin_setahun"
        ]
        biaya_jabatan_non_rutin_setahun = perhitungan_biaya_jabatan[
            "biaya_jabatan_non_rutin_setahun"
        ]
        biaya_jabatan_setahun = perhitungan_biaya_jabatan["biaya_jabatan_setahun"]
        biaya_jabatan = perhitungan_biaya_jabatan["biaya_jabatan"]

        netto_non_rutin = jumlah_penghasilan_non_rutin - biaya_jabatan_non_rutin_setahun

        if is_keluar:
            netto_setahun_rutin = (
                jumlah_penghasilan_rutin_setahun
                - biaya_jabatan_rutin_setahun
                - pensiun
                - akumulasi_pensiun
            )
            netto_setahun = netto_setahun_rutin + netto_non_rutin
            pengurang = (
                biaya_jabatan_rutin_setahun
                + biaya_jabatan_non_rutin_setahun
                + pensiun
                + akumulasi_pensiun
            )
        else:
            if is_lokal:
                netto_setahun_rutin = (
                    jumlah_penghasilan_rutin_setahun
                    - biaya_jabatan_rutin_setahun
                    - (pensiun * (13 - bulan_bergabung))
                )
                pengurang = (
                    biaya_jabatan_rutin_setahun
                    + biaya_jabatan_non_rutin_setahun
                    + (pensiun * (13 - bulan_bergabung))
                )
            else:
                netto_setahun_rutin = (
                    jumlah_penghasilan_rutin_setahun - biaya_jabatan_rutin_setahun
                ) - (pensiun * 12)
                pengurang = (
                    biaya_jabatan_rutin_setahun + biaya_jabatan_non_rutin_setahun
                ) + (pensiun * 12)
            netto_setahun = netto_setahun_rutin + netto_non_rutin

        if gaji > 0.0:
            ptkp = ptkp_category.get_rate(tanggal_pemotongan)
        else:
            ptkp = 0.0

        if netto_setahun > ptkp:
            pkp = float(int((netto_setahun - ptkp) / 1000) * 1000)
            pkp_rutin = float(int((netto_setahun_rutin - ptkp) / 1000) * 1000)
        else:
            pkp = 0.0
            pkp_rutin = 0.0

        obj_pph = self.env["l10n_id.pph_21_rate"]
        pph_setahun = obj_pph.find(tanggal_pemotongan).compute_tax(pkp)
        pph_setahun_rutin = obj_pph.find(tanggal_pemotongan).compute_tax(pkp_rutin)
        pph_non_rutin = pph_setahun - pph_setahun_rutin

        if is_lokal:
            pph_sebulan = pph_setahun_rutin / (13 - bulan_bergabung)
        else:
            pph_sebulan = pph_setahun_rutin / 12

        if is_keluar:
            if is_lokal:
                pph = pph_setahun
            else:
                pph = pph_setahun * ((periode_pemotongan - bulan_bergabung) / 12)
        else:
            pph = pph_sebulan + pph_non_rutin

        npwp = self.vat and len(self.vat) > 0 or False
        if not npwp:
            obj_multiplier = self.env["l10n_id.pph_21_npwp_rate_modifier"]
            pph_setahun = (
                obj_multiplier.get_rate(tanggal_pemotongan) / 100.00
            ) * pph_setahun
            pph_setahun_rutin = (
                obj_multiplier.get_rate(tanggal_pemotongan) / 100.00
            ) * pph_setahun_rutin
            pph_non_rutin = pph_setahun - pph_setahun_rutin
            pph = (obj_multiplier.get_rate(tanggal_pemotongan) / 100.00) * pph
        if not npwp:
            pph = float(int(pph))
        else:
            pph = round(pph)
        pph = float(int(pph))
        if is_keluar:
            pph = pph - akumulasi_pph_yang_disetor

        result["biaya_jabatan_rutin_setahun"] = biaya_jabatan_rutin_setahun
        result["biaya_jabatan_non_rutin_setahun"] = biaya_jabatan_non_rutin_setahun
        result["biaya_jabatan"] = biaya_jabatan
        result["biaya_jabatan_setahun"] = biaya_jabatan_setahun
        result["pengurang"] = pengurang
        result["jumlah_penghasilan_non_rutin"] = jumlah_penghasilan_non_rutin
        result["jumlah_penghasilan_rutin"] = jumlah_penghasilan_rutin
        result["jumlah_penghasilan_rutin_setahun"] = jumlah_penghasilan_rutin_setahun
        result["netto_setahun"] = netto_setahun
        result["netto_setahun_rutin"] = netto_setahun_rutin
        result["ptkp"] = ptkp
        result["pkp"] = pkp
        result["pkp_rutin"] = pkp_rutin
        result["pph_setahun"] = pph_setahun
        result["pph_setahun_rutin"] = pph_setahun_rutin
        result["pph_non_rutin"] = pph_non_rutin
        result["pph"] = pph

        return result
